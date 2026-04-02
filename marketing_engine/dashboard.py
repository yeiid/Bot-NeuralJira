import streamlit as st
import os
import json
from PIL import Image
from orchestrator import MarketingOrchestrator
from core.news_fetcher import NewsFetcher
from core.content_ai import ContentAI
from gen_infographic import generate as generate_image
from core.facebook_api import FacebookAPI

# Configuración de Página
st.set_page_config(
    page_title="NeuralJira - Marketing Engine",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo Personalizado (Cyberpunk Dark)
st.markdown("""
    <style>
    .main {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    .stButton>button {
        background-color: #8B5CF6;
        color: white;
        border-radius: 8px;
        border: none;
        box-shadow: 0 0 15px #8B5CF688;
    }
    .stButton>button:hover {
        background-color: #7C3AED;
        box-shadow: 0 0 25px #8B5CF6AA;
    }
    h1, h2, h3 {
        color: #22D3EE !important;
    }
    .status-box {
        padding: 15px;
        border-radius: 10px;
        background-color: #1E293B;
        border: 1px solid #8B5CF6;
    }
    </style>
    """, unsafe_allow_value=True)

# Inicialización de componentes (Caching)
@st.cache_resource
def get_orchestrator():
    return MarketingOrchestrator()

orchestrator = get_orchestrator()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://via.placeholder.com/150/8B5CF6/FFFFFF?text=NeuralJira", width=150)
    st.title("NeuralJira Bot")
    st.markdown("### Configuración")
    
    api_key_status = "✅ API Key OK" if os.getenv("ANTHROPIC_API_KEY") else "❌ Falta ANTHROPIC_API_KEY"
    st.info(api_key_status)
    
    selected_mode = st.radio("Modo", ["🤖 Noticias Automáticas", "🛠️ Generar Manual", "📅 Programación"])
    
    if st.button("🔄 Validar Facebook"):
        success, msg = orchestrator.facebook_api.validate_connection()
        if success: st.success(msg)
        else: st.error(msg)

# --- MAIN CONTENT ---
st.title("🚀 NeuralJira Content Engine")
st.write("Gestiona la presencia digital de NeuralJira con IA.")

if selected_mode == "🤖 Noticias Automáticas":
    st.header("📰 Central de Noticias Tech")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Fuentes Disponibles")
        source = st.selectbox("Selecciona fuente:", list(NewsFetcher.FEEDS.keys()))
        if st.button("🔍 Ver Últimas Noticias"):
            news_items = orchestrator.news_fetcher.fetch_latest(source)
            st.session_state.news_items = news_items

    with col2:
        if "news_items" in st.session_state:
            st.subheader(f"Últimas de {source}")
            for i, item in enumerate(st.session_state.news_items[:5]):
                with st.expander(f"{item['title']}"):
                    st.write(item['summary'])
                    if st.button(f"Procesar con IA - News {i}"):
                        st.session_state.selected_news = item
                        st.session_state.step = "writing"
        else:
            st.write("Haz clic en 'Ver Últimas Noticias' para empezar.")

    # --- PASO 2: REDACCIÓN ---
    if "selected_news" in st.session_state:
        st.divider()
        st.header("🧠 Inteligencia Artificial - Galldroko Redacción")
        
        col_w1, col_w2 = st.columns(2)
        
        with col_w1:
            st.subheader("Entrada")
            st.info(f"Procesando: {st.session_state.selected_news['title']}")
            
            if st.button("📝 Generar Redacción Sugerida"):
                with st.spinner("Claude redactando..."):
                    content = orchestrator.content_ai.generate_post_content(
                        st.session_state.selected_news['title'], 
                        template_type="news"
                    )
                    st.session_state.generated_content = content

        with col_w2:
            if "generated_content" in st.session_state:
                st.subheader("Resultado Sugerido")
                headline = st.text_input("Titular", st.session_state.generated_content.get('headline', ''))
                body = st.text_area("Cuerpo", st.session_state.generated_content.get('body', ''), height=150)
                
                if st.button("🎨 Diseñar Infografía"):
                    st.session_state.final_data = {
                        "headline": headline,
                        "body": body,
                        "source": st.session_state.generated_content.get('source', 'NeuralJira')
                    }
                    with st.spinner("Renderizando imagen..."):
                        img_path = generate_image("news", st.session_state.final_data)
                        st.session_state.generated_img = img_path
                        st.success(f"Imagen generada!")

    # --- PASO 3: PREVIEW & PUBLISH ---
    if "generated_img" in st.session_state:
        st.divider()
        st.header("🖼️ Vista Previa & Publicación")
        
        c1, c2 = st.columns([2, 1])
        
        with c1:
            img = Image.open(st.session_state.generated_img)
            st.image(img, use_column_width=True)
        
        with c2:
            st.subheader("Acciones")
            fb_msg = f"🚀 {st.session_state.final_data['headline']}\n\n{st.session_state.final_data['body']}\n\n#NeuralJira #Tech #AI"
            st.text_area("Copia del Post", fb_msg, height=200)
            
            if st.button("📤 PUBLICAR AHORA EN FACEBOOK"):
                with st.spinner("Publicando..."):
                    success, res = orchestrator.facebook_api.create_post_with_image(fb_msg, st.session_state.generated_img)
                    if success:
                        st.balloons()
                        st.success(f"¡Publicado con éxito! ID: {res.get('post_id')}")
                    else:
                        st.error(f"Error: {res.get('error')}")

elif selected_mode == "🛠️ Generar Manual":
    st.header("🛠️ Constructor de Posts Manual")
    template = st.selectbox("Template:", ["tutorial", "quote", "news", "tips", "event"])
    
    # Renderizar inputs dinámicos según el template... (por brevedad simplificamos)
    st.info("Ingresa los datos manualmente para generar una infografía específica.")
    
    if template == "tutorial":
        title = st.text_input("Título del Tutorial")
        steps = []
        for i in range(4):
            steps.append(st.text_input(f"Paso {i+1}"))
        cta = st.text_input("Call to Action", "¡Guarda este post!")
        
        if st.button("🎨 Generar Tutorial"):
            data = {"title": title, "steps": [s for s in steps if s], "cta": cta}
            path = generate_image("tutorial", data)
            st.image(Image.open(path))

elif selected_mode == "📅 Programación":
    st.header("📅 Calendario Editorial")
    st.write("Aquí podrás ver los posts programados por Galldroko.")
    st.warning("Implementación de base de datos TinyDB pendiente para seguimiento.")
