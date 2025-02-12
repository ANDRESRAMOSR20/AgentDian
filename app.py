import streamlit as st
from architecture_rag import graph
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="Asistente Virtual", layout="wide")
st.title("📄 Asistente Virtual basado para la DIAN")
st.markdown("Este asistente responde preguntas basadas en el contenido de los documentos PDF cargados.")


query = st.text_input("Escribe tu pregunta aquí:", "")


if st.button("Consultar"):
    if query.strip():
        # Crear el mensaje de usuario
        input_message = [{"role": "user", "content": query}]

        # Ejecutar el flujo en el grafo
        with st.spinner("Buscando respuesta..."):
            response = None
            for step in graph.stream({"messages": input_message}, stream_mode="values"):
                response = step["messages"][-1].content  # Obtener la última respuesta
            
            st.subheader("🔍 Respuesta:")
            st.write(response if response else "No encontré información relevante en los PDFs.")

    else:
        st.warning("⚠️ Por favor, ingresa una pregunta antes de consultar.")
