from langchain_google_genai import ChatGoogleGenerativeAI
from api.graph.prompts import DOCUMENT_BIAS_PROMPT
from api.graph.state import AthenaState

def document_analysis_node(state: AthenaState) -> dict:
    """Analyze the uploaded document for potential bias."""
    document_context = state.get("document_context", {})
    if not document_context or not document_context.get("content"):
        return {"error": "No document content provided for analysis", "response": "No document content provided"}
        
    content = document_context.get("content")
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
        prompt = DOCUMENT_BIAS_PROMPT.format(document_text=content)
        
        response = llm.invoke([
            {"role": "user", "content": prompt}
        ])
        
        # Update state with the analysis in document_context and response
        updated_context = {**document_context, "initial_analysis": response.content}
        return {
            "response": response.content,
            "document_context": updated_context
        }
    except Exception as e:
        return {"error": str(e), "response": f"Failed to analyze document: {str(e)}"}
