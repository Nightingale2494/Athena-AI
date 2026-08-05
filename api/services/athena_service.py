from datetime import datetime, timezone
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from api.graph import athena_graph

class AthenaService:
    @staticmethod
    def _convert_history_to_messages(history: List[Dict[str, str]]) -> list:
        messages = []
        if not history:
            return messages
        for msg in history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role in ["assistant", "model"]:
                messages.append(AIMessage(content=content))
        return messages

    @classmethod
    def run_chat(cls, user_message: str, history: List[Dict[str, str]], conversation_id: str, user_id: str = "anonymous") -> Dict[str, Any]:
        # Convert history
        messages = cls._convert_history_to_messages(history)
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        # Prepare state
        initial_state = {
            "messages": messages,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "mode": "chat",
            "bias_analysis": "neutral",
            "document_context": None,
            "response": "",
            "error": None
        }
        
        # Run graph
        final_state = athena_graph.invoke(initial_state)
        
        if final_state.get("error"):
            return {
                'response': final_state.get("response") or "I encountered an error while processing your request.",
                'bias_analysis': 'error',
                'error': final_state.get("error"),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        return {
            'response': final_state.get("response", ""),
            'bias_analysis': final_state.get("bias_analysis", "neutral"),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    @classmethod
    def run_document_analysis(cls, document_text: str, filename: str, user_id: str = "anonymous") -> Dict[str, Any]:
        # Prepare state
        initial_state = {
            "messages": [],
            "user_id": user_id,
            "conversation_id": "",
            "mode": "analyze",
            "bias_analysis": "neutral",
            "document_context": {
                "filename": filename,
                "content": document_text,
                "initial_analysis": ""
            },
            "response": "",
            "error": None
        }
        
        # Run graph
        final_state = athena_graph.invoke(initial_state)
        
        if final_state.get("error"):
            return {
                'analysis': f"Error analyzing document: {final_state.get('error')}",
                'error': final_state.get("error"),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        return {
            'analysis': final_state.get("response", ""),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    @classmethod
    def run_document_chat(
        cls,
        filename: str,
        document_text: str,
        initial_analysis: str,
        user_message: str,
        history: List[Dict[str, str]],
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        # Convert history
        messages = cls._convert_history_to_messages(history)
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        # Prepare state
        initial_state = {
            "messages": messages,
            "user_id": user_id,
            "conversation_id": "",
            "mode": "document_chat",
            "bias_analysis": "neutral",
            "document_context": {
                "filename": filename,
                "content": document_text,
                "initial_analysis": initial_analysis
            },
            "response": "",
            "error": None
        }
        
        # Run graph
        final_state = athena_graph.invoke(initial_state)
        
        if final_state.get("error"):
            return {
                'response': "I hit a technical issue while analyzing this document chat. Please try again.",
                'error': final_state.get("error"),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        return {
            'response': final_state.get("response", ""),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
