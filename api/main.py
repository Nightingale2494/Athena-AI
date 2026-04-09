print("MAIN FILE STARTED 🚀")
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime, timezone
from google.cloud import firestore as firestore_module

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
    from _gemini import get_athena_response, analyze_document_for_bias
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

@app.get("/api/messages/{conversation_id}")
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
async def upload_document(file: UploadFile = File(...), authorization: str = Header(None)):
    user = verify_token(authorization)
    user_id = user["uid"]

    if not file.filename.endswith(".txt"):
        return JSONResponse(status_code=400, content={"error": "Only .txt files supported"})

    file_content = await file.read()
    try:
        text_content = file_content.decode("utf-8")
    except Exception:
        text_content = file_content.decode("latin-1")

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
        "timestamp": analysis_result["timestamp"],
    }
