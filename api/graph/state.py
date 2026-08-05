from typing import List, Dict, Any, Optional, TypedDict
from langchain_core.messages import BaseMessage

class DocumentContext(TypedDict, total=False):
    filename: str
    content: str
    initial_analysis: str

class AthenaState(TypedDict):
    messages: List[BaseMessage]
    user_id: str
    conversation_id: str
    bias_analysis: str  # "neutral", "bias_aware", "error"
    document_context: Optional[DocumentContext]
    response: str
    error: Optional[str]
    mode: str  # "chat", "analyze", "document_chat"
