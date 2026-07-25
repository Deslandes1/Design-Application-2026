import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import random
import time
import urllib.parse
import os
import tempfile
import numpy as np

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
    width = st.selectbox("Width", [512, 768, 1024, 1280, 1920], index=3)
    height = st.selectbox("Height", [512, 768, 1024, 1280, 1920], index=3)
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

# ====== MODE SELECTION ======
mode = st.radio(
    "Choose your design source:",
    ["🎨 AI Generation (Text)", "🖼️ Upload Image", "🎬 Upload Video", "🎬 Slideshow (Multiple Clips)", "📄 Flyer Creator", "⬜ Blank Sheet", "🟦 Color Sheet"],
    horizontal=True,
    index=5
)

st.markdown("---")

# ====== INPUT SECTION ======
uploaded_image = None
uploaded_video = None
uploaded_files = None
prompt = ""
flyer_company = "MisNova"
flyer_subtitle = "Personalisation de Qualité"
flyer_services = """Impression sur T-shirts et Polo
Personnalisation de Sacs et Casquettes
Flyers et Affiches
Bâches et Enseignes
Marquage sur Verrerie et Métal
Impressions Grand Format"""
color_sheet_bg = "#FFFFFF"
service_lines_input = ""
service_font_size = 30
service_line_spacing = 50
service_bullets = True

if mode == "🎨 AI Generation (Text)":
    st.markdown("Describe your dream design – I'll bring it to life.")
    st.caption("💡 For long text (like flyer details), please use the **📄 Flyer Creator** mode for best results. This AI mode works best with short, descriptive prompts (under 450 characters).")
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
    prompt = st.text_area(
        "Enter your design prompt",
        height=100,
        value=st.session_state.get("prompt", ""),
        key="prompt_input"
    )
    if prompt:
        char_count = len(prompt)
        if char_count > 450:
            st.warning(f"⚠️ Your prompt is {char_count} characters. It will be automatically shortened to ~450 characters to avoid API errors.")
        else:
            st.info(f"📝 {char_count} characters (safe limit: 450)")

elif mode == "🖼️ Upload Image":
    st.markdown("Upload an image, and we'll add your title/subtitle overlay to it.")
    uploaded_image = st.file_uploader(
        "Choose an image...",
        type=["png", "jpg", "jpeg", "webp", "bmp"],
        key="img_uploader"
    )
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Preview of uploaded image", use_column_width=True)

elif mode == "🎬 Upload Video":
    st.markdown("Upload a video, and we'll overlay your title/subtitle onto it.")
    st.info("⏳ Processing video may take a moment. Keep the video under 30 seconds for best performance.")
    uploaded_video = st.file_uploader(
        "Choose a video...",
        type=["mp4", "avi", "mov", "mkv", "webm"],
        key="vid_uploader"
    )
    if uploaded_video is not None:
        st.success(f"✅ Video loaded: {uploaded_video.name} (Size: {uploaded_video.size // 1024} KB)")

elif mode == "🎬 Slideshow (Multiple Clips)":
    st.markdown("Upload multiple videos and/or images to create a slideshow. Order is the upload order.")
    st.info("You can upload up to 10 files (videos and images mixed). Images will be shown for a set duration.")
    uploaded_files = st.file_uploader(
        "Choose files...",
        type=["mp4", "avi", "mov", "mkv", "webm", "png", "jpg", "jpeg", "webp", "bmp"],
        accept_multiple_files=True,
        key="slideshow_uploader"
    )
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} files uploaded.")
        for f in uploaded_files:
            st.caption(f"• {f.name} ({f.size // 1024} KB)")

elif mode == "📄 Flyer Creator":
    st.markdown("### 🖨️ Create a professional flyer")
    st.success("💡 This mode generates flyers **without any API calls** – ideal for structured designs like flyers, posters, and business cards.")
    flyer_company = st.text_input("Company / Logo name", value="MisNova", key="flyer_company")
    flyer_subtitle = st.text_input("Subtitle", value="Personalisation de Qualité", key="flyer_subtitle")
    flyer_services = st.text_area(
        "Services (one per line)",
        value="""Impression sur T-shirts et Polo
Personnalisation de Sacs et Casquettes
Flyers et Affiches
Bâches et Enseignes
Marquage sur Verrerie et Métal
Impressions Grand Format""",
        height=200,
        key="flyer_services"
    )

elif mode in ["⬜ Blank Sheet", "🟦 Color Sheet"]:
    if mode == "⬜ Blank Sheet":
        st.markdown("### ⬜ Generate a blank white sheet with your text")
        st.success("✅ This mode creates a **solid white background** with your title, subtitle, and optional service list.")
    else:
        st.markdown("### 🟦 Generate a solid color sheet with your text")
        st.success("✅ Choose any background color, add title/subtitle, and a service list.")
        color_sheet_bg = st.color_picker("Pick a background color", value="#FF6600", key="color_sheet_bg")
        st.caption(f"💡 Selected color: {color_sheet_bg}")
    
    st.markdown("---")
    st.markdown("### 📝 Additional text lines (e.g., services)")
    service_lines_input = st.text_area(
        "Enter each line (one per line)",
        value="Impression sur T-shirts et Polo\nPersonnalisation de Sacs et Casquettes\nFlyers et Affiches\nBâches et Enseignes\nMarquage sur Verrerie et Métal\nImpressions Grand Format",
        height=200,
        key="service_lines"
    )
    col1, col2 = st.columns(2)
    with col1:
        service_font_size = st.slider("Service font size", 10, 80, 30, key="service_font_size")
        service_line_spacing = st.slider("Line spacing", 20, 80, 50, key="service_spacing")
    with col2:
        service_bullets = st.checkbox("Add bullet points", value=True, key="service_bullets")

st.markdown("---")

# ====== TEXT OVERLAY ======
st.markdown("### ✏️ Text Overlay (professional & colourful)")
col1, col2 = st.columns(2)
with col1:
    overlay_title = st.text_input("Title text", placeholder="e.g. Be Like Brit Summer 2026")
    overlay_subtitle = st.text_input("Subtitle text", placeholder="e.g. Design Class by Venite")
with col2:
    title_font_size = st.slider("Title font size", 1, 600, 200, step=1)
    subtitle_font_size = st.slider("Subtitle font size", 1, 600, 100, step=1)
    text_color = st.color_picker("Text color", "#FFD700")
    text_position = st.selectbox("Position", ["Top", "Center", "Bottom"])

st.markdown("---")

# ====== LOGO OVERLAY ======
st.markdown("### 🖼️ Logo Overlay (Optional)")
st.caption("Upload a logo or image to place in a corner. PNG with transparency works best. **Leave empty for a clean sheet with only text.**")
col_logo1, col_logo2 = st.columns(2)
with col_logo1:
    uploaded_logo = st.file_uploader(
        "Upload logo (PNG/JPG)",
        type=["png", "jpg", "jpeg", "webp"],
        key="logo_uploader"
    )
with col_logo2:
    logo_corner = st.selectbox(
        "Corner position",
        ["Top Left", "Top Right", "Bottom Left", "Bottom Right"],
        key="logo_corner"
    )
    logo_size_percent = st.slider(
        "Logo size (% of canvas width)",
        5, 30, 15,
        key="logo_size"
    ) / 100.0

st.markdown("---")

# ====== BACKGROUND AUDIO ======
if mode in ["🎬 Upload Video", "🎬 Slideshow (Multiple Clips)"]:
    st.markdown("### 🎵 Background Audio (Optional)")
    st.caption("Choose a preset sound or upload your own.")

    PRESET_SOUNDS = {
        "None": None,
        "Joy (Happy)": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "Victory (Triumph)": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "Love (Romantic)": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        "Discovery (Adventure)": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
        "Inspirational": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
        "Relaxing": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
        "Custom (upload your own)": None
    }

    sound_options = list(PRESET_SOUNDS.keys())
    selected_sound = st.selectbox("Select background sound", sound_options, index=0, key="bg_sound_selector")

    custom_audio_upload = None
    if selected_sound == "Custom (upload your own)":
        custom_audio_upload = st.file_uploader(
            "Upload your audio (MP3/WAV/M4A)",
            type=["mp3", "wav", "m4a"],
            key="custom_audio_uploader"
        )
        if custom_audio_upload:
            st.success(f"✅ Audio loaded: {custom_audio_upload.name}")

    st.markdown("---")

if mode == "🎬 Slideshow (Multiple Clips)":
    image_duration = st.slider("Image duration (seconds)", 1, 10, 3, key="img_dur_slideshow")

# ====== GENERATE BUTTON ======
col_gen, col_clear = st.columns([4, 1])
with col_gen:
    generate = st.button("🚀 Generate / Apply Design", use_container_width=True)
with col_clear:
    clear = st.button("🗑️ Clear", use_container_width=True)
    if clear:
        if mode == "🎨 AI Generation (Text)":
            st.session_state.prompt = ""
        st.rerun()

# ====== FONT LOADER ======
def get_font(size, bold=True):
    ttf_files = [f for f in os.listdir('.') if f.lower().endswith('.ttf')]
    if ttf_files:
        try:
            return ImageFont.truetype(ttf_files[0], size)
        except:
            pass
    font_names = [
        "OpenSans-Bold.ttf", "OpenSans-Regular.ttf",
        "DejaVuSans-Bold.ttf", "DejaVuSans.ttf",
        "Arial Bold.ttf", "Arial.ttf", "arialbd.ttf", "arial.ttf"
    ]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except:
            pass
    st.warning("No scalable font found. Using fallback – text may be small. Upload a TrueType font (.ttf) file to the app folder for best results.")
    return ImageFont.load_default()

def get_font_path():
    ttf_files = [f for f in os.listdir('.') if f.lower().endswith('.ttf')]
    if ttf_files:
        return os.path.abspath(ttf_files[0])
    common_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/Arial.ttf"
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

# ====== GENERATION HELPERS ======
def enhance_prompt(prompt):
    quality_keywords = "high quality, professional, detailed, 8k, sharp focus, vibrant colors"
    if not any(kw in prompt.lower() for kw in ["high quality", "professional", "detailed", "8k"]):
        prompt = f"{prompt}, {quality_keywords}"
    return prompt

def truncate_prompt(prompt, max_length=450):
    cleaned = ' '.join(prompt.split())
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length] + "..."
    return cleaned

def create_placeholder_image(width, height):
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        ratio = y / height
        r = int(10 + 40 * ratio)
        g = int(20 + 20 * ratio)
        b = int(40 + 80 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    center = (width//2, height//2)
    for radius in range(min(width, height)//2, 0, -5):
        alpha = int(10 * (1 - radius / (min(width, height)//2)))
        overlay = Image.new('RGBA', (width, height), (0,0,0,0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.ellipse((center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius), 
                             fill=(255,255,255,alpha))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    return img

def create_fallback_image(prompt, width, height):
    img = Image.new('RGB', (width, height), color='#1a2a3a')
    draw = ImageDraw.Draw(img)
    try:
        font = get_font(40, bold=True)
    except:
        font = ImageFont.load_default()
    lines = []
    words = prompt.split()
    line = ""
    for word in words:
        if draw.textlength(line + " " + word, font=font) < width - 40:
            line += " " + word
        else:
            lines.append(line.strip())
            line = word
    if line:
        lines.append(line.strip())
    y = 50
    for line in lines:
        draw.text((20, y), line, font=font, fill='#FFFFFF')
        y += 50
    draw.text((20, height - 40), "Fallback image - API unavailable", font=font, fill='#FF6600')
    return img

def generate_image(prompt, width, height, style):
    cleaned_prompt = truncate_prompt(prompt, max_length=450)
    if len(cleaned_prompt) != len(prompt):
        st.info(f"✂️ Prompt shortened from {len(prompt)} to {len(cleaned_prompt)} characters.")
    style_map = {
        "Cinematic": "cinematic",
        "Anime": "anime",
        "Realistic": "realistic",
        "Cyberpunk": "cyberpunk",
        "Watercolor": "watercolor",
        "3D Render": "3d+render",
    }
    style_param = style_map.get(style, "")
    enhanced_prompt = enhance_prompt(cleaned_prompt)
    if style_param:
        enhanced_prompt = f"{enhanced_prompt}, {style_param} style"
    encoded = urllib.parse.quote(enhanced_prompt)
    urls = [
        f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={random.randint(1,999999)}",
        f"https://pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed={random.randint(1,999999)}"
    ]
    for attempt in range(3):
        for url in urls:
            try:
                response = requests.get(url, timeout=60)
                if response.status_code != 200:
                    st.warning(f"Attempt {attempt+1}: Status {response.status_code}. Retrying...")
                    time.sleep(2)
                    continue
                content_type = response.headers.get('Content-Type', '')
                if 'image' not in content_type:
                    st.warning(f"Attempt {attempt+1}: Received non-image content ({content_type}). Retrying...")
                    time.sleep(2)
                    continue
                try:
                    img = Image.open(io.BytesIO(response.content))
                    return img
                except Exception as e:
                    st.warning(f"Attempt {attempt+1}: Cannot open image: {e}. Retrying...")
                    time.sleep(2)
                    continue
            except requests.exceptions.Timeout:
                st.warning(f"Attempt {attempt+1}: Timeout. Retrying...")
                time.sleep(3)
            except Exception as e:
                st.warning(f"Attempt {attempt+1}: {e}. Retrying...")
                time.sleep(2)
    st.warning("Using generated fallback image (API unavailable).")
    return create_fallback_image(prompt, width, height)

def add_text_overlay(img, title, subtitle, title_size, subtitle_size, color, position):
    """
    Draws title and subtitle on the image.
    Returns: (img, y_after_subtitle) where y_after_subtitle is the Y coordinate right after the subtitle.
    """
    img = img.copy()
    w, h = img.size
    draw = ImageDraw.Draw(img)
    title_font = get_font(title_size, bold=True)
    subtitle_font = get_font(subtitle_size, bold=True)
    
    if position == "Top":
        y_start = int(h * 0.08)
    elif position == "Bottom":
        y_start = int(h * 0.70)
    else:
        y_start = int(h * 0.28)
    
    temp = Image.new('RGB', (1,1))
    temp_draw = ImageDraw.Draw(temp)
    title_bbox = temp_draw.textbbox((0,0), title, font=title_font) if title else (0,0,0,0)
    subtitle_bbox = temp_draw.textbbox((0,0), subtitle, font=subtitle_font) if subtitle else (0,0,0,0)
    title_w = title_bbox[2] - title_bbox[0] if title else 0
    title_h = title_bbox[3] - title_bbox[1] if title else 0
    sub_w = subtitle_bbox[2] - subtitle_bbox[0] if subtitle else 0
    sub_h = subtitle_bbox[3] - subtitle_bbox[1] if subtitle else 0
    
    y = y_start
    if title:
        # Shadow/glow effects
        for offset in range(10, 0, -2):
            alpha = int(30 * (offset/10))
            glow_color = (255,255,255, alpha)
            draw.text((w//2 - title_w//2 + offset//2, y+offset//2), title, font=title_font, fill=glow_color)
        for dx in range(-4, 5, 2):
            for dy in range(-4, 5, 2):
                if dx != 0 or dy != 0:
                    draw.text((w//2 - title_w//2 + dx, y+dy), title, font=title_font, fill='black')
        draw.text((w//2 - title_w//2, y), title, font=title_font, fill=color)
        y += title_h + 25
    
    if subtitle:
        for offset in range(6, 0, -2):
            alpha = int(20 * (offset/6))
            glow_color = (255,255,255, alpha)
            draw.text((w//2 - sub_w//2 + offset//2, y+offset//2), subtitle, font=subtitle_font, fill=glow_color)
        for dx in range(-3, 4, 2):
            for dy in range(-3, 4, 2):
                if dx != 0 or dy != 0:
                    draw.text((w//2 - sub_w//2 + dx, y+dy), subtitle, font=subtitle_font, fill='black')
        draw.text((w//2 - sub_w//2, y), subtitle, font=subtitle_font, fill=color)
        y += sub_h + 25
    else:
        # If no subtitle, add a small padding after title
        y += 10  # minimal gap
    
    return img, y

def add_service_lines(img, lines, font_size, line_spacing, color, start_y, bullets=True):
    """
    Draw a list of lines with optional bullet points.
    """
    img = img.copy()
    w, h = img.size
    draw = ImageDraw.Draw(img)
    font = get_font(font_size, bold=False)
    bullet_color = "#FF6600"  # orange bullet
    bullet_radius = 6
    margin = int(w * 0.08)  # left margin for text and bullets
    bullet_x = margin - bullet_radius - 8

    y = start_y
    for line in lines:
        if not line.strip():
            continue
        if bullets:
            # Draw bullet
            draw.ellipse((bullet_x - bullet_radius, y - bullet_radius, bullet_x + bullet_radius, y + bullet_radius), fill=bullet_color)
            draw.text((margin, y - font_size//2), line.strip(), font=font, fill=color)
        else:
            draw.text((margin, y - font_size//2), line.strip(), font=font, fill=color)
        y += line_spacing
    return img

def add_background(img, bg_color, output_size=(1200, 1200)):
    canvas = Image.new('RGB', output_size, bg_color)
    img_w, img_h = img.size
    x = (output_size[0] - img_w) // 2
    y = (output_size[1] - img_h) // 2
    canvas.paste(img, (x, y))
    return canvas

def add_logo_overlay(img, logo_bytes, corner, size_percent):
    if logo_bytes is None:
        return img
    try:
        logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
    except:
        st.warning("Could not open logo file. Skipping logo overlay.")
        return img
    img = img.copy()
    w, h = img.size
    logo_w = int(w * size_percent)
    logo_h = int(logo_w * (logo.height / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    padding = int(w * 0.02)
    if corner == "Top Left":
        x, y = padding, padding
    elif corner == "Top Right":
        x, y = w - logo_w - padding, padding
    elif corner == "Bottom Left":
        x, y = padding, h - logo_h - padding
    else:
        x, y = w - logo_w - padding, h - logo_h - padding
    if logo.mode == 'RGBA':
        img.paste(logo, (x, y), logo.split()[3])
    else:
        img.paste(logo, (x, y))
    return img

# ====== VIDEO HELPERS (unchanged) ======
def create_text_image_for_video(width, height, title, subtitle, title_size, subtitle_size, color, position):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_title = get_font(title_size, bold=True)
    font_sub = get_font(subtitle_size, bold=True)
    temp = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp)
    if title:
        bbox = temp_draw.textbbox((0, 0), title, font=font_title)
        title_w = bbox[2] - bbox[0]
        title_h = bbox[3] - bbox[1]
    else:
        title_w = title_h = 0
    if subtitle:
        bbox = temp_draw.textbbox((0, 0), subtitle, font=font_sub)
        sub_w = bbox[2] - bbox[0]
        sub_h = bbox[3] - bbox[1]
    else:
        sub_w = sub_h = 0
    if position == "Top":
        y_start = int(height * 0.08)
    elif position == "Bottom":
        y_start = int(height * 0.70)
    else:
        y_start = int(height * 0.28)
    y = y_start
    if title:
        x = (width - title_w) // 2
        for dx in range(-4, 5, 2):
            for dy in range(-4, 5, 2):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), title, font=font_title, fill='black')
        draw.text((x, y), title, font=font_title, fill=color)
        y += title_h + 25
    if subtitle:
        x = (width - sub_w) // 2
        for dx in range(-3, 4, 2):
            for dy in range(-3, 4, 2):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), subtitle, font=font_sub, fill='black')
        draw.text((x, y), subtitle, font=font_sub, fill=color)
    return img

def apply_audio_fade(audio_clip, fade_duration=2.0):
    try:
        from moviepy.audio.fx.audio_fadein import audio_fadein
        from moviepy.audio.fx.audio_fadeout import audio_fadeout
        if audio_clip.duration > fade_duration * 2:
            audio_clip = audio_clip.fx(audio_fadein, fade_duration)
            audio_clip = audio_clip.fx(audio_fadeout, fade_duration)
        else:
            half = audio_clip.duration / 2
            if half > 0.5:
                audio_clip = audio_clip.fx(audio_fadein, half)
                audio_clip = audio_clip.fx(audio_fadeout, half)
    except Exception:
        pass
    return audio_clip

def process_video_with_overlay(video_file, title, subtitle, title_size, subtitle_size, color, position,
                               logo_bytes, logo_corner, logo_size_percent,
                               audio_bytes=None, mute_original=False):
    try:
        from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip, AudioFileClip, CompositeAudioClip
    except ImportError:
        st.error("MoviePy is not installed. Please run: pip install moviepy")
        return None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_input:
        tmp_input.write(video_file.read())
        input_path = tmp_input.name
    try:
        clip = VideoFileClip(input_path)
        if clip.duration > 60:
            st.warning(f"Video is {clip.duration:.1f}s long. Processing only the first 60 seconds.")
            clip = clip.subclip(0, 60)
        w, h = clip.size
        clips_to_composite = [clip]
        text_pil = create_text_image_for_video(
            w, h, title, subtitle, title_size, subtitle_size, color, position
        )
        text_np = np.array(text_pil)
        text_clip = ImageClip(text_np).set_duration(clip.duration).set_position((0, 0))
        clips_to_composite.append(text_clip)
        if logo_bytes is not None:
            try:
                logo_pil = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
                logo_w = int(w * logo_size_percent)
                logo_h = int(logo_w * (logo_pil.height / logo_pil.width))
                logo_pil = logo_pil.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
                logo_np = np.array(logo_pil)
                logo_clip = ImageClip(logo_np).set_duration(clip.duration)
                padding = int(w * 0.02)
                if logo_corner == "Top Left":
                    pos = (padding, padding)
                elif logo_corner == "Top Right":
                    pos = (w - logo_w - padding, padding)
                elif logo_corner == "Bottom Left":
                    pos = (padding, h - logo_h - padding)
                else:
                    pos = (w - logo_w - padding, h - logo_h - padding)
                logo_clip = logo_clip.set_position(pos)
                clips_to_composite.append(logo_clip)
            except Exception as e:
                st.warning(f"Could not add logo to video: {e}")
        final_clip = CompositeVideoClip(clips_to_composite)
        if audio_bytes is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                tmp_audio.write(audio_bytes)
                audio_path = tmp_audio.name
            try:
                bg_audio = AudioFileClip(audio_path)
                if bg_audio.duration < final_clip.duration:
                    bg_audio = bg_audio.loop(duration=final_clip.duration)
                else:
                    bg_audio = bg_audio.subclip(0, final_clip.duration)
                bg_audio = apply_audio_fade(bg_audio, fade_duration=2.0)
                if mute_original:
                    final_clip = final_clip.set_audio(bg_audio)
                else:
                    if final_clip.audio is not None:
                        orig_audio = final_clip.audio.volumex(1.0)
                        bg_audio = bg_audio.volumex(0.3)
                        mixed = CompositeAudioClip([orig_audio, bg_audio])
                        final_clip = final_clip.set_audio(mixed)
                    else:
                        final_clip = final_clip.set_audio(bg_audio)
            except Exception as e:
                st.warning(f"Could not process background audio: {e}")
            finally:
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_output:
            output_path = tmp_output.name
        final_clip.write_videofile(
            output_path,
            fps=clip.fps,
            codec='libx264',
            audio_codec='aac',
            preset='ultrafast',
            threads=2,
            verbose=False,
            logger=None
        )
        return output_path
    except Exception as e:
        st.error(f"Video processing error: {e}")
        return None
    finally:
        if os.path.exists(input_path):
            os.unlink(input_path)

# ====== SLIDESHOW (unchanged) ======
def resize_clip_with_pil(clip, target_w, target_h):
    def resize_frame(frame):
        pil_img = Image.fromarray(frame)
        resized = pil_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        return np.array(resized)
    return clip.fl_image(resize_frame)

def create_slideshow(uploaded_files, image_duration, audio_bytes,
                     title, subtitle, title_size, subtitle_size, color, position,
                     logo_bytes, logo_corner, logo_size_percent):
    try:
        from moviepy.editor import (
            VideoFileClip, ImageClip, concatenate_videoclips,
            AudioFileClip, CompositeAudioClip, CompositeVideoClip
        )
    except ImportError:
        st.error("MoviePy is not installed. Please run: pip install moviepy")
        return None
    if not uploaded_files:
        st.warning("No files uploaded.")
        return None
    clip_infos = []
    temp_paths = []
    first_video_fps = 24
    for file_obj in uploaded_files:
        ext = os.path.splitext(file_obj.name)[1].lower()
        if ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(file_obj.read())
                tmp_path = tmp.name
            temp_paths.append(tmp_path)
            try:
                clip = VideoFileClip(tmp_path)
                if first_video_fps == 24 and hasattr(clip, 'fps') and clip.fps:
                    first_video_fps = clip.fps
                clip_infos.append((clip, True))
            except Exception as e:
                st.warning(f"Could not load video {file_obj.name}: {e}")
                continue
        elif ext in ['.png', '.jpg', '.jpeg', '.webp', '.bmp']:
            try:
                img = Image.open(io.BytesIO(file_obj.read()))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                    img.save(tmp_img, format='PNG')
                    tmp_path = tmp_img.name
                temp_paths.append(tmp_path)
                clip = ImageClip(tmp_path).set_duration(image_duration)
                clip_infos.append((clip, False))
            except Exception as e:
                st.warning(f"Could not load image {file_obj.name}: {e}")
                continue
        else:
            st.warning(f"Unsupported file type: {file_obj.name}")
    if not clip_infos:
        st.error("No valid clips to create slideshow.")
        return None
    target_w = width
    target_h = height
    resized_clips = []
    is_video_flags = []
    for clip, is_video in clip_infos:
        if clip.size != (target_w, target_h):
            clip = resize_clip_with_pil(clip, target_w, target_h)
        resized_clips.append(clip)
        is_video_flags.append(is_video)
    total_dur = sum(c.duration for c in resized_clips)
    bg_audio_full = None
    if audio_bytes is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            tmp_audio.write(audio_bytes)
            audio_path = tmp_audio.name
        temp_paths.append(audio_path)
        try:
            bg_audio_full = AudioFileClip(audio_path)
            if bg_audio_full.duration < total_dur:
                bg_audio_full = bg_audio_full.loop(duration=total_dur)
            else:
                bg_audio_full = bg_audio_full.subclip(0, total_dur)
            bg_audio_full = apply_audio_fade(bg_audio_full, fade_duration=2.0)
        except Exception as e:
            st.warning(f"Could not load background audio: {e}")
            bg_audio_full = None
    final_clips = []
    current_time = 0.0
    for idx, (clip, is_video) in enumerate(zip(resized_clips, is_video_flags)):
        seg_duration = clip.duration
        audio_track = None
        if bg_audio_full is not None:
            bg_seg = bg_audio_full.subclip(current_time, current_time + seg_duration)
            if is_video:
                bg_vol = 0.1
            else:
                bg_vol = 0.7
            bg_seg = bg_seg.volumex(bg_vol)
        else:
            bg_seg = None
        if is_video:
            orig_audio = clip.audio
            if orig_audio is not None and bg_seg is not None:
                audio_track = CompositeAudioClip([orig_audio, bg_seg])
            elif orig_audio is not None:
                audio_track = orig_audio
            elif bg_seg is not None:
                audio_track = bg_seg
            else:
                audio_track = None
        else:
            if bg_seg is not None:
                audio_track = bg_seg
            else:
                audio_track = None
        if audio_track is not None:
            clip = clip.set_audio(audio_track)
        else:
            clip = clip.set_audio(None)
        final_clips.append(clip)
        current_time += seg_duration
    final_video = concatenate_videoclips(final_clips, method="compose")
    text_pil = create_text_image_for_video(
        target_w, target_h, title, subtitle, title_size, subtitle_size, color, position
    )
    text_np = np.array(text_pil)
    text_clip = ImageClip(text_np).set_duration(final_video.duration).set_position((0, 0))
    overlays = [final_video, text_clip]
    if logo_bytes is not None:
        try:
            logo_pil = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
            logo_w = int(target_w * logo_size_percent)
            logo_h = int(logo_w * (logo_pil.height / logo_pil.width))
            logo_pil = logo_pil.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            logo_np = np.array(logo_pil)
            logo_clip = ImageClip(logo_np).set_duration(final_video.duration)
            padding = int(target_w * 0.02)
            if logo_corner == "Top Left":
                pos = (padding, padding)
            elif logo_corner == "Top Right":
                pos = (target_w - logo_w - padding, padding)
            elif logo_corner == "Bottom Left":
                pos = (padding, target_h - logo_h - padding)
            else:
                pos = (target_w - logo_w - padding, target_h - logo_h - padding)
            logo_clip = logo_clip.set_position(pos)
            overlays.append(logo_clip)
        except Exception as e:
            st.warning(f"Could not add logo to slideshow: {e}")
    final_composite = CompositeVideoClip(overlays)
    fps = first_video_fps
    for c in resized_clips:
        if hasattr(c, 'fps') and c.fps:
            fps = c.fps
            break
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_output:
        output_path = tmp_output.name
    final_composite.write_videofile(
        output_path,
        fps=fps,
        codec='libx264',
        audio_codec='aac',
        preset='ultrafast',
        threads=2,
        verbose=False,
        logger=None
    )
    for path in temp_paths:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass
    return output_path

# ====== FLYER GENERATOR (unchanged) ======
def generate_flyer(company_name, subtitle, services_list, canvas_width, canvas_height):
    img = Image.new('RGB', (canvas_width, canvas_height), color='white')
    draw = ImageDraw.Draw(img)
    orange = "#FF6600"
    black = "#000000"
    dark_gray = "#333333"
    
    try:
        font_large = get_font(100, bold=True)
        font_medium = get_font(60, bold=True)
        font_small = get_font(40, bold=True)
        font_service = get_font(35, bold=False)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_service = ImageFont.load_default()

    def draw_centered(text, y, font, color, shadow=True):
        text_width = draw.textlength(text, font=font)
        x = (canvas_width - text_width) // 2
        if shadow:
            draw.text((x + 4, y + 4), text, font=font, fill='black')
        draw.text((x, y), text, font=font, fill=color)

    draw_centered(company_name, 60, font_large, orange, shadow=True)
    draw_centered("SERIGRAPHIE", 180, font_medium, orange, shadow=False)
    draw_centered(subtitle, 270, font_small, dark_gray, shadow=False)
    line_y = 330
    draw.line((canvas_width//4, line_y, canvas_width*3//4, line_y), fill=orange, width=3)
    service_start_y = 380
    line_spacing = 55
    for i, service in enumerate(services_list):
        if not service.strip():
            continue
        y = service_start_y + i * line_spacing
        bullet_radius = 8
        bullet_x = canvas_width // 4 - 30
        draw.ellipse((bullet_x - bullet_radius, y - bullet_radius, bullet_x + bullet_radius, y + bullet_radius), fill=orange)
        draw.text((canvas_width//4 + 10, y - 15), service.strip(), font=font_service, fill=black)
    footer_y = canvas_height - 60
    footer_text = "Contact: (509) 4738-5663 | deslandes78@gmail.com"
    draw_centered(footer_text, footer_y, font_service, dark_gray, shadow=False)
    return img

# ====== MAIN GENERATION LOGIC ======
if generate:
    audio_bytes = None
    if mode in ["🎬 Upload Video", "🎬 Slideshow (Multiple Clips)"]:
        if selected_sound != "None":
            if selected_sound == "Custom (upload your own)":
                if custom_audio_upload:
                    audio_bytes = custom_audio_upload.read()
            else:
                url = PRESET_SOUNDS.get(selected_sound)
                if url:
                    try:
                        response = requests.get(url, timeout=30)
                        if response.status_code == 200:
                            audio_bytes = response.content
                        else:
                            st.warning(f"Could not download preset sound: {selected_sound}")
                    except Exception as e:
                        st.warning(f"Error downloading preset sound: {e}")

    # ----- AI Generation -----
    if mode == "🎨 AI Generation (Text)":
        if not prompt:
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("🎨 Creating your design..."):
                img = generate_image(prompt, width, height, style)
                if img:
                    if overlay_title or overlay_subtitle:
                        img, _ = add_text_overlay(img, overlay_title, overlay_subtitle, title_font_size, subtitle_font_size, text_color, text_position)
                    img = add_logo_overlay(img, uploaded_logo.read() if uploaded_logo else None, logo_corner, logo_size_percent)
                    st.markdown("### ✨ Generated Design")
                    col_display, col_info = st.columns([2, 1])
                    with col_display:
                        st.image(img, use_column_width=True)
                    with col_info:
                        st.markdown(f"**Prompt:** {prompt[:200]}{'...' if len(prompt)>200 else ''}")
                        st.markdown(f"**Size:** {width}×{height}")
                        st.markdown(f"**Style:** {style if style != 'No style' else 'None'}")
                        st.markdown("---")
                        st.markdown("### 💾 Download Options")
                        bg_option = st.selectbox("Choose background sheet color", ["White", "Black", "Custom"], index=0, key="bg_ai")
                        if bg_option == "Custom":
                            custom_color = st.color_picker("Pick a color", "#FFFFFF", key="cp_ai")
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

    # ----- Upload Image -----
    elif mode == "🖼️ Upload Image":
        if uploaded_image is None:
            st.warning("Please upload an image first.")
        else:
            with st.spinner("🖼️ Applying design to your image..."):
                img = Image.open(uploaded_image)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                if overlay_title or overlay_subtitle:
                    img, _ = add_text_overlay(img, overlay_title, overlay_subtitle, title_font_size, subtitle_font_size, text_color, text_position)
                img = add_logo_overlay(img, uploaded_logo.read() if uploaded_logo else None, logo_corner, logo_size_percent)
                st.markdown("### ✨ Designed Image")
                col_display, col_info = st.columns([2, 1])
                with col_display:
                    st.image(img, use_column_width=True)
                with col_info:
                    st.markdown(f"**Original file:** {uploaded_image.name}")
                    st.markdown(f"**Size:** {width}×{height}")
                    st.markdown("---")
                    st.markdown("### 💾 Download Options")
                    bg_option = st.selectbox("Choose background sheet color", ["White", "Black", "Custom"], index=0, key="bg_img")
                    if bg_option == "Custom":
                        custom_color = st.color_picker("Pick a color", "#FFFFFF", key="cp_img")
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
                        label="⬇️ Download Designed Image with Sheet",
                        data=byte_im,
                        file_name=f"designed_{uploaded_image.name.split('.')[0]}_{int(time.time())}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                if "history" not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.append({
                    "prompt": f"Uploaded: {uploaded_image.name}",
                    "image": img,
                    "timestamp": time.time(),
                    "style": "Upload",
                    "width": width,
                    "height": height
                })
                if len(st.session_state.history) > 20:
                    st.session_state.history = st.session_state.history[-20:]

    # ----- Upload Video -----
    elif mode == "🎬 Upload Video":
        if uploaded_video is None:
            st.warning("Please upload a video first.")
        else:
            with st.spinner("🎬 Processing video with overlays and audio..."):
                logo_bytes = uploaded_logo.read() if uploaded_logo else None
                output_path = process_video_with_overlay(
                    uploaded_video,
                    overlay_title,
                    overlay_subtitle,
                    title_font_size,
                    subtitle_font_size,
                    text_color,
                    text_position,
                    logo_bytes,
                    logo_corner,
                    logo_size_percent,
                    audio_bytes,
                    mute_original=False
                )
                if output_path and os.path.exists(output_path):
                    st.success("✅ Video processed successfully!")
                    st.markdown("### 🎬 Designed Video")
                    with open(output_path, "rb") as f:
                        video_bytes = f.read()
                    st.download_button(
                        label="⬇️ Download Designed Video (MP4)",
                        data=video_bytes,
                        file_name=f"designed_{uploaded_video.name.split('.')[0]}_{int(time.time())}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    os.unlink(output_path)
                else:
                    st.error("Video processing failed. Please check the logs.")

    # ----- Slideshow -----
    elif mode == "🎬 Slideshow (Multiple Clips)":
        if not uploaded_files or len(uploaded_files) == 0:
            st.warning("Please upload at least one file.")
        else:
            with st.spinner("🎬 Creating slideshow with professional audio..."):
                logo_bytes = uploaded_logo.read() if uploaded_logo else None
                output_path = create_slideshow(
                    uploaded_files,
                    image_duration,
                    audio_bytes,
                    overlay_title,
                    overlay_subtitle,
                    title_font_size,
                    subtitle_font_size,
                    text_color,
                    text_position,
                    logo_bytes,
                    logo_corner,
                    logo_size_percent
                )
                if output_path and os.path.exists(output_path):
                    st.success("✅ Slideshow created successfully!")
                    st.markdown("### 🎬 Slideshow Video")
                    with open(output_path, "rb") as f:
                        video_bytes = f.read()
                    st.download_button(
                        label="⬇️ Download Slideshow (MP4)",
                        data=video_bytes,
                        file_name=f"slideshow_{int(time.time())}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    os.unlink(output_path)
                else:
                    st.error("Slideshow creation failed. Please check the logs.")

    # ----- Flyer Creator -----
    elif mode == "📄 Flyer Creator":
        with st.spinner("📄 Generating your professional flyer..."):
            services = [s.strip() for s in flyer_services.split('\n') if s.strip()]
            img = generate_flyer(
                company_name=flyer_company,
                subtitle=flyer_subtitle,
                services_list=services,
                canvas_width=width,
                canvas_height=height
            )
            if uploaded_logo is not None:
                img = add_logo_overlay(img, uploaded_logo.read(), logo_corner, logo_size_percent)
            st.markdown("### 📄 Your Professional Flyer")
            col_display, col_info = st.columns([2, 1])
            with col_display:
                st.image(img, use_column_width=True)
            with col_info:
                st.markdown(f"**Size:** {width}×{height}")
                st.markdown("---")
                st.markdown("### 💾 Download Options")
                bg_option = st.selectbox("Choose background sheet color", ["White", "Black", "Custom"], index=0, key="bg_flyer")
                if bg_option == "Custom":
                    custom_color = st.color_picker("Pick a color", "#FFFFFF", key="cp_flyer")
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
                    label="⬇️ Download Flyer with Sheet",
                    data=byte_im,
                    file_name=f"flyer_{int(time.time())}.png",
                    mime="image/png",
                    use_container_width=True
                )
            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({
                "prompt": f"Flyer: {flyer_company}",
                "image": img,
                "timestamp": time.time(),
                "style": "Flyer",
                "width": width,
                "height": height
            })
            if len(st.session_state.history) > 20:
                st.session_state.history = st.session_state.history[-20:]

    # ----- Blank Sheet (with service lines) -----
    elif mode == "⬜ Blank Sheet":
        with st.spinner("⬜ Generating blank white sheet with your text..."):
            img = Image.new('RGB', (width, height), color='white')
            y_after_text = 0
            if overlay_title or overlay_subtitle:
                img, y_after_text = add_text_overlay(img, overlay_title, overlay_subtitle, title_font_size, subtitle_font_size, text_color, text_position)
            else:
                # If no title/subtitle, start services from top with some padding
                y_after_text = int(height * 0.08)
            
            # Add service lines with a small gap (30px) after subtitle
            service_lines = [line for line in service_lines_input.split('\n') if line.strip()]
            if service_lines:
                start_y = y_after_text + 30  # small gap
                img = add_service_lines(img, service_lines, service_font_size, service_line_spacing, text_color, start_y, bullets=service_bullets)
            
            if uploaded_logo is not None:
                img = add_logo_overlay(img, uploaded_logo.read(), logo_corner, logo_size_percent)

            st.markdown("### ⬜ Your White Sheet")
            col_display, col_info = st.columns([2, 1])
            with col_display:
                st.image(img, use_column_width=True)
            with col_info:
                st.markdown(f"**Size:** {width}×{height}")
                st.markdown("---")
                st.markdown("### 💾 Download Options")
                bg_option = st.selectbox("Choose background sheet color", ["White", "Black", "Custom"], index=0, key="bg_blank")
                if bg_option == "Custom":
                    custom_color = st.color_picker("Pick a color", "#FFFFFF", key="cp_blank")
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
                    label="⬇️ Download White Sheet",
                    data=byte_im,
                    file_name=f"white_sheet_{int(time.time())}.png",
                    mime="image/png",
                    use_container_width=True
                )
            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({
                "prompt": f"White Sheet {width}x{height}",
                "image": img,
                "timestamp": time.time(),
                "style": "Blank",
                "width": width,
                "height": height
            })
            if len(st.session_state.history) > 20:
                st.session_state.history = st.session_state.history[-20:]

    # ----- Color Sheet (with service lines) -----
    elif mode == "🟦 Color Sheet":
        with st.spinner("🟦 Generating your custom color sheet with text..."):
            img = Image.new('RGB', (width, height), color=color_sheet_bg)
            y_after_text = 0
            if overlay_title or overlay_subtitle:
                img, y_after_text = add_text_overlay(img, overlay_title, overlay_subtitle, title_font_size, subtitle_font_size, text_color, text_position)
            else:
                y_after_text = int(height * 0.08)
            
            service_lines = [line for line in service_lines_input.split('\n') if line.strip()]
            if service_lines:
                start_y = y_after_text + 30
                img = add_service_lines(img, service_lines, service_font_size, service_line_spacing, text_color, start_y, bullets=service_bullets)
            
            if uploaded_logo is not None:
                img = add_logo_overlay(img, uploaded_logo.read(), logo_corner, logo_size_percent)

            st.markdown("### 🟦 Your Color Sheet")
            col_display, col_info = st.columns([2, 1])
            with col_display:
                st.image(img, use_column_width=True)
            with col_info:
                st.markdown(f"**Size:** {width}×{height}")
                st.markdown(f"**Background color:** {color_sheet_bg}")
                st.markdown("---")
                st.markdown("### 💾 Download Options")
                bg_option = st.selectbox("Choose background sheet color", ["White", "Black", "Custom"], index=0, key="bg_color")
                if bg_option == "Custom":
                    custom_color = st.color_picker("Pick a color", "#FFFFFF", key="cp_color")
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
                    label="⬇️ Download Color Sheet",
                    data=byte_im,
                    file_name=f"color_sheet_{int(time.time())}.png",
                    mime="image/png",
                    use_container_width=True
                )
            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({
                "prompt": f"Color Sheet {width}x{height} ({color_sheet_bg})",
                "image": img,
                "timestamp": time.time(),
                "style": "ColorSheet",
                "width": width,
                "height": height
            })
            if len(st.session_state.history) > 20:
                st.session_state.history = st.session_state.history[-20:]

# ====== HISTORY ======
if "history" in st.session_state and st.session_state.history:
    st.markdown("---")
    st.markdown("### 🖼️ History")
    history_items = st.session_state.history[::-1]
    cols = st.columns(3)
    for idx, item in enumerate(history_items):
        with cols[idx % 3]:
            with st.container():
                st.image(item["image"], use_column_width=True)
                st.caption(item["prompt"][:80] + ("..." if len(item["prompt"]) > 80 else ""))
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("♻️ Reuse", key=f"reuse_{idx}"):
                        st.session_state.prompt = item["prompt"]
                        st.rerun()
                with col_b:
                    if st.button("❌ Delete", key=f"del_{idx}"):
                        st.session_state.history.remove(item)
                        st.rerun()
else:
    if not generate:
        st.info("👆 Select a mode, upload or enter a prompt, then click **Generate / Apply Design**.")

# ====== FOOTER ======
st.markdown("---")
st.caption("Gesner Deslandes, Technology Coordinator at Be Like Brit Summer Project 2026")
st.caption("📞 (509) 4738-5663 | 📧 deslandes78@gmail.com")
