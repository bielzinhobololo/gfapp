import io
import requests
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import pandas as pd

# -------------------------
# CONFIGURAÇÃO DO APP
# -------------------------
st.set_page_config(
    page_title="GfApp - Leitura de Meios de Cultura",
    layout="centered",
    page_icon="🔬"
)

# Paleta dark/gótica
PRIMARY_COLOR = "#8A2BE2"   # Roxo
SECONDARY_COLOR = "#000000" # Preto
TEXT_COLOR = "#E0E0E0"      # Cinza claro

# CSS customizado
st.markdown(f"""
    <style>
        .stApp {{
            background-color: {SECONDARY_COLOR};
            color: {TEXT_COLOR};
            font-family: "Arial", sans-serif;
        }}
        .stButton>button {{
            background-color: {PRIMARY_COLOR};
            color: white;
            font-size: 16px;
            border-radius: 8px;
            padding: 0.6em 1.2em;
            border: none;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }}
        .stButton>button:hover {{
            background-color: #BA55D3;
            color: black;
        }}
        h1, h2, h3, h4 {{
            color: {PRIMARY_COLOR};
            text-align: center;
        }}
        .example-card {{
            background-color: #111111;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 10px;
        }}
        .example-card img {{
            border-radius: 5px;
        }}
        .block-container {{
            text-align: center;
        }}
    </style>
""", unsafe_allow_html=True)

# -------------------------
# CONFIG DO ROBOFLOW
# -------------------------
API_KEY = "L7fyYDRGWncVRE5le4Rk"
INFERENCE_URL = "https://serverless.roboflow.com/my-first-project-v3eob/2"

# -------------------------
# SESSION STATE
# -------------------------
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

# -------------------------
# INTERFACE
# -------------------------
st.title("GfApp")
st.subheader("Leitura de Meios de Cultura")
st.markdown(
    "<div style='text-align: center;'>"
    "Envie imagens de placas de Petri para análise automática. "
    "O modelo identifica elementos presentes e apresenta os resultados de forma clara."
    "</div>", unsafe_allow_html=True
)

# Upload de imagem
file = st.file_uploader("Selecione uma imagem para análise:", type=["jpg", "jpeg", "png"])
if file is not None:
    st.session_state.uploaded_file = file

# -------------------------
# Exemplos em cards
# -------------------------
st.markdown("### Exemplos disponíveis")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="example-card">', unsafe_allow_html=True)
    st.image("exemplo1.jpg", caption="Exemplo 1", width="stretch")
    if st.button("Usar Exemplo 1"):
        st.session_state.uploaded_file = open("exemplo1.jpg", "rb")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="example-card">', unsafe_allow_html=True)
    st.image("exemplo2.jpg", caption="Exemplo 2", width="stretch")
    if st.button("Usar Exemplo 2"):
        st.session_state.uploaded_file = open("exemplo2.jpg", "rb")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Processamento
# -------------------------
if st.button("Enviar imagem para análise"):
    if st.session_state.uploaded_file is None:
        st.error("Por favor, selecione ou carregue uma imagem.")
    else:
        uploaded_file = st.session_state.uploaded_file
        img_bytes = uploaded_file.read()
        endpoint = f"{INFERENCE_URL}?api_key={API_KEY}"

        try:
            with st.spinner("Analisando imagem..."):
                res = requests.post(endpoint, files={"file": img_bytes}, timeout=60)

            if res.status_code != 200:
                st.error(f"Erro {res.status_code}: {res.text}")
            else:
                data = res.json()
                predictions = data.get("predictions", [])

                if not predictions:
                    st.warning("Nenhum objeto foi identificado na imagem.")
                    st.image(Image.open(io.BytesIO(img_bytes)), caption="Imagem enviada", width="stretch")
                else:
                    # Tabela de resultados
                    df = pd.DataFrame(predictions)
                    st.subheader("Resultados da análise")
                    st.dataframe(df)

                    # Desenhar caixas na imagem
                    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    draw = ImageDraw.Draw(pil_img)

                    try:
                        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
                    except:
                        font = ImageFont.load_default()

                    for p in predictions:
                        x, y, w, h = p["x"], p["y"], p["width"], p["height"]
                        label = p["class"]
                        conf = p["confidence"]

                        x0, y0 = x - w / 2, y - h / 2
                        x1, y1 = x + w / 2, y + h / 2

                        draw.rectangle([x0, y0, x1, y1], outline=PRIMARY_COLOR, width=3)
                        text = f"{label} ({conf:.2f})"
                        draw.text((x0, y0 - 15), text, fill=PRIMARY_COLOR, font=font)

                    st.subheader("Imagem processada")
                    st.image(pil_img, width="stretch")
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
