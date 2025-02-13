from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Union, TypedDict
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langgraph.graph import StateGraph, END

CustomState = TypedDict("CustomState", {"messages": List[Union[HumanMessage, AIMessage]], "history": RedisChatMessageHistory})


# 📌 1️⃣ Generación de Respuesta Basada en Recuperación
def generate(state: CustomState):
    """Genera una respuesta utilizando el contexto recuperado y el historial de conversación."""

    # 🔹 Obtiene los mensajes de herramientas recientes (recuperación)
    tool_messages = [
        message for message in reversed(state["messages"])
        if isinstance(message, AIMessage) and hasattr(message, "tool_calls") and message.tool_calls
    ]

    if not tool_messages:
        docs_content = "No se encontró información relevante en la base de datos."
    else:
        docs_content = "\n\n".join(set(msg.content for msg in tool_messages if msg.content))

    # 🔹 Mensaje del sistema con el contexto recuperado
    system_message_content = (
        "Usted es un asistente para tareas de respuesta a preguntas. "
        "Utilice los siguientes elementos de contexto recuperados para responder "
        "las preguntas. si no conoces la resputa, di que "
        "no la sabes. Utiliza cinco frases como maximo para"
        "responder concisamente."
        "\n\n"
        f"{docs_content}"
    )

    # 🔹 Obtiene el historial de conversación
    historical_messages = state["history"].messages

    # 🔹 Obtiene los mensajes recientes de usuario y sistema
    conversation_messages = [
        msg for msg in state["messages"]
        if isinstance(msg, (HumanMessage, SystemMessage)) or (isinstance(msg, AIMessage) and not getattr(msg, "tool_calls", None))
    ]

    # 🔹 Construye el prompt final para el LLM
    full_prompt = (
        [SystemMessage(content=system_message_content)]
        + historical_messages  # Historial completo
        + conversation_messages  # Mensaje actual
    )

    # 🔹 Genera la respuesta con el modelo de lenguaje
    try:
        print("🤖 Generando respuesta con el modelo...")
        response = llm_with_tools.invoke(full_prompt)  # ✅ Se corrigió la variable usada en invoke()

        if not response or not hasattr(response, "content") or not response.content.strip():
            print("❌ La respuesta generada está vacía o no es válida.")
            response = AIMessage(content="Lo siento, no pude encontrar una respuesta adecuada.")

        print(f"✅ Respuesta generada: {response.content}")

    except Exception as e:
        print(f"❌ Error al generar la respuesta: {e}")
        response = AIMessage(content="Error al generar la respuesta.")

    # 🔹 Agrega la respuesta al historial evitando duplicados
    previous_messages = {msg.content for msg in state["history"].messages}

    if response.content in previous_messages:
        print("⚠️ Respuesta duplicada detectada, no se almacena.")
    else:
        state["history"].add_ai_message(response.content)
        print("✅ Respuesta guardada en historial de Redis.")

    return {"messages": [response]}


# 📌 2️⃣ Configuración del Grafo de Ejecución
from confg import query_or_respond, tools, tools_condition

graph_builder = StateGraph(CustomState)
graph_builder.add_node("query_or_respond", query_or_respond)  # Decide si recuperar o responder
graph_builder.add_node("tools", tools)  # Ejecuta la recuperación si es necesario
graph_builder.add_node("generate", generate)  # Genera la respuesta final

# 🔹 Punto de Entrada del Grafo
graph_builder.set_entry_point("query_or_respond")

# 🔹 Definición de Condiciones para Decidir si Buscar Información
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"},  # Si se requiere, pasa por la herramienta de recuperación
)

# 🔹 Flujo del Grafo: De `tools` a `generate` y luego Finaliza
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

# 📌 3️⃣ Compilación y Ejecución del Grafo con Mejoras
graph = graph_builder.compile()

# 📌 4️⃣ Ejecución con una Consulta de Prueba
input_message = "¿Me gustaría saber qué ha sucedido con los presidentes que han servido?"

# Inicializar la historia de chat con Redis
message_history = RedisChatMessageHistory(session_id="test_session")

# Estado inicial con mensajes y historial
initial_state = {
    "messages": [HumanMessage(content=input_message)],
    "history": message_history
}

# 🚀 Iniciando ejecución del grafo con mejoras...
print("\n🚀 Iniciando ejecución del grafo...")

# ✅ Limpiar historial antes de procesar la nueva consulta
print("🗑️ Limpiando historial en Redis...")
message_history.clear()

for step in graph.stream(
    initial_state,
    stream_mode="values",
):
    if step["messages"]:
        last_message = step["messages"][-1]
    else:
        print("⚠️ No hay mensajes en este paso del grafo. Se genera un mensaje predeterminado.")
        last_message = AIMessage(content="No se pudo generar una respuesta en este paso.")

    # ✅ Verificar si la respuesta es válida antes de guardarla
    if not last_message or not last_message.content.strip():
        print("❌ Respuesta vacía o inválida. Generando respuesta alternativa.")
        last_message = AIMessage(content="Lo siento, no encontré información relevante.")

    # 📌 Evitar respuestas duplicadas o que repitan el mensaje del usuario
    try:
        previous_messages = {msg.content for msg in message_history.messages}
    except AttributeError:
        print("⚠️ No se pudo obtener el historial de Redis, se usará un historial vacío.")
        previous_messages = set()    
        
    if last_message.content in previous_messages or last_message.content == input_message:
        print("⚠️ Respuesta duplicada o repetición del mensaje del usuario, no se almacena.")
    else:
        message_history.add_ai_message(last_message.content)
        print("✅ Respuesta guardada en historial de Redis.")
    
    # 📌 Mostrar la respuesta generada
    last_message.pretty_print()

# 📌 5️⃣ Visualización del Historial de Mensajes Limpio
print("\n🔍 Historial de Conversación:")
for message in message_history.messages:
    print(f"{message.type}: {message.content}")
