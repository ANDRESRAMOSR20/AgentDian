from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import RedisChatMessageHistory
from typing import List, Union, TypedDict
import asyncio

# 📌 1️⃣ Definición del Estado de Conversación
CustomState = TypedDict("CustomState", {"messages": List[Union[HumanMessage, AIMessage]], "history": RedisChatMessageHistory})

# 📌 2️⃣ Configuración del Modelo LLM con herramientas
print("🔧 Inicializando modelo LLM...")
try:
    llm = ChatOllama(model="hf.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF:IQ4_NL")
    print("✅ Modelo LLM cargado correctamente.")
except Exception as e:
    print(f"❌ Error al inicializar el modelo LLM: {e}")

# 📌 3️⃣ Función para gestionar consultas y respuestas
def query_or_respond(state: CustomState):
    """Recupera historial antes de responder y almacena nuevas interacciones."""
    
    if "messages" not in state or not isinstance(state["messages"], list):
        return {"messages": [AIMessage(content="No hay mensajes en la conversación.")]}

    if "history" not in state:
        state["history"] = RedisChatMessageHistory(session_id="default_session")

    user_message = state["messages"][-1]
    print(f"📝 Último mensaje del usuario: {user_message.content}")

    # 🔹 Recuperar historial antes de responder
    try:
        stored_messages = asyncio.run(state["history"].aget_messages())
    except Exception as e:
        print(f"⚠️ Error al recuperar historial: {e}")
        stored_messages = []

    # 🔹 Agregar el nuevo mensaje al historial
    state["history"].add_user_message(user_message.content)

    # 🔹 Pasar historial + mensaje al modelo
    all_messages = stored_messages + [user_message]
    response = llm.invoke(all_messages)  # Ahora el modelo recibe contexto

    response_content = response.content if isinstance(response, AIMessage) else response
    state["history"].add_ai_message(response_content)

    return {"messages": [AIMessage(content=response_content)]}


# 📌 4️⃣ Función de decisión para usar herramientas o generar respuesta directa
def tools_condition(state: CustomState):
    """Determina si se debe usar la herramienta de recuperación."""
    if not state["messages"]:  # Evita IndexError si la lista está vacía
        return END
    last_message = state["messages"][-1].content.lower()
    return "tools" if any(keyword in last_message for keyword in ["buscar", "recuperar", "información"]) else END

# 📌 5️⃣ Definición del Nodo de Herramientas para Recuperación
from architecture_rag import retrieve
tools = ToolNode([retrieve])

# 📌 6️⃣ Construcción del Grafo de Conversación
workflow = StateGraph(CustomState)

# Configuración del flujo
workflow.add_node("query_or_respond", query_or_respond)
workflow.add_node("tools", tools)

workflow.set_entry_point("query_or_respond")
workflow.add_conditional_edges("query_or_respond", tools_condition, {"tools": "tools", END: END})

# 🔥 Compilación y ejecución del grafo
try:
    app = workflow.compile()
    print("✅ Grafo de conversación compilado correctamente.")
except Exception as e:
    print(f"❌ Error al compilar el grafo de conversación: {e}")

# 📌 🔎 Prueba inicial del modelo
try:
    test_message = [HumanMessage(content="Hola, ¿Cuál es el nombre del presidente de Estados Unidos?")]
    test_response = llm.invoke(test_message)
    print(f"✅ Prueba exitosa: {test_response.content}")
except Exception as e:
    print(f"❌ Error en la prueba del modelo: {e}")
