import streamlit as st
from google import genai

# Configurar la página
st.set_page_config(page_title="Chat con Gemini", page_icon="🤖")

# Título de la app
st.title("🤖 Chat con Gemini AI")

# Configurar Gemini
@st.cache_resource
def configure_gemini():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        
        # Listar modelos disponibles para debugging
        try:
            models = client.models.list()
            available_models = [m.name for m in models]
            st.session_state.available_models = available_models
        except:
            st.session_state.available_models = []
        
        return client
    except KeyError:
        st.error("⚠️ No se encontró GEMINI_API_KEY en secrets.toml")
        st.info("Crea el archivo .streamlit/secrets.toml con tu API key")
        st.stop()
    except Exception as e:
        st.error(f"Error al configurar Gemini: {str(e)}")
        st.stop()

client = configure_gemini()

# Inicializar el historial de chat en session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input del usuario
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Obtener respuesta de Gemini
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                # Usar el modelo seleccionado
                selected_model = st.session_state.get('model', 'models/gemini-2.5-flash')
                
                response = client.models.generate_content(
                    model=selected_model,
                    contents=prompt
                )
                response_text = response.text
                st.markdown(response_text)
                
                # Agregar respuesta al historial
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
            except Exception as e:
                st.error(f"❌ Error con modelo '{selected_model}': {str(e)}")
                st.info("💡 Intenta seleccionar otro modelo del sidebar")

# Botón para limpiar el chat
if st.sidebar.button("🗑️ Limpiar conversación"):
    st.session_state.messages = []
    st.rerun()

# Información en el sidebar
with st.sidebar:
    st.markdown("### Acerca de")
    st.markdown("Esta app usa **Gemini 2.0 Flash** de Google para generar respuestas.")
    st.markdown("---")
    st.markdown(f"💬 Mensajes en la conversación: {len(st.session_state.messages)}")
    
    # Selector de modelo
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    
    # Mostrar modelos disponibles si los hay
    if 'available_models' in st.session_state and st.session_state.available_models:
        st.markdown("**Modelos disponibles:**")
        for model in st.session_state.available_models[:7]:
            st.text(model)
    
    # Usar los modelos que realmente están disponibles
    model_options = {
        "Gemini 2.5 Flash (Recomendado)": "models/gemini-2.5-flash",
        "Gemini 2.5 Flash Lite": "models/gemini-2.5-flash-lite-preview-06-17",
        "Gemini 2.5 Pro": "models/gemini-2.5-pro-preview-03-25",
        "Gemini 2.5 Flash (Mayo)": "models/gemini-2.5-flash-preview-05-20"
    }
    
    selected_display = st.selectbox(
        "Modelo",
        list(model_options.keys()),
        key="model_display",
        help="Gemini 2.5 Flash es el modelo más rápido y eficiente"
    )
    
    # Guardar el nombre real del modelo
    if 'model' not in st.session_state or st.session_state.get('last_display') != selected_display:
        st.session_state.model = model_options[selected_display]
        st.session_state.last_display = selected_display