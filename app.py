import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import random
import time
import urllib.parse
import os
import tempfile

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
    ["🎨 AI Generation (Text)", "🖼️ Upload Image", "🎬 Upload Video"],
    horizontal=True,
    index=0
)

st.markdown("---")

# ====== INPUT SECTION – CONDITIONAL BASED ON MODE ======
uploaded_image = None
uploaded_video = None
prompt = ""

if mode == "🎨 AI Generation (Text)":
    st.markdown("Describe your dream design – I'll bring it to life.")
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

# ====== NEW: LOGO OVERLAY (OPTIONAL) ======
st.markdown("### 🖼️ Logo Overlay (Optional)")
st.caption("Upload a logo or image to place in a corner. PNG with transparency works best.")
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
    """Returns path to a .ttf file for moviepy, or None."""
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

# ====== ORIGINAL GENERATION FUNCTIONS ======
def enhance_prompt(prompt):
    quality_keywords = "high quality, professional, detailed, 8k, sharp focus, vibrant colors"
    if not any(kw in prompt.lower() for kw in ["high quality", "professional", "detailed", "8k"]):
        prompt = f"{prompt}, {quality_keywords}"
    return prompt

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

def generate_image(prompt, width, height, style):
    style_map = {
        "Cinematic": "cinematic",
        "Anime": "anime",
        "Realistic": "realistic",
        "Cyberpunk": "cyberpunk",
        "Watercolor": "watercolor",
        "3D Render": "3d+render",
    }
    style_param = style_map.get(style, "")
    enhanced_prompt = enhance_prompt(prompt)
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
                if response.status_code == 200:
                    return Image.open(io.BytesIO(response.content))
                elif response.status_code == 404:
                    continue
                else:
                    st.warning(f"Attempt {attempt+1}: API returned {response.status_code}. Retrying...")
                    time.sleep(2)
            except requests.exceptions.Timeout:
                st.warning(f"Attempt {attempt+1}: Timeout. Retrying...")
                time.sleep(3)
            except Exception as e:
                st.warning(f"Attempt {attempt+1}: {e}. Retrying...")
                time.sleep(2)
    
    st.warning("Using placeholder gradient (API unavailable).")
    return create_placeholder_image(width, height)

def add_text_overlay(img, title, subtitle, title_size, subtitle_size, color, position):
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
    return img

def add_background(img, bg_color, output_size=(1200, 1200)):
    canvas = Image.new('RGB', output_size, bg_color)
    img_w, img_h = img.size
    x = (output_size[0] - img_w) // 2
    y = (output_size[1] - img_h) // 2
    canvas.paste(img, (x, y))
    return canvas

# ====== NEW: LOGO OVERLAY FOR IMAGES ======
def add_logo_overlay(img, logo_bytes, corner, size_percent):
    """
    Overlays a logo/image onto the given PIL Image.
    """
    if logo_bytes is None:
        return img
    try:
        logo = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
    except:
        st.warning("Could not open logo file. Skipping logo overlay.")
        return img

    img = img.copy()
    w, h = img.size
    # Resize logo based on canvas width
    logo_w = int(w * size_percent)
    logo_h = int(logo_w * (logo.height / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    padding = int(w * 0.02)  # 2% margin

    x, y = 0, 0
    if corner == "Top Left":
        x, y = padding, padding
    elif corner == "Top Right":
        x, y = w - logo_w - padding, padding
    elif corner == "Bottom Left":
        x, y = padding, h - logo_h - padding
    else:  # Bottom Right
        x, y = w - logo_w - padding, h - logo_h - padding

    # Paste with transparency if available
    if logo.mode == 'RGBA':
        img.paste(logo, (x, y), logo.split()[3])
    else:
        img.paste(logo, (x, y))
    return img

# ====== VIDEO PROCESSING (UPDATED WITH LOGO) ======
def process_video_with_overlay(video_file, title, subtitle, title_size, subtitle_size, color, position, logo_bytes, logo_corner, logo_size_percent):
    try:
        from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
    except ImportError:
        st.error("MoviePy is not installed. Please run: pip install moviepy")
        return None

    font_path = get_font_path()
    if font_path is None:
        st.error("No .ttf font found. Please upload a TrueType font (.ttf) file to the app folder for video text overlay.")
        return None

    # Save uploaded video to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_input:
        tmp_input.write(video_file.read())
        input_path = tmp_input.name

    try:
        clip = VideoFileClip(input_path)
        # Limit to 60 seconds to avoid memory issues
        if clip.duration > 60:
            st.warning(f"Video is {clip.duration:.1f}s long. Processing only the first 60 seconds.")
            clip = clip.subclip(0, 60)

        w, h = clip.size
        clips_to_composite = [clip]

        # Position mapping for text
        if position == "Top":
            txt_y = int(h * 0.08)
        elif position == "Bottom":
            txt_y = int(h * 0.70)
        else:
            txt_y = int(h * 0.28)

        y_offset = txt_y

        # ---- Add Title ----
        if title:
            title_clip = TextClip(
                title,
                fontsize=title_size,
                color=color,
                font=font_path,
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(w * 0.9, None)
            )
            title_clip = title_clip.set_position(('center', y_offset)).set_duration(clip.duration)
            clips_to_composite.append(title_clip)
            y_offset += title_clip.h + 25

        # ---- Add Subtitle ----
        if subtitle:
            sub_clip = TextClip(
                subtitle,
                fontsize=subtitle_size,
                color=color,
                font=font_path,
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(w * 0.9, None)
            )
            sub_clip = sub_clip.set_position(('center', y_offset)).set_duration(clip.duration)
            clips_to_composite.append(sub_clip)

        # ---- NEW: Add Logo ----
        if logo_bytes is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_logo:
                tmp_logo.write(logo_bytes)
                logo_path = tmp_logo.name
            try:
                logo_clip = ImageClip(logo_path).set_duration(clip.duration)
                logo_w = int(w * logo_size_percent)
                logo_h = int(logo_w * (logo_clip.h / logo_clip.w))
                logo_clip = logo_clip.resize(width=logo_w, height=logo_h)
                padding = int(w * 0.02)
                if logo_corner == "Top Left":
                    pos = (padding, padding)
                elif logo_corner == "Top Right":
                    pos = (w - logo_w - padding, padding)
                elif logo_corner == "Bottom Left":
                    pos = (padding, h - logo_h - padding)
                else:  # Bottom Right
                    pos = (w - logo_w - padding, h - logo_h - padding)
                logo_clip = logo_clip.set_position(pos).set_duration(clip.duration)
                clips_to_composite.append(logo_clip)
            except Exception as e:
                st.warning(f"Could not add logo to video: {e}")
            finally:
                if os.path.exists(logo_path):
                    os.unlink(logo_path)

        if len(clips_to_composite) == 1:
            st.warning("No title, subtitle, or logo to overlay. Returning original video.")
            return clip

        final_clip = CompositeVideoClip(clips_to_composite)
        # Write to temp output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_output:
            output_path = tmp_output.name

        final_clip.write_videofile(output_path, fps=clip.fps, codec='libx264', audio_codec='aac', verbose=False, logger=None)
        return output_path

    except Exception as e:
        st.error(f"Video processing error: {e}")
        return None
    finally:
        if os.path.exists(input_path):
            os.unlink(input_path)

# ====== MAIN GENERATION LOGIC ======
if generate:
    if mode == "🎨 AI Generation (Text)":
        if not prompt:
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("🎨 Creating your design..."):
                img = generate_image(prompt, width, height, style)
                if img:
                    if overlay_title or overlay_subtitle:
                        img = add_text_overlay(img, overlay_title, overlay_subtitle, title_font_size, subtitle_font_size, text_color, text_position)
                    # ---- NEW: apply logo ----
                    img = add_logo_overlay(img, uploaded_logo.read() if uploaded_logo else None, logo_corner, logo_size_percent)
                    
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

    elif mode == "🖼️ Upload Image":
        if uploaded_image is None:
            st.warning("Please upload an image first.")
        else:
            with st.spinner("🖼️ Applying design to your image..."):
                img = Image.open(uploaded_image)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                if overlay_title or overlay_subtitle:
                    img = add_text_overlay(img, overlay_title, overlay_subtitle, title_font_size, subtitle_font_size, text_color, text_position)
                # ---- NEW: apply logo ----
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

    elif mode == "🎬 Upload Video":
        if uploaded_video is None:
            st.warning("Please upload a video first.")
        else:
            with st.spinner("🎬 Processing video with overlays... This may take a moment."):
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
                    logo_size_percent
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
