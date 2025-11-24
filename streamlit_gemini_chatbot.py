import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage

# Configuración inicial
st.set_page_config(page_title="Chatbot Básico", page_icon="🤖", layout="wide")
st.title("🤖 Chatbot - paso 2 - con LangChain")
st.markdown("Este es un *chatbot de ejemplo* construido con LangChain + Streamlit.")

# Inicializar session_state variables
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-2.5-flash"
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Layout: main chat area (left) and controls (right)
left_col, right_col = st.columns([10, 2])

# Controls in the right column (acts like a right sidebar)
with right_col:
    # Use a form so changes are applied only when the user clicks 'Aplicar'.
    with st.form("config_form"):
        st.write("⚙️ Configuración")
        models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        selected = st.selectbox(
            "Modelo",
            models,
            index=models.index(st.session_state.selected_model)
        )

        temp = st.slider(
            "Temp",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.temperature,
            step=0.1
        )
        st.caption("0 = determinístico · 2 = creativo")

        apply_btn = st.form_submit_button("Aplicar")

    # Apply the form values when submitted
    if apply_btn:
        st.session_state.selected_model = selected
        st.session_state.temperature = temp
        st.experimental_rerun()

    # Keep a separate clear button for immediate clearing
    if st.button("🗑️ Limpiar", use_container_width=True):
        st.session_state.mensajes = []
        st.experimental_rerun()

# Initialize chat model with current settings
chat_model = ChatGoogleGenerativeAI(
    model=st.session_state.selected_model,
    temperature=st.session_state.temperature
)

# Renderizar historial existente y el input dentro de la columna izquierda
with left_col:
    for msg in st.session_state.mensajes:
        role = "assistant" if isinstance(msg, AIMessage) else "user"
        with st.chat_message(role):
            st.markdown(msg.content)

    # Input de usuario
    pregunta = st.chat_input("Escribe tu mensaje:")

    if pregunta:
        # Mostrar y almacenar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(pregunta)

        st.session_state.mensajes.append(HumanMessage(content=pregunta))

        respuesta = chat_model.invoke(st.session_state.mensajes)

        with st.chat_message("assistant"):
            st.markdown(respuesta.content)

        st.session_state.mensajes.append(respuesta)