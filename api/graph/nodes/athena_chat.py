from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from api.graph.prompts import ATHENA_SYSTEM_PROMPT
from api.graph.tools import ATHENA_TOOLS
from api.graph.state import AthenaState

def athena_chat_node(state: AthenaState) -> dict:
    """Generate unbiased response for the general chat flow, supporting tools."""
    messages = state.get("messages", [])
    
    # Prepend the system prompt to the messages list
    formatted_messages = [SystemMessage(content=ATHENA_SYSTEM_PROMPT)] + messages
    
    # Initialize Gemini model
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)
    llm_with_tools = llm.bind_tools(ATHENA_TOOLS)
    
    response = llm_with_tools.invoke(formatted_messages)
    
    # Return the message to state. If tool calls exist, LangGraph will route to tools node.
    if response.tool_calls:
        return {"messages": [response]}
    else:
        return {"messages": [response], "response": response.content}
