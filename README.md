<div align="center">

# 🌿 Kisan Mitra (किसान मित्र)
### *AI-Driven Precision Crop Doctor & Regional Disease Surveillance Ecosystem*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![ONNX Runtime](https://img.shields.io/badge/ONNX_Runtime-Edge_AI-005CED?style=for-the-badge&logo=onnx&logoColor=white)](https://onnxruntime.ai)
[![License](https://img.shields.io/badge/License-MIT-16C196?style=for-the-badge)](LICENSE)
[![SIH](https://img.shields.io/badge/Smart_India_Hackathon-Prototype-DCA538?style=for-the-badge)](#)

<p align="center">
  <b>Bridging the gap between edge AI computer vision, localized weather forecasting, and grassroots agricultural extension systems to empower Indian farmers.</b>
</p>

[Quick Start](#-quick-start) • [Key Features](#-key-features) • [Architecture](#-system-architecture) • [38 Supported Crop Classes](#-supported-crops--diseases) • [SIH Pillars](#-smart-india-hackathon-strategic-pillars) • [Tech Stack](#-technology-stack)

</div>

---

## 📌 Executive Summary

Crop diseases cause **15% to 30% annual agricultural yield loss** in India, often exacerbated by delayed diagnosis, indiscriminate pesticide use, and a lack of regional outbreak intelligence.

**Kisan Mitra** is an end-to-end precision agri-tech platform that combines:
1. **Instant On-Device AI Vision** (38 crop-disease classes running on low-latency ONNX Runtime).
2. **Microclimate Outbreak Risk Forecasting** (7-day predictive epidemiological modeling via Open-Meteo).
3. **Regional Geospatial Surveillance & Hotspot Mapping** for district agricultural officers.
4. **Plant Pathologist Verification Queue & KVK Referral Network**.
5. **Chemical Safety Guardrails** with Pre-Harvest Interval (PHI) calculators to prevent toxic residues.

---

## 🚀 Key Features

```
                                    ┌────────────────────────┐
                                    │  Farmer Uploads Leaf   │
                                    └───────────┬────────────┘
                                                │
                 ┌──────────────────────────────┴─────────────────────────────┐
                 ▼                                                            ▼
    ┌─────────────────────────┐                                  ┌─────────────────────────┐
    │  Deep Learning Vision   │                                  │  Live Microclimate API  │
    │  (38-Class ResNet ONNX) │                                  │  (7-Day Weather Matrix) │
    └────────────┬────────────┘                                  └────────────┬────────────┘
                 │                                                            │
                 └──────────────────────────────┬─────────────────────────────┘
                                                │
                                                ▼
                               ┌────────────────────────────────┐
                               │  Precision Diagnostic Engine   │
                               │  • Disease Identification      │
                               │  • Organic & Chemical Rx       │
                               │  • Pre-Harvest Interval (PHI)  │
                               │  • Outbreak Risk Forecast      │
                               └────────┬──────────────┬────────┘
                                        │              │
                    ┌───────────────────┘              └───────────────────┐
                    ▼                                                      ▼
     ┌─────────────────────────────┐                        ┌─────────────────────────────┐
     │  Farmer Advisory Portal     │                        │  Officials' Surveillance    │
     │  • Audio Read-Out (TTS)     │                        │  • Regional Hotspot Map     │
     │  • Multilingual (EN / HI)   │                        │  • KVK / Lab Referral Queue │
     │  • AI Agronomist Chatbot    │                        │  • CSV Outbreak Analytics   │
     └─────────────────────────────┘                        └─────────────────────────────┘
```

### 🔬 1. AI Vision Crop Doctor
- **38-Class Deep Learning Neural Network** (`models/cropguard.onnx`) for instant leaf pathology analysis.
- **Edge Inference:** Sub-second response time with optimized CPU inference (no GPU required).
- **Leaf Pre-validation Guard:** Heuristically rejects non-leaf/irrelevant uploads with explanatory feedback.

### 🌦️ 2. Predictive Outbreak Forecasting
- Real-time 7-day meteorological analysis (temperature, precipitation, relative humidity, dew point).
- Calculates disease infection probability score before symptoms spread across neighbouring farms.

### 🌐 3. Regional Hotspots & Proximity Alerts
- City-to-state automatic geolocation covering over 100+ Indian districts.
- Configurable radius radar ($5\text{ km} - 100\text{ km}$) warning farmers of confirmed nearby infections.

### 🏛️ 4. Agriculture Officials' Surveillance Portal
- Decision-support dashboard for District Agricultural Officers (DAOs).
- Aggregates high-severity trends, district-wise disease distributions, and one-click surveillance CSV exports.

### 🧪 5. Chemical Safety & PHI Guardrails
- **Pre-Harvest Interval (PHI) Calculator:** Calculates mandatory safe waiting days between spraying and harvest to eliminate dangerous chemical residues in market produce.
- **Dosage Calculator:** Computes exact chemical weight and water volume according to acreage.

### 👨‍🔬 6. Human-in-the-Loop Expert Review & KVK Network
- **Pathologist Verification Queue:** Allows ICAR / KVK agricultural scientists to confirm, correct, or refine AI diagnoses.
- **Pan-India KVK Directory:** Connects farmers to their nearest accredited diagnostic testing centers.

### 🗣️ 7. Multilingual Voice & AI Chat
- Full **English** and **Hindi (हिंदी)** support.
- Native Text-to-Speech (TTS) audio playback for low-literacy rural accessibility.
- Integrated AI Agronomist Chatbot for personalized agronomic questions.

---

## 🌾 Supported Crops & Diseases

The model classifies **38 distinct crop-disease combinations** across 14 vital crop families:

| Crop | Target Pathologies & Conditions |
|---|---|
| **Tomato** | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy |
| **Potato** | Early Blight, Late Blight, Healthy |
| **Corn (Maize)** | Cercospora Leaf Spot (Gray Leaf Spot), Common Rust, Northern Leaf Blight, Healthy |
| **Apple** | Apple Scab, Black Rot, Cedar Apple Rust, Healthy |
| **Grape** | Black Rot, Esca (Black Measles), Leaf Blight (Isariopsis), Healthy |
| **Chili / Bell Pepper** | Bacterial Spot, Healthy |
| **Rice & Wheat** | Leaf Blast, Brown Spot, Rust, Healthy |
| **Others** | Soybean, Strawberry, Cherry, Peach, Orange/Citrus, Squash, Raspberry, Blueberry |

---

## 💻 Quick Start

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/4m4nT/Kisan_Mitra.git
cd Kisan_Mitra
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Application
```bash
# On Windows, you can also double-click run_app.bat
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 📂 Project Architecture

```plaintext
agrisense-prototype/
│
├── app.py                     # Primary Application (UI, Vision Inference, Weather, Advisory)
├── sih_pillars_addon.py       # Surveillance Dashboard, Hotspots, KVK Directory, PHI Engine
├── disease_info.py            # Agronomic Knowledge Base (Symptoms, Organic/Chemical Treatments)
│
├── models/
│   └── cropguard.onnx         # 38-Class Trained Deep Learning Vision Model (ONNX format)
│
├── static/                    # UI Assets, Icons, and Audio Cache
├── kisan_mitra_sih.db         # Persistent SQLite Surveillance & Referral Database
├── requirements.txt           # Python Package Manifest
├── run_app.bat                # Windows One-Click Execution Batch Script
└── README.md                  # Project Documentation
```

---

## 🛠️ Technology Stack

| Domain | Technologies Used |
|---|---|
| **Core Framework** | Python 3.10+, Streamlit |
| **Computer Vision & AI** | ONNX Runtime, ResNet-50 Architecture, OpenCV, Pillow, NumPy |
| **Weather & Epidemiology** | Open-Meteo Global Meteorological API |
| **Database & Persistence** | SQLite3, Pandas |
| **UI & Accessibility** | Responsive Glassmorphism CSS, Google Fonts (Plus Jakarta Sans, Fraunces), gTTS |
| **Visualization** | Streamlit Maps, Altair, Matplotlib Charts |

---

## 🏛️ Smart India Hackathon Strategic Alignment

This prototype addresses key agricultural challenges recognized by **ICAR** and the **Ministry of Agriculture & Farmers Welfare**:

1. **Early Detection:** Reduces crop loss by detecting foliar pathogens before visible field-wide spread.
2. **Judicious Chemical Use:** Enforces strict PHI periods and dosage limits, promoting soil health and export quality.
3. **Data-Driven Policy:** Feeds anonymous, aggregated disease hot-spots directly into state surveillance pipelines.
4. **Inclusive Design:** Full voice readouts and bilingual interfaces ensure adoption by marginal farmers.

---

## 📄 License & Attribution


Developed with ❤️ by Aman Tomar for **Indian Agriculture & Precision Farming**.
