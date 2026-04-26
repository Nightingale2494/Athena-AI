print("MAIN FILE STARTED 🚀")
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime, timezone
from google.cloud import firestore as firestore_module
import csv
import io
import os
import zipfile
import xml.etree.ElementTree as ET

def _is_readable_text(text: str) -> bool:
    """Heuristic check to avoid running analysis on mostly-binary/garbled content."""
    if not text:
        return False

    stripped = text.strip()
    if len(stripped) < 120:
        return False

    printable_chars = sum(1 for c in stripped if c.isprintable())
    printable_ratio = printable_chars / max(len(stripped), 1)

    alpha_chars = sum(1 for c in stripped if c.isalpha())
    alpha_ratio = alpha_chars / max(len(stripped), 1)

    word_count = len([w for w in stripped.split() if any(ch.isalpha() for ch in w)])
    return printable_ratio > 0.85 and alpha_ratio > 0.35 and word_count >= 20

def _extract_csv_text(file_content: bytes) -> str:
    decoded = file_content.decode("utf-8", errors="ignore")
    if not decoded.strip():
        decoded = file_content.decode("latin-1", errors="ignore")
    if not decoded.strip():
        return ""

    reader = csv.reader(io.StringIO(decoded))
    lines = []
    for row in reader:
        cleaned = [str(cell).strip() for cell in row if str(cell).strip()]
        if cleaned:
            lines.append(" | ".join(cleaned))
    return "\n".join(lines)

def _extract_xlsx_text(file_content: bytes) -> str:
    """Lightweight XLSX text extraction without third-party dependencies."""
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    shared_strings = []

    with zipfile.ZipFile(io.BytesIO(file_content)) as zf:
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall("s:si", ns):
                parts = [node.text or "" for node in si.findall(".//s:t", ns)]
                shared_strings.append("".join(parts))

        sheet_files = sorted(
            [name for name in zf.namelist() if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")]
        )

        lines = []
        for sheet_file in sheet_files:
            sheet_root = ET.fromstring(zf.read(sheet_file))
            sheet_name = os.path.basename(sheet_file).replace(".xml", "")
            lines.append(f"[{sheet_name}]")

            for row in sheet_root.findall(".//s:row", ns):
                row_values = []
                for cell in row.findall("s:c", ns):
                    cell_type = cell.attrib.get("t")
                    value_node = cell.find("s:v", ns)
                    if value_node is None or value_node.text is None:
                        continue

                    value = value_node.text
                    if cell_type == "s":
                        try:
                            value = shared_strings[int(value)]
                        except Exception:
                            pass
                    if str(value).strip():
                        row_values.append(str(value).strip())
                if row_values:
                    lines.append(" | ".join(row_values))

        return "\n".join(lines)

def _extract_text_for_analysis(file_content: bytes, filename: str, content_type: str = "") -> str:
    ext = os.path.splitext((filename or "").lower())[1]
    content_type = (content_type or "").lower()

    if ext in [".csv", ".tsv"] or "csv" in content_type:
        try:
            return _extract_csv_text(file_content)
        except Exception:
            return ""

    if ext == ".xlsx" or "spreadsheetml" in content_type:
        try:
            return _extract_xlsx_text(file_content)
        except Exception:
            return ""

    # Generic plain-text fallback
    text_content = file_content.decode("utf-8", errors="ignore").strip()
    if not text_content:
        text_content = file_content.decode("latin-1", errors="ignore").strip()
    return text_content

app = FastAPI(title="Athena API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later we can lock this down
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from _firebase import db
    from _auth import verify_token
    from _gemini import get_athena_response, analyze_document_for_bias, get_document_chat_response
    print("IMPORTS SUCCESS ✅")
except Exception as e:
    print("IMPORT ERROR 💀:", e)

@app.get("/")
def root():
    return {"status": "Athena backend alive 🚀"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "athena"}

@app.post("/api/chat")
async def chat(request: Request, authorization: str = Header(None)):
    user = verify_token(authorization)
    user_id = user["uid"]
    data = await request.json()

    message = data.get("message")
    conversation_id = data.get("conversation_id") or str(uuid.uuid4())

    conversation_ref = db.collection("conversations").document(conversation_id)
    conversation_doc = conversation_ref.get()

    conversation_history = []
    if conversation_doc.exists:
        messages_ref = conversation_ref.collection("messages").select(["role", "content"]).order_by("timestamp").limit(10)
        conversation_history = [{"role": m.to_dict()["role"], "content": m.to_dict()["content"]} for m in messages_ref.stream()]
    else:
        conversation_ref.set({
            "user_id": user_id,
            "title": message[:50] + "..." if len(message) > 50 else message,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "message_count": 0,
        })

    athena_result = get_athena_response(message, conversation_history)

    user_message_id = str(uuid.uuid4())
    conversation_ref.collection("messages").document(user_message_id).set({
        "role": "user",
        "content": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    athena_message_id = str(uuid.uuid4())
    conversation_ref.collection("messages").document(athena_message_id).set({
        "role": "assistant",
        "content": athena_result["response"],
        "bias_analysis": athena_result["bias_analysis"],
        "timestamp": athena_result["timestamp"],
    })

    conversation_ref.update({
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "message_count": firestore_module.Increment(2),
    })

    return {
        "response": athena_result["response"],
        "bias_analysis": athena_result["bias_analysis"],
        "conversation_id": conversation_id,
        "message_id": athena_message_id,
    }

@app.get("/api/conversations")
def get_conversations(authorization: str = Header(None)):
    user = verify_token(authorization)
    user_id = user["uid"]

    conversations_ref = db.collection("conversations").where("user_id", "==", user_id).limit(50).stream()

    result = []
    for conv in conversations_ref:
        conv_data = conv.to_dict()
        message_count = conv_data.get("message_count", 0)
        if message_count == 0:
            message_count = db.collection("conversations").document(conv.id).collection("messages").count().get()[0][0].value
        result.append({
            "id": conv.id,
            "title": conv_data.get("title", "Untitled"),
            "created_at": conv_data.get("created_at", ""),
            "updated_at": conv_data.get("updated_at", ""),
            "message_count": message_count,
        })

    result.sort(key=lambda x: x["updated_at"], reverse=True)
    return result

@app.get("/api/conversations/{conversation_id}/messages")
def get_messages(conversation_id: str, authorization: str = Header(None)):
    user = verify_token(authorization)
    user_id = user["uid"]

    conversation_ref = db.collection("conversations").document(conversation_id)
    conversation_doc = conversation_ref.get()

    if not conversation_doc.exists:
        return JSONResponse(status_code=404, content={"error": "Conversation not found"})

    if conversation_doc.to_dict().get("user_id") != user_id:
        return JSONResponse(status_code=403, content={"error": "Access denied"})

    messages_ref = conversation_ref.collection("messages").order_by("timestamp")
    result = []
    for msg in messages_ref.stream():
        msg_data = msg.to_dict()
        result.append({
            "id": msg.id,
            "role": msg_data.get("role", "user"),
            "content": msg_data.get("content", ""),
            "bias_analysis": msg_data.get("bias_analysis"),
            "timestamp": msg_data.get("timestamp", ""),
        })

    return result

@app.get("/api/documents")
def get_documents(authorization: str = Header(None)):
    user = verify_token(authorization)
    user_id = user["uid"]

    docs_ref = db.collection("document_analyses").where("user_id", "==", user_id).limit(20).stream()

    result = []
    for doc in docs_ref:
        doc_data = doc.to_dict()
        result.append({
            "id": doc.id,
            "filename": doc_data.get("filename", ""),
            "analysis": doc_data.get("analysis", ""),
            "created_at": doc_data.get("created_at", ""),
        })

    result.sort(key=lambda x: x["created_at"], reverse=True)
    return result

@app.post("/api/upload")
@app.post("/api/upload/analyze")
async def upload_document(file: UploadFile = File(...), authorization: str = Header(None)):
    user = verify_token(authorization)
    user_id = user["uid"]

    file_content = await file.read()
    text_content = _extract_text_for_analysis(file_content, file.filename, file.content_type)
    if not _is_readable_text(text_content):
        return JSONResponse(
            status_code=400,
            content={
                "error": "I couldn't extract readable text from this file. Spreadsheets are supported for .csv, .tsv, and .xlsx files. For other formats, upload a text-readable file and try again."
            }
        )

    analysis_result = analyze_document_for_bias(text_content)

    doc_id = str(uuid.uuid4())
    db.collection("document_analyses").document(doc_id).set({
        "user_id": user_id,
        "filename": file.filename,
        "analysis": analysis_result["analysis"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    return {
        "id": doc_id,
        "filename": file.filename,
        "analysis": analysis_result["analysis"],
        "document_text": text_content[:12000],
        "timestamp": analysis_result["timestamp"],
    }

@app.post("/api/upload/chat")
async def chat_about_document(request: Request, authorization: str = Header(None)):
    verify_token(authorization)
    data = await request.json()

    filename = data.get("filename", "Uploaded document")
    document_text = (data.get("document_text") or "").strip()
    analysis = data.get("analysis") or ""
    message = (data.get("message") or "").strip()
    history = data.get("history") or []

    if not document_text:
        return JSONResponse(status_code=400, content={"error": "No document text context found. Re-upload the file and try again."})
    if not message:
        return JSONResponse(status_code=400, content={"error": "Message is required."})

    result = get_document_chat_response(
        filename=filename,
        document_text=document_text,
        initial_analysis=analysis,
        user_message=message,
        chat_history=history,
    )

    return {
        "response": result["response"],
        "timestamp": result["timestamp"],
    }
