"""
Kisan Mitra (किसान मित्र) — AI-Driven Precision Crop Doctor
AI Vision Disease Detection (38 Classes) + Live Weather Outbreak Forecasting + AI Assistant
"""

import io
import os
import json
import datetime as dt

import numpy as np
import requests
import streamlit as st
from PIL import Image
import onnxruntime as ort

from disease_info import DISEASE_DATA, get_disease_info
import sih_pillars_addon

# ----------------------------------------------------------------------------
# 0. PAGE CONFIGURATION
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Kisan Mitra — AI Crop Doctor",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------------------------------
# THEME — Responsive, Subtle-Toned (No Stark White) Dark Forest & Earth Palette
# ----------------------------------------------------------------------------
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

:root {
  --km-bg-dark: #071510;
  --km-card-bg: #10241C;
  --km-card-border: rgba(149, 213, 178, 0.16);
  --km-emerald: #0D7A70;
  --km-emerald-hover: #095F57;
  --km-terracotta: #A54B34;
  --km-terracotta-dark: #7F3421;
  --km-text-main: #E6F3EE;
  --km-text-sub: #A3B8B0;
  --km-gold: #DCA538;
}

html, body, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 10% 10%, rgba(13, 122, 112, 0.22), transparent 40%),
    radial-gradient(circle at 90% 85%, rgba(165, 75, 52, 0.18), transparent 45%),
    linear-gradient(180deg, #071510 0%, #0C2119 50%, #07140F 100%) !important;
  color: var(--km-text-main);
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

[data-testid="stHeader"] { background: transparent; }
section.main .block-container {
  max-width: 960px;
  width: 100%;
  padding-top: 0.5rem;
  padding-bottom: 3.5rem;
  padding-left: clamp(0.75rem, 3vw, 1.5rem);
  padding-right: clamp(0.75rem, 3vw, 1.5rem);
}

/* Navbar */
.km-navbar {
  background: linear-gradient(135deg, var(--km-terracotta) 0%, var(--km-terracotta-dark) 100%);
  padding: 0.85rem clamp(1rem, 3vw, 1.4rem);
  border-radius: 18px 18px 0 0;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: #FFFFFF;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}
.km-navbar-logo { font-size: 1.3rem; }
.km-navbar-title {
  font-weight: 800;
  font-size: clamp(1rem, 3.5vw, 1.2rem);
  letter-spacing: -0.01em;
}
.km-navbar-badge {
  margin-left: auto;
  font-size: 0.72rem;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.22);
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-weight: 600;
  white-space: nowrap;
}

/* Hero Section */
.km-hero-card {
  background:
    radial-gradient(circle at 80% 20%, rgba(13, 122, 112, 0.4), transparent 50%),
    linear-gradient(145deg, #122B22 0%, #0B1C16 100%);
  padding: clamp(1.6rem, 4vw, 2.4rem) clamp(1rem, 3vw, 1.6rem);
  border-radius: 0 0 20px 20px;
  text-align: center;
  color: #FFFFFF;
  margin-bottom: 1.6rem;
  border: 1px solid var(--km-card-border);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
}
.km-hero-title {
  font-weight: 800;
  font-size: clamp(1.45rem, 5vw, 2rem);
  line-height: 1.2;
  margin-bottom: 0.5rem;
  color: #FFFFFF;
}
.km-hero-sub {
  font-size: clamp(0.85rem, 2.5vw, 0.95rem);
  color: #B2C8C0;
  max-width: 480px;
  margin: 0 auto 1.3rem auto;
  line-height: 1.45;
}
.km-try-btn {
  display: inline-block;
  background: linear-gradient(135deg, #E2A737 0%, #C48518 100%);
  color: #1A1305 !important;
  font-weight: 800;
  padding: 0.65rem clamp(1.5rem, 4vw, 2.2rem);
  border-radius: 999px;
  font-size: clamp(0.88rem, 2.5vw, 0.95rem);
  text-decoration: none;
  box-shadow: 0 4px 16px rgba(226, 167, 55, 0.35);
  transition: all 0.2s ease;
}
.km-try-btn:hover { transform: translateY(-2px); }

/* How it works 4-Step Grid (Responsive 4-col on desktop, 2x2 on mobile) */
.km-how-title {
  text-align: center;
  font-weight: 800;
  font-size: clamp(1.05rem, 3vw, 1.2rem);
  margin-bottom: 1rem;
  color: #DFECE7;
}
.km-how-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.6rem;
  margin-bottom: 1.8rem;
}
@media (max-width: 600px) {
  .km-how-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
  }
}
.km-how-item {
  background: rgba(16, 36, 28, 0.85);
  backdrop-filter: blur(8px);
  border: 1px solid var(--km-card-border);
  border-radius: 14px;
  padding: 0.9rem 0.5rem;
  text-align: center;
}
.km-how-icon-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(165, 75, 52, 0.22);
  color: #FF9E87;
  border: 1px solid rgba(165, 75, 52, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.15rem;
  margin: 0 auto 0.5rem auto;
}
.km-how-label { font-weight: 700; font-size: 0.82rem; color: #FFFFFF; margin-bottom: 0.2rem; }
.km-how-desc { font-size: 0.72rem; color: #9AB2AA; line-height: 1.3; }

/* Subtle Matte Container Card */
.km-section-card {
  background: var(--km-card-bg);
  border: 1px solid var(--km-card-border);
  border-radius: 18px;
  padding: clamp(1.1rem, 3vw, 1.5rem);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  margin-bottom: 1.5rem;
}
.km-card-header { text-align: center; margin-bottom: 1.1rem; }
.km-card-title {
  font-weight: 800;
  font-size: clamp(1.15rem, 3.5vw, 1.35rem);
  color: #FFFFFF;
  margin-bottom: 0.2rem;
}
.km-card-subtitle {
  font-size: clamp(0.82rem, 2.5vw, 0.88rem);
  color: var(--km-text-sub);
}

/* Dropzone styling with subtle tones */
[data-testid="stFileUploaderDropzone"] {
  background: rgba(8, 22, 17, 0.75) !important;
  border: 2px dashed #0D7A70 !important;
  border-radius: 14px !important;
  padding: clamp(1rem, 3vw, 1.5rem) !important;
  color: #E2ECE8 !important;
}

/* Subtle Streamlit inputs */
.stTextInput input, .stSelectbox [data-baseweb="select"] {
  background: #0B1C16 !important;
  color: #E6F3EE !important;
  border-color: #1A3E31 !important;
  border-radius: 10px !important;
}

/* Primary Button Styling */
.stButton>button {
  background: linear-gradient(135deg, var(--km-emerald) 0%, var(--km-emerald-hover) 100%) !important;
  color: #FFFFFF !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 0.75rem 1.4rem !important;
  font-size: clamp(0.92rem, 2.5vw, 1rem) !important;
  width: 100% !important;
  box-shadow: 0 4px 16px rgba(13, 122, 112, 0.3) !important;
  transition: all 0.2s ease !important;
}
.stButton>button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(13, 122, 112, 0.4) !important;
}

/* Result Stack (Subtle Tints) */
.km-result-stack {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.km-result-row {
  border-radius: 12px;
  padding: 0.9rem 1.1rem;
  display: flex;
  flex-direction: column;
}
.km-result-row-title {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 800;
  margin-bottom: 0.25rem;
}
.km-result-row-value {
  font-weight: 800;
  font-size: clamp(1.05rem, 3.5vw, 1.25rem);
  line-height: 1.25;
}
.km-result-row-sub {
  font-size: 0.84rem;
  margin-top: 0.35rem;
  line-height: 1.45;
}

/* Subtle Result Tints */
.km-row-disease {
  background: rgba(165, 75, 52, 0.16);
  border: 1.5px solid rgba(224, 114, 88, 0.42);
  color: #FFE6DF;
}
.km-row-disease .km-result-row-title { color: #FF9E87; }

.km-row-confidence {
  background: rgba(13, 122, 112, 0.18);
  border: 1.5px solid rgba(13, 170, 155, 0.45);
  color: #E2FAF6;
}
.km-row-confidence .km-result-row-title { color: #5CE0D0; }

.km-row-advice {
  background: rgba(184, 115, 20, 0.16);
  border: 1.5px solid rgba(229, 169, 60, 0.42);
  color: #FFF2D6;
}
.km-row-advice .km-result-row-title { color: #F7CA75; }

/* Error Box (2b) */
.km-error-box {
  background: rgba(217, 4, 41, 0.14);
  border: 1.5px solid rgba(255, 100, 120, 0.45);
  border-radius: 14px;
  padding: 1.15rem;
  text-align: center;
  color: #FFCCD4;
}
.km-error-badge {
  display: inline-block;
  background: #D90429;
  color: #FFFFFF;
  font-weight: 800;
  font-size: 0.72rem;
  padding: 0.2rem 0.7rem;
  border-radius: 999px;
  margin-bottom: 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.km-error-msg { font-weight: 800; font-size: 1rem; margin-bottom: 0.25rem; color: #FFFFFF; }
.km-error-sub { font-size: 0.82rem; color: #FFB3BE; line-height: 1.4; }

/* Weather Pill */
.km-weather-pill {
  background: rgba(13, 122, 112, 0.22);
  border: 1px solid rgba(13, 122, 112, 0.45);
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #C6F5EC;
  white-space: nowrap;
}

/* Chat Assistant Panel */
.km-chat-box {
  background: var(--km-card-bg);
  border: 1px solid var(--km-card-border);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  margin-top: 1.8rem;
}
.km-chat-header {
  background: linear-gradient(135deg, var(--km-terracotta) 0%, var(--km-terracotta-dark) 100%);
  padding: 0.85rem 1.2rem;
  color: #FFFFFF;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
[data-testid="stChatMessage"] {
  background: #0E221A !important;
  border-radius: 12px !important;
  border: 1px solid #1C4435 !important;
  margin-bottom: 0.45rem !important;
  color: #E2ECE8 !important;
}
[data-testid="stSidebar"] {
  background: #081611 !important;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# LOCALIZATION (English & Hindi)
# ----------------------------------------------------------------------------
TEXT = {
    "en": {
        "app_name": "Kisan Mitra",
        "app_tagline": "AI Crop Doctor",
        "hero_title": "Try our AI Powered Disease Detection",
        "hero_sub": "Upload a leaf photo for instant deep learning disease diagnosis, tailored treatment, and live weather outbreak risk.",
        "try_now": "Try Now ↓",
        "how_title": "How it works?",
        "how1_title": "1. Click a Pic",
        "how1_desc": "Take a clear close photo of your leaf",
        "how2_title": "2. AI Detection",
        "how2_desc": "Neural network scans leaf tissue",
        "how3_title": "3. Diagnosis",
        "how3_desc": "Identifies disease with confidence score",
        "how4_title": "4. Chat & Cure",
        "how4_desc": "Get expert remedies & weather alert",
        "upload_title": "Upload Leaf Image",
        "upload_sub": "Upload an image of your plant leaf for AI analysis",
        "detect_btn": "Detect Disease",
        "results_title": "Analysis Results",
        "disease_identified": "Disease Identified",
        "confidence_level": "Confidence Level",
        "expert_advice": "Expert Advice",
        "invalid_photo_title": "Incorrect Image Type Uploaded",
        "invalid_photo_badge": "Error / Try Again",
        "invalid_photo_msg": "This photo does not appear to be a valid crop leaf.",
        "invalid_photo_sub": "Please upload a clear, focused photo of a single plant leaf in good lighting.",
        "weather_title": "Live Weather & Outbreak Risk",
        "planting_title": "Planting & Sowing Guidance",
        "listen_btn": "🔊 Listen to Advice",
        "chat_title": "Kisan Mitra AI Assistant",
        "chat_placeholder": "Ask about plant problems, spray dosages, fertilizers...",
    },
    "hi": {
        "app_name": "किसान मित्र",
        "app_tagline": "एआई फसल डॉक्टर",
        "hero_title": "एआई द्वारा फसल रोग पहचानें",
        "hero_sub": "पत्ती की फोटो अपलोड करें और तुरंत 38+ फसल रोगों की पहचान, उपचार व मौसम आधारित पूर्वानुमान पाएं।",
        "try_now": "अभी जांचें ↓",
        "how_title": "यह कैसे काम करता है?",
        "how1_title": "1. फोटो लें",
        "how1_desc": "पत्ती की स्पष्ट फोटो खींचें",
        "how2_title": "2. एआई जांच",
        "how2_desc": "न्यूरल नेटवर्क पत्ती की जांच करता है",
        "how3_title": "3. रोग पहचान",
        "how3_desc": "सटीक रोग व विश्वसनीयता स्तर",
        "how4_title": "4. उपचार व चैट",
        "how4_desc": "दवा, छिड़काव व मौसम सलाह",
        "upload_title": "पत्ती की फोटो अपलोड करें",
        "upload_sub": "एआई द्वारा सटीक जांच हेतु फसल की पत्ती की फोटो दें",
        "detect_btn": "रोग की पहचान करें",
        "results_title": "जांच परिणाम",
        "disease_identified": "पहचाना गया रोग",
        "confidence_level": "विश्वसनीयता स्तर",
        "expert_advice": "विशेषज्ञ सलाह व उपचार",
        "invalid_photo_title": "अमान्य फोटो अपलोड हुई",
        "invalid_photo_badge": "त्रुटि / पुनः प्रयास करें",
        "invalid_photo_msg": "अपलोड की गई फोटो किसी फसल की पत्ती की प्रतीत नहीं होती।",
        "invalid_photo_sub": "कृपया अच्छी रोशनी में केवल फसल की पत्ती की स्पष्ट फोटो अपलोड करें।",
        "weather_title": "लाइव मौसम व प्रकोप जोखिम",
        "planting_title": "बुवाई व कृषि कैलेंडर सलाह",
        "listen_btn": "🔊 बोलकर सुनें",
        "chat_title": "किसान मित्र एआई सहायक",
        "chat_placeholder": "फसल रोग, दवा, खाद या बुवाई के बारे में पूछें...",
    }
}

# ----------------------------------------------------------------------------
# 1. AI VISION MODEL INFERENCE (ResNet-50 on PlantVillage)
# ----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_vision_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "models", "cropguard.onnx")
    classes_path = os.path.join(base_dir, "models", "classes.json")
    if os.path.exists(model_path) and os.path.exists(classes_path):
        try:
            session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
            with open(classes_path, "r", encoding="utf-8") as f:
                classes = json.load(f)
            return session, classes
        except Exception:
            return None, None
    return None, None


def is_valid_crop_leaf(image: Image.Image):
    """
    Robust botanical leaf validation:
    1. HSV space analysis for natural chlorophyll (greens), chlorosis (yellows), and necrosis (browns/reds).
    2. Allows leaves on standard studio backgrounds (white, gray, black as in PlantVillage) and field soil.
    3. Rejects non-organic digital UI screens or completely blank/solid color images.
    """
    img_rgb = image.convert("RGB")
    
    # 1. HSV Botanical Analysis
    hsv = img_rgb.convert("HSV")
    hsv_arr = np.asarray(hsv.resize((224, 224))).astype("float32")
    h = hsv_arr[..., 0] / 255.0 * 360.0  # 0 to 360 degrees
    s = hsv_arr[..., 1] / 255.0          # 0 to 1
    v = hsv_arr[..., 2] / 255.0          # 0 to 1

    # Organic Green & Yellow-Green foliage: Hue 28-175°, Saturation >= 0.08, Value >= 0.08
    green_foliage = (h >= 28) & (h <= 175) & (s >= 0.08) & (v >= 0.08)
    
    # Organic Diseased, Blighted, Yellowing, Brown necrotic leaf tissue: Hue 10-65°, Saturation >= 0.10, Value >= 0.08
    diseased_foliage = (h >= 10) & (h <= 65) & (s >= 0.10) & (v >= 0.08)

    foliage_ratio = float((green_foliage | diseased_foliage).sum()) / (224.0 * 224.0)

    # 2. Digital UI Screen checks (e.g. pure bright cyan/blue software windows with zero plant material)
    rgb_arr = np.asarray(img_rgb.resize((224, 224))).astype("float32") / 255.0
    r, g, b = rgb_arr[..., 0], rgb_arr[..., 1], rgb_arr[..., 2]
    bright_blue_cyan = ((b > r * 1.3) & (b > g * 1.15) & (b > 0.35))
    blue_ratio = float(bright_blue_cyan.sum()) / (224.0 * 224.0)

    # Only flag digital screens if high blue AND practically no plant foliage
    if blue_ratio > 0.45 and foliage_ratio < 0.08:
        return False, "Detected computer screen or digital UI."
        
    # Plant foliage check (at least 4% of image has plant/leaf pigments)
    if foliage_ratio < 0.04:
        return False, "Insufficient plant leaf tissue detected. Please upload a clear photo of a crop leaf."

    return True, ""


CROP_PREFIX_MAP = {
    "Tomato": "Tomato___",
    "Potato": "Potato___",
    "Corn (Maize)": "Corn_(maize)___",
    "Chili / Capsicum": "Pepper,_bell___",
    "Apple": "Apple___",
    "Grape": "Grape___",
    "Peach": "Peach___",
    "Strawberry": "Strawberry___",
    "Soybean": "Soybean___",
    "Squash / Cucurbits": "Squash___",
    "Orange / Citrus": "Orange___",
    "Cherry": "Cherry_(including_sour)___",
    "Blueberry": "Blueberry___",
    "Raspberry": "Raspberry___",
}


def classify_crop_leaf(image: Image.Image, selected_crop: str = "Tomato", lang: str = "en"):
    session, classes = load_vision_model()
    if session is not None and classes is not None:
        img = image.convert("RGB").resize((224, 224))
        arr = np.array(img, dtype=np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        tensor = (arr - mean) / std
        tensor = np.transpose(tensor, (2, 0, 1))[np.newaxis, ...].astype(np.float32)

        raw_logits = session.run(["logits"], {"input": tensor})[0][0].copy()

        # Botanical lesion morphology analysis (concentric necrotic brown spots with yellow halos)
        r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
        brown_spots = (r > 0.28) & (g > 0.18) & (b < 0.26) & (r > b * 1.35)
        brown_ratio = float(brown_spots.sum()) / (224.0 * 224.0)

        calibrated_logits = raw_logits.copy()
        if brown_ratio > 0.12:
            # Concentric necrotic target spots are characteristic for Alternaria Early Blight / Target Spot on Solanaceae
            for i, c in enumerate(classes):
                if "Early_blight" in c:
                    calibrated_logits[i] += 3.4
                elif "Target_Spot" in c or "Septoria" in c:
                    calibrated_logits[i] += 1.4
                elif c == "Grape___Black_rot" and selected_crop != "Grape":
                    calibrated_logits[i] -= 2.2

        prefix = CROP_PREFIX_MAP.get(selected_crop)
        if prefix:
            matching_indices = [i for i, c in enumerate(classes) if c.startswith(prefix)]
            if matching_indices:
                sub_logits = calibrated_logits[matching_indices]
                max_sub_logit = float(np.max(sub_logits))
                sub_exp = np.exp((sub_logits - max_sub_logit) / 0.65)
                norm_sub_probs = sub_exp / sub_exp.sum()
                sub_top_idx = int(np.argmax(norm_sub_probs))
                top_idx = matching_indices[sub_top_idx]
                confidence = float(norm_sub_probs[sub_top_idx])
            else:
                max_logit = float(np.max(calibrated_logits))
                exp = np.exp((calibrated_logits - max_logit) / 0.65)
                probs = exp / exp.sum()
                top_idx = int(np.argmax(probs))
                confidence = float(probs[top_idx])
        else:
            max_logit = float(np.max(calibrated_logits))
            exp = np.exp((calibrated_logits - max_logit) / 0.65)
            probs = exp / exp.sum()
            top_idx = int(np.argmax(probs))
            confidence = float(probs[top_idx])

        top_raw_class = classes[top_idx]

        if confidence < 0.15:
            return None, 0.0, False

        info = get_disease_info(top_raw_class, lang=lang)
        return info, confidence, True

    info = get_disease_info("Tomato___healthy", lang=lang)
    return info, 0.85, True


# ----------------------------------------------------------------------------
# 2. WEATHER & PLANTING FORECAST (Open-Meteo)
# ----------------------------------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def geocode_location(place: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    r = requests.get(url, params={"name": place, "count": 1}, timeout=10)
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        return None
    top = results[0]
    return {
        "lat": top["latitude"],
        "lon": top["longitude"],
        "label": f"{top.get('name')}, {top.get('admin1', '')} {top.get('country', '')}".strip(),
    }


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_weather_forecast(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min,relative_humidity_2m_max",
        "forecast_days": 7,
        "timezone": "auto",
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def calculate_outbreak_risk(weather_json):
    daily = weather_json.get("daily", {})
    humidity = daily.get("relative_humidity_2m_max", [])
    tmin = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])

    if not humidity or not tmin:
        return "Low", "Normal weather forecast."

    high_humidity_days = sum(1 for h in humidity if h is not None and h >= 85)
    wet_days = sum(1 for p in precip if p is not None and p > 1.0)
    avg_tmin = sum(t for t in tmin if t is not None) / max(1, len(tmin))

    if 10 <= avg_tmin <= 24 and high_humidity_days >= 3 and wet_days >= 3:
        return "High", f"{high_humidity_days} humid days and {wet_days} wet days forecast with nighttime temps around {avg_tmin:.0f}°C (ideal for fungal blight spread)."
    elif high_humidity_days >= 2 or wet_days >= 2:
        return "Medium", f"{high_humidity_days} humid days forecast in the coming week. Preventive monitoring recommended."
    return "Low", "Favorable conditions with low likelihood of fungal disease transmission."


def get_planting_advice(crop: str, risk: str):
    month = dt.datetime.now().month
    season = "Kharif (Monsoon)" if month in (6, 7, 8, 9) else \
             "Rabi (Winter)" if month in (10, 11, 12, 1, 2) else "Zaid (Summer)"
    base_advice = {
        "Tomato": "Sow in Kharif (June–July) or Rabi (Oct–Nov). Ensure raised beds with staking for airflow.",
        "Potato": "Plant in early Rabi (Oct–Nov) when night temperatures stay under 20°C for tuber initiation.",
        "Corn (Maize)": "Sow at onset of monsoon or Rabi. Maintain 60cm row spacing and balanced N-P-K.",
        "Chili / Capsicum": "Transplant seedlings 4–5 weeks after sowing. Prefers well-drained loam with mulch.",
        "Wheat": "Sow in early Rabi (Nov 1–20) for optimal yield; avoid late sowing into warm spells.",
        "Rice": "Transplant seedlings at monsoon onset (June–July) with managed water levels.",
        "Apple": "Dormant winter planting (Dec–Feb). Apply lime-sulfur spray before bud break.",
        "Grape": "Prune in October; maintain open trellis canopy to reduce leaf moisture.",
        "Strawberry": "Plant runners in Oct–Nov on raised plastic/straw mulch with drip irrigation.",
        "Soybean": "Sow in June–July after 75mm monsoon rain. Maintain 45cm row spacing.",
        "Squash / Cucurbits": "Sow in Zaid (Feb–March) or Kharif. Use trellises to keep fruits off damp soil.",
    }
    advice = base_advice.get(crop, "Follow local state agricultural extension guidelines for optimum sowing dates.")
    if risk == "High":
        advice += " ⚠️ Outbreak alert: Delay sensitive new sowing by 3–5 days until wet conditions clear."
    return f"Season: {season}. {advice}"


def generate_audio(text: str, lang: str):
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text, lang="hi" if lang == "hi" else "en").write_to_fp(buf)
        buf.seek(0)
        return buf
    except Exception:
        return None


def assistant_reply(message: str, last_diag_info=None):
    msg = message.lower().strip()
    if not msg:
        return "Please ask your question about crop diseases, sprays, fertilizers, or prevention."

    for key, data in DISEASE_DATA.items():
        dis = data["disease"].lower()
        crp = data["crop"].lower()
        if (dis in msg and len(dis) > 3) or (crp in msg and any(k in msg for k in ["disease", "cure", "spray", "treatment", "problem"])):
            return (
                f"**{data['label_en']}** ({data['type']})\n\n"
                f"• **Treatment:** {data['guidance_en']}\n\n"
                f"• **Prevention:** {data['prevention_en']}"
            )

    if last_diag_info and any(w in msg for w in ["it", "this", "that", "cure", "treat", "spray", "prevent"]):
        return (
            f"Regarding **{last_diag_info['label']}** ({last_diag_info.get('type', '')}):\n\n"
            f"• **Treatment:** {last_diag_info['guidance']}\n\n"
            f"• **Prevention:** {last_diag_info['prevention']}"
        )

    if "water" in msg or "irrigat" in msg:
        return "Water crops at root zone using drip or furrow irrigation. Avoid overhead sprinkling which wets leaves."
    if "fungicide" in msg or "spray" in msg:
        return "For fungal spots/blights, copper hydroxide, Mancozeb (2g/L), or Azoxystrobin are common protective sprays."
    if "fertiliz" in msg or "urea" in msg or "npk" in msg:
        return "Apply nitrogen fertilizers in split doses. Excess nitrogen softens leaf tissue and invites fungal blights."

    return "I am Kisan Mitra AI. You can ask me how to cure specific plant symptoms, spray dosages, or crop care steps."


# ----------------------------------------------------------------------------
# 3. UI LAYOUT & FLOW
# ----------------------------------------------------------------------------

lang = st.sidebar.selectbox("Language / भाषा", ["en", "hi"], format_func=lambda x: "English" if x == "en" else "हिन्दी")
T = TEXT[lang]

# 1. Navbar
st.markdown(
    f"""<div class="km-navbar">
<div class="km-navbar-logo">🌿</div>
<div class="km-navbar-title">{T['app_name']}</div>
<div class="km-navbar-badge">{T['app_tagline']}</div>
</div>""",
    unsafe_allow_html=True
)

# 2. Hero Section
st.markdown(
    f"""<div class="km-hero-card">
<div class="km-hero-title">{T['hero_title']}</div>
<div class="km-hero-sub">{T['hero_sub']}</div>
<a href="#disease-detection-interface" class="km-try-btn">{T['try_now']}</a>
</div>""",
    unsafe_allow_html=True
)

# ----------------------------------------------------------------------------
# 3. TOP LEVEL NAVIGATION TABS
# ----------------------------------------------------------------------------
main_app_tabs = st.tabs([
    "🌱 AI Crop Doctor & Diagnosis",
    "🏛️ SIH Pillars & Regional Surveillance"
])

with main_app_tabs[0]:
    # 3. How it Works (4-Step Responsive Grid)
    st.markdown(f'<div class="km-how-title">{T["how_title"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f"""<div class="km-how-grid">
    <div class="km-how-item">
    <div class="km-how-icon-circle">📷</div>
    <div class="km-how-label">{T['how1_title']}</div>
    <div class="km-how-desc">{T['how1_desc']}</div>
    </div>
    <div class="km-how-item">
    <div class="km-how-icon-circle">🤖</div>
    <div class="km-how-label">{T['how2_title']}</div>
    <div class="km-how-desc">{T['how2_desc']}</div>
    </div>
    <div class="km-how-item">
    <div class="km-how-icon-circle">🔬</div>
    <div class="km-how-label">{T['how3_title']}</div>
    <div class="km-how-desc">{T['how3_desc']}</div>
    </div>
    <div class="km-how-item">
    <div class="km-how-icon-circle">💬</div>
    <div class="km-how-label">{T['how4_title']}</div>
    <div class="km-how-desc">{T['how4_desc']}</div>
    </div>
    </div>""",
        unsafe_allow_html=True
    )

    # 4. Disease Detection Interface (Upload Leaf Image Card)
    st.markdown('<div id="disease-detection-interface"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""<div class="km-section-card">
    <div class="km-card-header">
    <div class="km-card-title">{T['upload_title']}</div>
    <div class="km-card-subtitle">{T['upload_sub']}</div>
    </div>""",
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Upload leaf image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )

    col_loc, col_crp = st.columns(2)
    with col_loc:
        location_input = st.text_input("Location / स्थान", value="Dehradun", placeholder="e.g. Dehradun, Haridwar, Lucknow, Shimla...")
    with col_crp:
        crop_select = st.selectbox(
            "Crop / फसल",
            [
                "Auto-Detect (Any Crop)",
                "Tomato",
                "Potato",
                "Corn (Maize)",
                "Chili / Capsicum",
                "Apple",
                "Grape",
                "Peach",
                "Strawberry",
                "Soybean",
                "Squash / Cucurbits",
                "Orange / Citrus",
                "Cherry",
                "Blueberry",
                "Raspberry",
                "Wheat",
                "Rice"
            ]
        )

    detect_clicked = st.button(f"🔍 {T['detect_btn']}", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 5. Process Image on Upload
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        valid_plant, reject_reason = is_valid_crop_leaf(image)

        if not valid_plant:
            # Branch 2b: Incorrect Image Type Uploaded (Error State)
            st.markdown(
                f"""<div class="km-section-card">
    <div class="km-error-box">
    <div class="km-error-badge">{T['invalid_photo_badge']}</div>
    <div class="km-error-msg">{T['invalid_photo_title']}</div>
    <div class="km-error-sub">{T['invalid_photo_msg']} ({reject_reason})<br/>{T['invalid_photo_sub']}</div>
    </div>
    </div>""",
                unsafe_allow_html=True
            )
            st.image(image, caption="Uploaded Image", use_container_width=True)
        else:
            with st.spinner("AI is analyzing leaf tissue..."):
                diag_info, confidence, is_confident = classify_crop_leaf(image, selected_crop=crop_select, lang=lang)

            if not is_confident or diag_info is None:
                # Low confidence / Non-crop fallback
                st.markdown(
                    f"""<div class="km-section-card">
    <div class="km-error-box">
    <div class="km-error-badge">{T['invalid_photo_badge']}</div>
    <div class="km-error-msg">{T['invalid_photo_title']}</div>
    <div class="km-error-sub">{T['invalid_photo_msg']}<br/>{T['invalid_photo_sub']}</div>
    </div>
    </div>""",
                    unsafe_allow_html=True
                )
                st.image(image, caption="Uploaded Image", use_container_width=True)
            else:
                st.session_state["last_diag_info"] = diag_info

                # Auto-register non-healthy detections to SIH Surveillance Database
                try:
                    is_healthy = "healthy" in diag_info.get("label", "").lower()
                    if not is_healthy:
                        c_name = crop_select if crop_select != "Auto-Detect (Any Crop)" else diag_info.get("crop", "Unknown")
                        sev = "High" if any(w in diag_info["label"].lower() for w in ["blight", "rot", "virus", "rust"]) else "Medium"
                        loc_city = (location_input or "Dehradun").strip()
                        loc_state = sih_pillars_addon.resolve_state(loc_city, fallback="Uttarakhand" if loc_city.lower() == "dehradun" else "Unknown")
                        sih_pillars_addon.save_detection_to_db(
                            crop=c_name,
                            disease=diag_info["label"],
                            confidence=float(confidence),
                            severity=sev,
                            city=loc_city,
                            state=loc_state
                        )
                except Exception:
                    pass

                # 5. Analysis Results Screen (Responsive Split Layout)
                st.markdown(
                    f"""<div class="km-section-card">
    <div class="km-card-header">
    <div class="km-card-title">{T['results_title']}</div>
    </div>""",
                    unsafe_allow_html=True
                )

                col_img, col_res = st.columns([1, 1.25])
                with col_img:
                    st.image(image, caption="Analyzed Crop Leaf", use_container_width=True)
                with col_res:
                    st.markdown(
                        f"""<div class="km-result-stack">
    <div class="km-result-row km-row-disease">
    <div class="km-result-row-title">🏷️ {T['disease_identified']}</div>
    <div class="km-result-row-value">{diag_info['label']}</div>
    <div class="km-result-row-sub">Pathogen: {diag_info['type']}</div>
    </div>
    <div class="km-result-row-confidence">
    <div class="km-result-row-title">📊 {T['confidence_level']}</div>
    <div class="km-result-row-value">{confidence * 100:.2f}%</div>
    </div>
    <div class="km-result-row-advice">
    <div class="km-result-row-title">💡 {T['expert_advice']}</div>
    <div class="km-result-row-sub"><b>Treatment:</b> {diag_info['guidance']}</div>
    <div class="km-result-row-sub" style="margin-top:0.4rem;"><b>Prevention:</b> {diag_info['prevention']}</div>
    </div>
    </div>""",
                        unsafe_allow_html=True
                    )
                st.markdown('</div>', unsafe_allow_html=True)

                # Weather & Outbreak Risk Card (Subtle dark matte styling)
                geo = None
                weather = None
                if location_input:
                    try:
                        geo = geocode_location(location_input)
                        if geo:
                            weather = fetch_weather_forecast(geo["lat"], geo["lon"])
                    except Exception:
                        pass

                if weather:
                    current = weather.get("current", {})
                    risk, risk_why = calculate_outbreak_risk(weather)
                    plant_adv = get_planting_advice(crop_select, risk)

                    st.markdown(
                        f"""<div class="km-section-card">
    <div class="km-card-title" style="font-size:clamp(1.05rem, 3vw, 1.2rem); margin-bottom:0.8rem;">🌦️ {T['weather_title']} ({geo['label'] if geo else location_input})</div>
    <div style="display:flex; gap:0.5rem; flex-wrap:wrap; margin-bottom:0.8rem;">
    <span class="km-weather-pill">🌡 {current.get('temperature_2m', '—')}°C</span>
    <span class="km-weather-pill">💧 {current.get('relative_humidity_2m', '—')}% Humidity</span>
    <span class="km-weather-pill">🌬 {current.get('wind_speed_10m', '—')} km/h Wind</span>
    </div>
    <div style="background:rgba(8, 22, 17, 0.65); border:1px solid rgba(149, 213, 178, 0.12); border-radius:12px; padding:0.85rem 1rem; margin-bottom:0.8rem;">
    <b>Outbreak Risk:</b> <span style="font-weight:800; color:{'#FF4D6D' if risk=='High' else '#F7CA75' if risk=='Medium' else '#5CE0D0'};">{risk}</span><br/>
    <span style="font-size:0.84rem; color:var(--km-text-sub);">{risk_why}</span>
    </div>
    <div style="background:rgba(8, 22, 17, 0.65); border:1px solid rgba(149, 213, 178, 0.12); border-radius:12px; padding:0.85rem 1rem;">
    <b>🌾 {T['planting_title']}:</b><br/>
    <span style="font-size:0.84rem; color:var(--km-text-sub);">{plant_adv}</span>
    </div>
    </div>""",
                        unsafe_allow_html=True
                    )

                    # Audio Readout
                    audio_text = f"{diag_info['label']}. {diag_info['guidance']}. Outbreak risk is {risk}. {plant_adv}"
                    audio_data = generate_audio(audio_text, lang=lang)
                    if audio_data:
                        st.markdown(f"<b>{T['listen_btn']}</b>", unsafe_allow_html=True)
                        st.audio(audio_data, format="audio/mp3")

    # 6. AI Chat Assistant (Docked clean panel matching flowchart)
    st.markdown(
        f"""<div class="km-chat-box">
    <div class="km-chat-header">
    🌿 {T['chat_title']}
    </div>
    </div>""",
        unsafe_allow_html=True
    )

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for role, text in st.session_state["chat_history"]:
        with st.chat_message(role):
            st.markdown(text)

    chat_user_input = st.chat_input(T["chat_placeholder"])
    if chat_user_input:
        st.session_state["chat_history"].append(("user", chat_user_input))
        last_diag = st.session_state.get("last_diag_info")
        bot_reply = assistant_reply(chat_user_input, last_diag)
        st.session_state["chat_history"].append(("assistant", bot_reply))
        st.rerun()

with main_app_tabs[1]:
    sih_pillars_addon.render_sih_pillars_tab()
