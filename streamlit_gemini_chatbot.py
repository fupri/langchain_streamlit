import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage

# Configuración inicial
st.set_page_config(page_title="Chatbot Básico", page_icon="🛸", layout="wide")
st.title("Bienvenido al chatbot configurable con tecnología Gemini")
st.markdown("Construido con LangChain + Streamlit.")

# Inicializar session_state variables
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-2.5-flash"
if "answer_length" not in st.session_state:
    st.session_state.answer_length = "medium"
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Layout: area principal del chat (izquierda) y controles (derecha)
left_col, right_col = st.columns([10, 2])

# Controles en la columna derecha (actúa como una barra lateral derecha)
with right_col:
    # Usa un formulario para que los cambios se apliquen solo cuando el usuario haga clic en 'Aplicar'.
    with st.form("config_form"):
        st.write("Configuración")
        models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        selected = st.selectbox(
            "Modelo",
            models,
            index=models.index(st.session_state.selected_model)
        )

        temp = st.slider(
            "Temperatura",
            min_value=0.0,
            max_value=2.0,
            value=st.session_state.temperature,
            step=0.1
        )
        st.caption("0 = determinístico · 2 = creativo")

        length_options = {"Corta (Breve y conciso)": "short", 
                          "Media (Explicación clara)": "medium", 
                          "Larga (Respuesta muy detallada)": "long"}
        selected_length = st.selectbox(
            "Longitud",
            list(length_options.keys()),
            index=list(length_options.values()).index(st.session_state.answer_length)
        )
        answer_length = length_options[selected_length]

        apply_btn = st.form_submit_button("Aplicar")

    # Aplicar cambios de configuración al hacer clic en 'Aplicar'
    if apply_btn:
        st.session_state.selected_model = selected
        st.session_state.temperature = temp
        st.session_state.answer_length = answer_length
        st.rerun()

    # Mantener un botón separado para limpiar inmediatamente
    if st.button("Vaciar chat", use_container_width=True):
        st.session_state.mensajes = []
        st.rerun()

# Inicializar el modelo del chat con la configuracion actual
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

# Input de usuario SIEMPRE fuera del bloque de columnas para que quede abajo
pregunta = st.chat_input("¿En qué estás pensando?")

if pregunta:
    # Mostrar y almacenar mensaje del usuario
    with left_col:
        with st.chat_message("user"):
            st.markdown(pregunta)

    st.session_state.mensajes.append(HumanMessage(content=pregunta))

    # Construye mensajes con instrucciones de longitud
    length_instructions = {
        "short": "Proporciona respuestas muy breves y concisas, en máximo 2-3 oraciones.",
        "medium": "Proporciona respuestas moderadas con explicaciones claras, alrededor de un párrafo.",
        "long": "Proporciona respuestas detalladas y completas con ejemplos cuando sea relevante."
    }
    messages_with_context = [
        HumanMessage(content=length_instructions.get(st.session_state.answer_length, "medium"))
    ] + st.session_state.mensajes

    respuesta = chat_model.invoke(messages_with_context)

    with left_col:
        with st.chat_message("assistant"):
            st.markdown(respuesta.content)

    st.session_state.mensajes.append(respuesta)