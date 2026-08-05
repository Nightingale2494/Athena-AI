import sys
import os
import logging
from datetime import datetime, timezone

# Add current directory to path for safety
sys.path.insert(0, os.path.dirname(__file__))

try:
    from services import AthenaService
except ImportError:
    from api.services import AthenaService

logger = logging.getLogger(__name__)

def get_athena_response(
    user_message: str, 
    conversation_history: list = None, 
    conversation_id: str = "legacy_compat", 
    user_id: str = "anonymous"
) -> dict:
    """Get a response from Athena via the LangGraph workflow."""
    try:
        history = conversation_history or []
        return AthenaService.run_chat(
            user_message=user_message,
            history=history,
            conversation_id=conversation_id,
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Gemini LangGraph chat error: {str(e)}")
        return {
            'response': "I apologize, but I'm experiencing technical difficulties with the graph workflow. Please try again.",
            'bias_analysis': 'error',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

def analyze_document_for_bias(document_text: str, filename: str = "document_upload.txt", user_id: str = "anonymous") -> dict:
    """Analyze a document for potential biases using the LangGraph workflow."""
    try:
        return AthenaService.run_document_analysis(
            document_text=document_text,
            filename=filename,
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Document LangGraph analysis error: {str(e)}")
        return {
            'analysis': f"Error analyzing document: {str(e)}",
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

def get_document_chat_response(
    filename: str,
    document_text: str,
    initial_analysis: str,
    user_message: str,
    chat_history: list = None,
    user_id: str = "anonymous"
) -> dict:
    """Chat about a previously analyzed document using the LangGraph workflow."""
    try:
        history = chat_history or []
        return AthenaService.run_document_chat(
            filename=filename,
            document_text=document_text,
            initial_analysis=initial_analysis,
            user_message=user_message,
            history=history,
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Document LangGraph chat error: {str(e)}")
        return {
            'response': "I hit a technical issue while analyzing this document chat. Please try again.",
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
