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
    ["🎨 AI Generation (Text)", "🖼️ Upload Image", "🎬 Upload Video", "🎬 Slideshow (Multiple Clips)"],
    horizontal=True,
    index=0
)

st.markdown("---")

# ====== INPUT SECTION – CONDITIONAL ======
uploaded_image = None
uploaded_video = None
uploaded_files = None  # for slideshow
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

# ====== LOGO OVERLAY (OPTIONAL) ======
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

# ====== 🎵 BACKGROUND AUDIO (for video/slideshow modes) ======
# Only show this section if the mode is video or slideshow
if mode in ["🎬 Upload Video", "🎬 Slideshow (Multiple Clips)"]:
    st.markdown("### 🎵 Background Audio (Optional)")
    st.caption("Choose a preset sound or upload your own.")

    # Preset sound options
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

    # If "Custom" is selected, show file uploader
    custom_audio_upload = None
    if selected_sound == "Custom (upload your own)":
        custom_audio_upload = st.file_uploader(
            "Upload your audio (MP3/WAV/M4A)",
            type=["mp3", "wav", "m4a"],
            key="custom_audio_uploader"
        )
        if custom_audio_upload:
            st.success(f"✅ Audio loaded: {custom_audio_upload.name}")

    # Mute original audio checkbox
    mute_original_audio = st.checkbox("Mute original video audio (use background only)", value=True, key="mute_audio_video")

    st.markdown("---")

# ====== SLIDESHOW‑SPECIFIC SETTINGS (image duration) ======
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
    else:  # Bottom Right
        x, y = w - logo_w - padding, h - logo_h - padding

    if logo.mode == 'RGBA':
        img.paste(logo, (x, y), logo.split()[3])
    else:
        img.paste(logo, (x, y))
    return img

# ====== VIDEO PROCESSING (SINGLE) – UPDATED WITH AUDIO ======
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

def process_video_with_overlay(video_file, title, subtitle, title_size, subtitle_size, color, position,
                               logo_bytes, logo_corner, logo_size_percent,
                               audio_bytes=None, mute_original=True):
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

        # Text overlay
        text_pil = create_text_image_for_video(
            w, h, title, subtitle, title_size, subtitle_size, color, position
        )
        text_np = np.array(text_pil)
        text_clip = ImageClip(text_np).set_duration(clip.duration).set_position((0, 0))
        clips_to_composite.append(text_clip)

        # Logo overlay
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

        if len(clips_to_composite) == 1:
            st.warning("No title, subtitle, or logo to overlay. Returning original video.")
            return clip

        final_clip = CompositeVideoClip(clips_to_composite)

        # ---- Background audio ----
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
                
                if mute_original:
                    final_clip = final_clip.set_audio(bg_audio)
                else:
                    if final_clip.audio is not None:
                        orig_audio = final_clip.audio.volumex(0.3)
                        bg_audio = bg_audio.volumex(0.7)
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

# ====== SLIDESHOW FUNCTION (UPDATED) ======
def create_slideshow(uploaded_files, image_duration, audio_bytes, mute_original,
                     title, subtitle, title_size, subtitle_size, color, position,
                     logo_bytes, logo_corner, logo_size_percent):
    try:
        from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
    except ImportError:
        st.error("MoviePy is not installed. Please run: pip install moviepy")
        return None

    if not uploaded_files:
        st.warning("No files uploaded.")
        return None

    clips = []
    temp_paths = []

    for file_obj in uploaded_files:
        ext = os.path.splitext(file_obj.name)[1].lower()
        if ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(file_obj.read())
                tmp_path = tmp.name
            temp_paths.append(tmp_path)
            try:
                clip = VideoFileClip(tmp_path)
                clips.append(clip)
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
                clips.append(clip)
            except Exception as e:
                st.warning(f"Could not load image {file_obj.name}: {e}")
                continue
        else:
            st.warning(f"Unsupported file type: {file_obj.name}")

    if not clips:
        st.error("No valid clips to create slideshow.")
        return None

    # Resize all clips to target size (width, height from sidebar)
    target_w = width
    target_h = height
    resized_clips = []
    for clip in clips:
        if clip.size != (target_w, target_h):
            clip = clip.resize(width=target_w, height=target_h)
        resized_clips.append(clip)
    final_clip = concatenate_videoclips(resized_clips, method="compose")

    # ---- Background audio ----
    if audio_bytes is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            tmp_audio.write(audio_bytes)
            audio_path = tmp_audio.name
        temp_paths.append(audio_path)
        try:
            bg_audio = AudioFileClip(audio_path)
            if bg_audio.duration < final_clip.duration:
                bg_audio = bg_audio.loop(duration=final_clip.duration)
            else:
                bg_audio = bg_audio.subclip(0, final_clip.duration)
            
            if mute_original:
                final_clip = final_clip.set_audio(bg_audio)
            else:
                if final_clip.audio is not None:
                    orig_audio = final_clip.audio.volumex(0.3)
                    bg_audio = bg_audio.volumex(0.7)
                    mixed = CompositeAudioClip([orig_audio, bg_audio])
                    final_clip = final_clip.set_audio(mixed)
                else:
                    final_clip = final_clip.set_audio(bg_audio)
        except Exception as e:
            st.warning(f"Could not process background audio: {e}")

    # ---- Text overlay ----
    text_pil = create_text_image_for_video(target_w, target_h, title, subtitle, title_size, subtitle_size, color, position)
    text_np = np.array(text_pil)
    text_clip = ImageClip(text_np).set_duration(final_clip.duration).set_position((0, 0))
    overlays = [final_clip, text_clip]

    # ---- Logo overlay ----
    if logo_bytes is not None:
        try:
            logo_pil = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
            logo_w = int(target_w * logo_size_percent)
            logo_h = int(logo_w * (logo_pil.height / logo_pil.width))
            logo_pil = logo_pil.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            logo_np = np.array(logo_pil)
            logo_clip = ImageClip(logo_np).set_duration(final_clip.duration)
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

    # Write output
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_output:
        output_path = tmp_output.name

    fps = clips[0].fps if hasattr(clips[0], 'fps') and clips[0].fps else 24
    final_composite.write_videofile(
        output_path,
        fps=fps,
        codec='libx264',
        audio_codec='aac',
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

# ====== MAIN GENERATION LOGIC ======
if generate:
    # ----- Determine audio bytes for video/slideshow modes -----
    audio_bytes = None
    mute_audio = True  # default
    if mode in ["🎬 Upload Video", "🎬 Slideshow (Multiple Clips)"]:
        mute_audio = mute_original_audio if 'mute_original_audio' in locals() else True
        if selected_sound != "None":
            if selected_sound == "Custom (upload your own)":
                if custom_audio_upload:
                    audio_bytes = custom_audio_upload.read()
            else:
                # Download preset sound
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
                        img = add_text_overlay(img, overlay_title, overlay_subtitle, title_font_size, subtitle_font_size, text_color, text_position)
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
                    img = add_text_overlay(img, overlay_title, overlay_subtitle, title_font_size, subtitle_font_size, text_color, text_position)
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

    # ----- Upload Video (single) -----
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
                    mute_audio
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
            with st.spinner("🎬 Creating slideshow with audio..."):
                logo_bytes = uploaded_logo.read() if uploaded_logo else None
                output_path = create_slideshow(
                    uploaded_files,
                    image_duration,
                    audio_bytes,
                    mute_audio,
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
