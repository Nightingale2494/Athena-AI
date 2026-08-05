from langchain_google_genai import ChatGoogleGenerativeAI
from api.graph.prompts import DOCUMENT_CHAT_PROMPT, ATHENA_SYSTEM_PROMPT
from api.graph.state import AthenaState

def document_chat_node(state: AthenaState) -> dict:
    """Chat about a document, grounded in the document context."""
    document_context = state.get("document_context", {})
    if not document_context or not document_context.get("content"):
        return {"error": "No document content found for chat context", "response": "No document context"}
        
    messages = state.get("messages", [])
    if not messages:
        return {"error": "No user message provided", "response": "No user message"}
        
    user_message = messages[-1].content
    
    # Format chat history (excluding the last user message)
    history_lines = []
    for msg in messages[:-1]:
        role = "User" if msg.type == "human" else "Athena"
        history_lines.append(f"{role}: {msg.content}")
    history_block = "\n".join(history_lines) if history_lines else "No previous chat yet."
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)
        prompt = DOCUMENT_CHAT_PROMPT.format(
            filename=document_context.get("filename", "document"),
            initial_analysis=document_context.get("initial_analysis", "No initial analysis"),
            document_text=document_context.get("content"),
            history_block=history_block,
            user_message=user_message
        )
        
        response = llm.invoke([
            {"role": "system", "content": ATHENA_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ])
        
        return {"messages": [response], "response": response.content}
    except Exception as e:
        return {"error": str(e), "response": f"Failed to chat about document: {str(e)}"}
