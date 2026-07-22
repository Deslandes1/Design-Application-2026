import streamlit as st
import requests
from PIL import Image, ImageDraw
import io
import base64
import random
import time
import urllib.parse

# ====== PAGE CONFIG ======
st.set_page_config(page_title="Be Like Brit Design", page_icon="🎨", layout="wide")

# ====== CUSTOM CSS – LIGHT BLUE THEME ======
st.markdown("""
<style>
    .stApp { background: #E3F2FD; color: #1a2a3a; }
    .stApp [data-testid="stAppViewContainer"] { background: transparent; }
    [data-testid="stSidebar"] { background: #B3E5FC !important; border-right: 1px solid #90CAF9; }
    [data-testid="stSidebar"] * { color: #0a2a44 !important; }
    .stSidebar .stButton > button { background: #64B5F6 !important; color: white !important; }
    h1, h2, h3 { color: #0a2a44 !important; }
    .stTextInput > div > div > input,
    .stTextArea > div > textarea,
    .stSelectbox > div > div { background: #FFFFFF !important; color: #1a2a3a !important; border: 1px solid #90CAF9 !important; border-radius: 8px !important; }
    .stSlider > div > div { background: #64B5F6 !important; }
    .stButton > button { background: linear-gradient(105deg, #1E88E5 0%, #42A5F5 100%); color: white; border: none; border-radius: 40px; padding: 0.6rem 2rem; font-weight: 600; transition: 0.2s; width: 100%; }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 4px 20px rgba(30, 136, 229, 0.4); }
    .generated-image { border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.1); margin: 10px 0; width: 100%; }
    .history-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 15px; margin: 10px 0; }
    .history-item { background: white; border-radius: 8px; padding: 10px; border: 1px solid #90CAF9; transition: 0.2s; position: relative; }
    .history-item:hover { transform: scale(1.02); border-color: #1E88E5; }
    .history-item img { width: 100%; border-radius: 6px; }
    .history-item .prompt-text { font-size: 0.8rem; color: #1a2a3a; margin-top: 5px; word-break: break-word; }
    .history-item .delete-btn { position: absolute; top: 5px; right: 5px; background: #ff4444; color: white; border: none; border-radius: 50%; width: 24px; height: 24px; cursor: pointer; font-size: 14px; line-height: 24px; text-align: center; }
    .preset-btn { background: #E1F5FE !important; color: #0a2a44 !important; border: 1px solid #81D4FA !important; border-radius: 20px !important; padding: 0.2rem 1rem !important; font-size: 0.8rem !important; margin: 2px !important; }
    .preset-btn:hover { background: #B3E5FC !important; }
    .download-label { font-weight: 600; color: #0a2a44; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# ====== SIDEBAR ======
with st.sidebar:
    st.markdown("## ☀️ Summer 2026 Design Class")
    st.markdown("---")
    st.header("⚙️ Settings")
    width = st.selectbox("Width", [512, 768, 1024, 1280], index=2)
    height = st.selectbox("Height", [512, 768, 1024, 1280], index=2)
    style = st.selectbox("Style", ["No style", "Cinematic", "Anime", "Realistic", "Cyberpunk", "Watercolor", "3D Render"])
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.caption("Powered by [Pollinations.ai](https://pollinations.ai) – free, no API key required.")
    st.caption("Gesner Deslandes, Technology Coordinator at Be Like Brit Summer Project 2026")
    st.caption("📞 (509) 4738-5663")
    st.caption("📧 deslandes78@gmail.com")
    st.markdown("---")
    if st.button("🗑️ Clear All History", use_container_width=True):
        if "history" in st.session_state:
            st.session_state.history = []
        st.rerun()

# ====== MAIN PAGE TITLE ======
st.markdown("""
<div style="text-align: center; padding: 1rem 0 0.5rem 0;">
    <h1 style="font-size: 3.5rem; font-weight: 800; background: linear-gradient(135deg, #0D47A1 0%, #42A5F5 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0;">Be Like Brit</h1>
    <h2 style="font-size: 2.2rem; font-weight: 300; color: #0a2a44; margin-top: -0.5rem;">Design Application</h2>
    <hr style="width: 200px; border: 2px solid #42A5F5; border-radius: 5px; margin: 0.5rem auto;">
</div>
""", unsafe_allow_html=True)

st.markdown("Describe your dream design – I'll bring it to life.")

# ====== PRESET PROMPTS ======
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

# ====== PROMPT INPUT ======
prompt = st.text_area("Enter your design prompt", height=100,
                      value=st.session_state.get("prompt", ""),
                      key="prompt_input")

col_gen, col_clear = st.columns([4, 1])
with col_gen:
    generate = st.button("🚀 Generate Design", use_container_width=True)
with col_clear:
    clear = st.button("🗑️ Clear", use_container_width=True)
    if clear:
        st.session_state.prompt = ""
        st.rerun()

# ====== GENERATION LOGIC ======
def enhance_prompt(prompt):
    """Append quality keywords to improve output."""
    quality_keywords = "high quality, professional, detailed, 8k, sharp focus, vibrant colors"
    if not any(kw in prompt.lower() for kw in ["high quality", "professional", "detailed", "8k"]):
        prompt = f"{prompt}, {quality_keywords}"
    return prompt

def generate_image(prompt, width, height, style):
    """Generate image using Pollinations.ai with enhanced prompt."""
    style_map = {
        "Cinematic": "cinematic",
        "Anime": "anime",
        "Realistic": "realistic",
        "Cyberpunk": "cyberpunk",
        "Watercolor": "watercolor",
        "3D Render": "3d+render",
    }
    style_param = style_map.get(style, "")
    # Enhance the prompt
    enhanced_prompt = enhance_prompt(prompt)
    if style_param:
        enhanced_prompt = f"{enhanced_prompt}, {style_param} style"
    encoded = urllib.parse.quote(enhanced_prompt)
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

def add_background(img, bg_color, output_size=(1200, 1200)):
    """Place generated image on a colored background sheet."""
    canvas = Image.new('RGB', output_size, bg_color)
    img_w, img_h = img.size
    x = (output_size[0] - img_w) // 2
    y = (output_size[1] - img_h) // 2
    canvas.paste(img, (x, y))
    return canvas

# ====== GENERATE ======
if generate and prompt:
    with st.spinner("🎨 Creating your design..."):
        img = generate_image(prompt, width, height, style)
        if img:
            st.markdown("### ✨ Generated Design")
            col_display, col_info = st.columns([2, 1])
            with col_display:
                st.image(img, use_column_width=True)
            with col_info:
                st.markdown(f"**Prompt:** {prompt}")
                st.markdown(f"**Size:** {width}×{height}")
                st.markdown(f"**Style:** {style if style != 'No style' else 'None'}")
                st.markdown("---")
                st.markdown("### 💾 Download Options")
                bg_option = st.selectbox("Choose background sheet color", ["White", "Black", "Custom"], index=0)
                if bg_option == "Custom":
                    custom_color = st.color_picker("Pick a color", "#FFFFFF")
                    bg_color = custom_color
                elif bg_option == "White":
                    bg_color = "#FFFFFF"
                else:
                    bg_color = "#000000"
                output_size = (max(width, height) + 200, max(width, height) + 200)
                bg_img = add_background(img, bg_color, output_size)
                buf = io.BytesIO()
                bg_img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                st.download_button(
                    label="⬇️ Download Design with Sheet",
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
                "timestamp": time.time(),
                "style": style,
                "width": width,
                "height": height
            })
            if len(st.session_state.history) > 20:
                st.session_state.history = st.session_state.history[-20:]

# ====== HISTORY GALLERY with Delete Option ======
if "history" in st.session_state and st.session_state.history:
    st.markdown("---")
    st.markdown("### 🖼️ History")
    history_items = st.session_state.history[::-1]  # newest first
    cols = st.columns(3)
    for idx, item in enumerate(history_items):
        with cols[idx % 3]:
            with st.container():
                # Display the image
                st.image(item["image"], use_column_width=True)
                st.caption(item["prompt"][:80] + ("..." if len(item["prompt"]) > 80 else ""))
                # Buttons row
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("♻️ Reuse", key=f"reuse_{idx}"):
                        st.session_state.prompt = item["prompt"]
                        st.rerun()
                with col_b:
                    if st.button("❌ Delete", key=f"del_{idx}"):
                        # Remove this item from history
                        st.session_state.history.remove(item)
                        st.rerun()
else:
    if not generate:
        st.info("👆 Enter a prompt and click **Generate Design** to create something beautiful.")

# ====== FOOTER ======
st.markdown("---")
st.caption("Gesner Deslandes, Technology Coordinator at Be Like Brit Summer Project 2026")
st.caption("📞 (509) 4738-5663 | 📧 deslandes78@gmail.com")
