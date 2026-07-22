import streamlit as st
import requests
from PIL import Image
import io
import base64
import random
import time

# ====== PAGE CONFIG ======
st.set_page_config(page_title="AI Design Generator", page_icon="🎨", layout="wide")

# ====== CUSTOM CSS – DARK PROFESSIONAL THEME ======
st.markdown("""
<style>
    /* Main container */
    .stApp {
        background: #0e1117;
        color: #f0f2f6;
    }
    .stApp [data-testid="stAppViewContainer"] {
        background: transparent;
    }
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    /* Inputs */
    .stTextInput > div > div > input {
        background: #1e2128 !important;
        color: #ffffff !important;
        border: 1px solid #3a3f4a !important;
        border-radius: 8px !important;
    }
    .stTextArea > div > textarea {
        background: #1e2128 !important;
        color: #ffffff !important;
        border: 1px solid #3a3f4a !important;
        border-radius: 8px !important;
    }
    .stSelectbox > div > div {
        background: #1e2128 !important;
        color: #ffffff !important;
    }
    .stSlider > div > div {
        background: #3a3f4a !important;
    }
    /* Buttons */
    .stButton > button {
        background: linear-gradient(105deg, #6c5ce7 0%, #a29bfe 100%);
        color: white;
        border: none;
        border-radius: 40px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 20px rgba(108, 92, 231, 0.4);
    }
    /* Image containers */
    .generated-image {
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.5);
        margin: 10px 0;
        width: 100%;
    }
    .history-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 15px;
        margin: 10px 0;
    }
    .history-item {
        background: #1e2128;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #3a3f4a;
        transition: 0.2s;
    }
    .history-item:hover {
        transform: scale(1.02);
        border-color: #6c5ce7;
    }
    .history-item img {
        width: 100%;
        border-radius: 6px;
    }
    .history-item .prompt-text {
        font-size: 0.8rem;
        color: #aaa;
        margin-top: 5px;
        word-break: break-word;
    }
    .preset-btn {
        background: #2a2d36 !important;
        color: #f0f2f6 !important;
        border: 1px solid #3a3f4a !important;
        border-radius: 20px !important;
        padding: 0.2rem 1rem !important;
        font-size: 0.8rem !important;
        margin: 2px !important;
    }
    .preset-btn:hover {
        background: #3a3f4a !important;
    }
</style>
""", unsafe_allow_html=True)

# ====== SIDEBAR ======
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/6c5ce7/FFFFFF?text=Design+AI", use_column_width=True)
    st.markdown("---")
    st.header("⚙️ Settings")
    width = st.selectbox("Width", [512, 768, 1024, 1280], index=2)
    height = st.selectbox("Height", [512, 768, 1024, 1280], index=2)
    style = st.selectbox("Style", ["No style", "Cinematic", "Anime", "Realistic", "Cyberpunk", "Watercolor", "3D Render"])
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption("Powered by [Pollinations.ai](https://pollinations.ai) – free, no API key required.")
    st.caption("Built by Gesner Deslandes | GlobalInternet.py")

# ====== MAIN ======
st.title("🎨 AI Design Generator")
st.markdown("Describe your dream design – I'll bring it to life.")

# Preset prompts
presets = [
    "Futuristic cityscape at sunset, neon lights, cyberpunk style",
    "Minimalist logo for a tech startup, geometric, blue and gold",
    "Vibrant tropical jungle with exotic flowers and waterfall",
    "Abstract digital art with flowing colorful curves",
    "Friendly cartoon character, mascot for a children's brand",
    "Elegant wedding invitation with gold foil and roses"
]

col_presets = st.columns(3)
for i, preset in enumerate(presets[:3]):
    with col_presets[i]:
        if st.button(preset, key=f"preset_{i}", help="Click to fill the prompt"):
            st.session_state.prompt = preset
            st.rerun()

# Prompt input
prompt = st.text_area("Enter your design prompt", height=100,
                      value=st.session_state.get("prompt", ""),
                      key="prompt_input")

# Generate button
col_gen, col_clear = st.columns([4, 1])
with col_gen:
    generate = st.button("🚀 Generate Design", use_container_width=True)
with col_clear:
    clear = st.button("🗑️ Clear", use_container_width=True)
    if clear:
        st.session_state.prompt = ""
        st.rerun()

# ====== GENERATION LOGIC ======
def generate_image(prompt, width, height, style):
    """Generate image using Pollinations.ai."""
    # Apply style if selected
    style_map = {
        "Cinematic": "cinematic",
        "Anime": "anime",
        "Realistic": "realistic",
        "Cyberpunk": "cyberpunk",
        "Watercolor": "watercolor",
        "3D Render": "3d+render",
    }
    style_param = style_map.get(style, "")
    if style_param:
        prompt = f"{prompt}, {style_param} style"
    # URL encode prompt
    import urllib.parse
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={random.randint(1,999999)}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            st.error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

if generate and prompt:
    with st.spinner("🎨 Creating your design..."):
        img = generate_image(prompt, width, height, style)
        if img:
            # Display
            st.markdown("### ✨ Generated Design")
            col_display, col_info = st.columns([2, 1])
            with col_display:
                st.image(img, use_column_width=True)
            with col_info:
                st.markdown(f"**Prompt:** {prompt}")
                st.markdown(f"**Size:** {width}×{height}")
                st.markdown(f"**Style:** {style if style != 'No style' else 'None'}")
                # Download
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                st.download_button(
                    label="💾 Download PNG",
                    data=byte_im,
                    file_name=f"design_{int(time.time())}.png",
                    mime="image/png",
                    use_container_width=True
                )
            # Save to history
            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({
                "prompt": prompt,
                "image": img,
                "timestamp": time.time()
            })
            # Keep only last 20
            if len(st.session_state.history) > 20:
                st.session_state.history = st.session_state.history[-20:]

# ====== HISTORY GALLERY ======
if "history" in st.session_state and st.session_state.history:
    st.markdown("---")
    st.markdown("### 🖼️ History")
    # Display last 5
    history_items = st.session_state.history[-5:][::-1]  # newest first
    cols = st.columns(3)
    for idx, item in enumerate(history_items):
        with cols[idx % 3]:
            with st.container():
                st.image(item["image"], use_column_width=True)
                st.caption(item["prompt"][:80] + ("..." if len(item["prompt"]) > 80 else ""))
                if st.button("Use this prompt", key=f"use_{idx}"):
                    st.session_state.prompt = item["prompt"]
                    st.rerun()
else:
    if not generate:
        st.info("👆 Enter a prompt and click **Generate Design** to create something beautiful.")

# ====== FOOTER ======
st.markdown("---")
st.caption("Built with ❤️ by Gesner Deslandes | GlobalInternet.py")
st.caption("📞 (509) 4738-5663 | 📧 deslandes78@gmail.com")
