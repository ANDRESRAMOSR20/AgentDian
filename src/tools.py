# tools.py

from langchain_core.messages import SystemMessage
from .architecture_rag import retrieve
from .confg import llm
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver  # Importa MemorySaver

# Step 1: Generate an AIMessage that may include a tool-call to be sent.
def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Step 2: Execute the retrieval.
tools = ToolNode([retrieve])

# Step 3: Generate a response using the retrieved content.
def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]
    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "Usted es un asistente para tareas de respuesta a preguntas. "
        "Utilice los siguientes elementos de contexto recuperados para responder "
        "las preguntas. si no conoces la resputa, di que "
        "no la sabes. Utiliza 8000 tokens como maximo para"
        "responder detalladamente segun la fuente de informacion brindar, la informacion completamente."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages
    # Run
    response = llm.invoke(prompt)
    return {"messages": [response]}

# Crear el grafo con memoria
graph_builder = StateGraph(MessagesState)

# Agregar nodos al grafo
graph_builder.add_node("query_or_respond", query_or_respond)
graph_builder.add_node("tools", tools)
graph_builder.add_node("generate", generate)

# Configurar el punto de entrada y las conexiones
graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

# Agregar memoria al grafo
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)  # Compila el grafo con memoria