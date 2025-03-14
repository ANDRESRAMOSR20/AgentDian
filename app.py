import streamlit as st
from src.tools import graph  # Importa el grafo con memoria
import uuid  # Para generar IDs únicos
from src.view import view_up_document, search_documents

# Configuración inicial de la página
st.set_page_config(page_title="Asistente Virtual", layout="wide", page_icon="🤖")
st.title("📄 Asistente Virtual basado para la DIAN")
st.markdown(
    "Este asistente responde preguntas basadas en el contenido de los documentos PDF cargados."
)

# Entrada del usuario para buscar por categoría
st.sidebar.header("Buscar y cargar documentos")


if st.sidebar.button("Cargar nuevos documentos"):
    view_up_document()

if st.sidebar.button("Buscar Documentos"):
    search_documents()


# Genera un thread_id único para la sesión actual
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())  # Genera un ID único


# Inicializa el historial de mensajes si no existe
if "message_history" not in st.session_state:
    st.session_state.message_history = []

# Mostrar el historial de mensajes en la parte principal
for msg in st.session_state.message_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Entrada de texto en la parte inferior
query = st.chat_input(placeholder="Escribe tu pregunta aquí...")

if query:
    # Agrega el mensaje del usuario al historial
    st.session_state.message_history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    # Ejecutar el flujo en el grafo
    with st.spinner("Buscando respuesta..."):
        response = None
        for step in graph.stream(
            {"messages": st.session_state.message_history},
            config={
                "configurable": {"thread_id": st.session_state.thread_id}
            },  # Proporciona el thread_id
            stream_mode="values",
        ):
            response = step["messages"][-1].content  # Obtener la última respuesta

        # Agrega la respuesta del modelo al historial
        st.session_state.message_history.append(
            {"role": "assistant", "content": response}
        )

        # Muestra la respuesta del asistente
        with st.chat_message("assistant"):
            st.write(response)
