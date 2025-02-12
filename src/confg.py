from langchain_ollama import ChatOllama

# Language Model Configuration
llm = ChatOllama(model="hf.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF:IQ4_NL")

# Generate a message to join a call tool
def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    user_message = state["messages"][-1]
    message_history.add_user_message(user_message.content)

    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])

    message_history.add_ai_message(response.content)

    print("\n🔍 Historial de Mensajes (Después de query_or_respond):")
    for msg in message_history.messages:
        print(f"{msg.type}: {msg.content}")


    return {"messages": [response]}

def tools_condition(state: MessagesState):
    """Determina si se debe llamar a la herramienta de recuperación."""
    last_message = state["messages"][-1].content.lower()
    return "tools" if any(keyword in last_message for keyword in ["buscar", "recuperar", "información"]) else END

# Execute the recuperation
from langgraph.prebuilt import ToolNode
tools = ToolNode([retrieve])