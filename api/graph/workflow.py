from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from api.graph.state import AthenaState
from api.graph.tools import ATHENA_TOOLS
from api.graph.nodes.bias_detection import detect_bias_node
from api.graph.nodes.athena_chat import athena_chat_node
from api.graph.nodes.document_analysis import document_analysis_node
from api.graph.nodes.document_chat import document_chat_node

# Define the graph workflow
workflow = StateGraph(AthenaState)

# Add all nodes
workflow.add_node("bias_detection", detect_bias_node)
workflow.add_node("athena_chat", athena_chat_node)
workflow.add_node("document_analysis", document_analysis_node)
workflow.add_node("document_chat", document_chat_node)
workflow.add_node("tools", ToolNode(ATHENA_TOOLS))

# Define state-based conditional routing entrypoint
def route_mode(state: AthenaState) -> str:
    mode = state.get("mode")
    if mode == "analyze":
        return "document_analysis"
    elif mode == "document_chat":
        return "document_chat"
    else:
        return "bias_detection"

workflow.add_conditional_edges(START, route_mode)

# Linear edge from bias detection to chat generation
workflow.add_edge("bias_detection", "athena_chat")

# ReAct loop conditional edges for tool calling
workflow.add_conditional_edges("athena_chat", tools_condition)
workflow.add_edge("tools", "athena_chat")

# Terminal paths
workflow.add_edge("document_analysis", END)
workflow.add_edge("document_chat", END)

# Compile the graph
athena_graph = workflow.compile()
