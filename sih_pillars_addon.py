"""
Kisan Mitra — Advanced Features Module (sih_pillars_addon.py)
Author: SIH Precision Agri-Tech Team

Advanced agricultural intelligence features:
  - Geospatial Hotspot Mapping & Outbreak Proximity Alerts
  - Agriculture Officials' Analytics & Surveillance Dashboard
  - Expert Validation Loop & KVK / Laboratory Referral Directory
  - Chemical Safety / PHI Guardrails & Follow-up Recovery Tracker

Run standalone:  streamlit run sih_pillars_addon.py
"""

import os
import sqlite3
import datetime as dt
import math
import io
import pandas as pd
import numpy as np
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# 1. PERSISTENT DATABASE ENGINE (SQLite)
# ─────────────────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kisan_mitra_sih.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Table 1: Disease Detections & Hotspots
    c.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            crop TEXT,
            disease TEXT,
            confidence REAL,
            severity TEXT,
            lat REAL,
            lon REAL,
            city TEXT,
            state TEXT,
            status TEXT DEFAULT 'Pending Expert Review',
            expert_notes TEXT DEFAULT '',
            farmer_phone TEXT DEFAULT ''
        )
    """)

    # Table 2: KVK & Lab Directory
    c.execute("""
        CREATE TABLE IF NOT EXISTS kvk_labs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            state TEXT,
            district TEXT,
            contact TEXT,
            address TEXT
        )
    """)

    # Table 3: Follow-up Recovery Schedules
    c.execute("""
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_id INTEGER,
            farmer_name TEXT,
            phone TEXT,
            crop TEXT,
            disease TEXT,
            scheduled_date TEXT,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT DEFAULT ''
        )
    """)

    conn.commit()

    # Seed KVK / lab directory if empty (pan-India network)
    c.execute("SELECT COUNT(*) FROM kvk_labs")
    if c.fetchone()[0] == 0:
        sample_kvk = [
            # Uttarakhand
            ("KVK Dehradun (ICAR-IVRI)", "KVK Extension Center", "Uttarakhand", "Dehradun", "+91 135 244 0145", "ICAR-IVRI Campus, Mukteshwar Road, Dehradun"),
            ("KVK Haridwar — Bharat Ratna C. Subramaniam", "KVK Extension Center", "Uttarakhand", "Haridwar", "+91 1332 272 450", "Pant Nagar University Extension, Haridwar"),
            ("G.B. Pant University of Agri & Technology", "Agriculture University Lab", "Uttarakhand", "Udham Singh Nagar", "+91 5944 233 338", "Pant Nagar, Udham Singh Nagar"),
            ("KVK Almora — ICAR VPKAS", "KVK Extension Center", "Uttarakhand", "Almora", "+91 5962 230 208", "ICAR-VPKAS, Almora"),
            # Himachal Pradesh
            ("KVK Shimla — Dr. Y.S. Parmar UHF", "KVK Extension Center", "Himachal Pradesh", "Shimla", "+91 177 265 0505", "Nauni, Solan — UHF Campus"),
            ("KVK Kangra — CSKHPKV", "KVK Extension Center", "Himachal Pradesh", "Kangra", "+91 1892 230 327", "Palampur, Kangra"),
            # Punjab
            ("Central Potato Research Station (ICAR)", "ICAR National Laboratory", "Punjab", "Jalandhar", "+91 181 225 3300", "Model Town, Jalandhar"),
            ("KVK Ludhiana — PAU", "KVK Extension Center", "Punjab", "Ludhiana", "+91 161 240 1960", "Punjab Agricultural University, Ludhiana"),
            # Haryana
            ("KVK Hisar — CCSHAU", "KVK Extension Center", "Haryana", "Hisar", "+91 1662 234 693", "Chaudhary Charan Singh HAU, Hisar"),
            ("KVK Karnal — ICAR NDRI", "KVK Extension Center", "Haryana", "Karnal", "+91 184 225 9023", "NDRI Campus, Karnal"),
            # Uttar Pradesh
            ("KVK Lucknow — CSAUAT", "KVK Extension Center", "Uttar Pradesh", "Lucknow", "+91 522 274 0544", "CSAUA&T Campus, Kanpur Road, Lucknow"),
            ("KVK Varanasi — ICAR IIVR", "KVK Extension Center", "Uttar Pradesh", "Varanasi", "+91 542 263 5214", "Indian Institute of Vegetable Research, Varanasi"),
            # Maharashtra
            ("KVK Pune — Junnar", "KVK Extension Center", "Maharashtra", "Pune", "+91 20 2553 7324", "Narayanangaon, Junnar, Pune"),
            ("ICAR — NRC for Grapes, Pune", "ICAR National Laboratory", "Maharashtra", "Pune", "+91 20 2695 6000", "Solapur Road, Manjri Farm, Pune"),
            # Rajasthan
            ("KVK Jaipur — SKNAU", "KVK Extension Center", "Rajasthan", "Jaipur", "+91 1425 254 022", "SKN Agriculture University, Jobner, Jaipur"),
            # Madhya Pradesh
            ("KVK Bhopal — ICAR CIAE", "KVK Extension Center", "Madhya Pradesh", "Bhopal", "+91 755 252 1000", "Nabi Bagh, Berasia Road, Bhopal"),
        ]
        c.executemany("""
            INSERT INTO kvk_labs (name, type, state, district, contact, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_kvk)

    conn.commit()
    conn.close()


def clean_legacy_records():
    """Remove any invalid/stale detection entries with fake test coordinates or incorrect default states."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        # Clean up any legacy test entries
        c.execute("""
            DELETE FROM detections
            WHERE farmer_phone IN ('9876543210','9876543211','9876543212','9876543213','9876543214','9876543215')
               OR (city = 'Pune' AND state = 'Maharashtra' AND expert_notes LIKE '%Cymoxanil%')
        """)
        conn.commit()
        conn.close()
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# 2. CITY, STATE & COORDINATES LOOKUP DATABASE
# ─────────────────────────────────────────────────────────────────────────────
CITY_STATE_MAP: dict[str, str] = {
    # Uttarakhand
    "dehradun": "Uttarakhand", "haridwar": "Uttarakhand", "rishikesh": "Uttarakhand",
    "mussoorie": "Uttarakhand", "roorkee": "Uttarakhand", "haldwani": "Uttarakhand",
    "nainital": "Uttarakhand", "almora": "Uttarakhand", "pithoragarh": "Uttarakhand",
    "rudrapur": "Uttarakhand", "kashipur": "Uttarakhand", "pantnagar": "Uttarakhand",
    "chamoli": "Uttarakhand", "tehri": "Uttarakhand", "uttarkashi": "Uttarakhand",
    "bageshwar": "Uttarakhand", "champawat": "Uttarakhand", "kotdwar": "Uttarakhand",
    # Himachal Pradesh
    "shimla": "Himachal Pradesh", "manali": "Himachal Pradesh", "dharamshala": "Himachal Pradesh",
    "solan": "Himachal Pradesh", "mandi": "Himachal Pradesh", "kullu": "Himachal Pradesh",
    "palampur": "Himachal Pradesh", "bilaspur": "Himachal Pradesh", "chamba": "Himachal Pradesh",
    # Punjab
    "ludhiana": "Punjab", "amritsar": "Punjab", "jalandhar": "Punjab",
    "patiala": "Punjab", "bathinda": "Punjab", "mohali": "Punjab", "pathankot": "Punjab",
    # Haryana
    "gurugram": "Haryana", "faridabad": "Haryana", "hisar": "Haryana",
    "panipat": "Haryana", "ambala": "Haryana", "karnal": "Haryana", "rohtak": "Haryana",
    # Uttar Pradesh
    "lucknow": "Uttar Pradesh", "kanpur": "Uttar Pradesh", "agra": "Uttar Pradesh",
    "varanasi": "Uttar Pradesh", "allahabad": "Uttar Pradesh", "prayagraj": "Uttar Pradesh",
    "meerut": "Uttar Pradesh", "noida": "Uttar Pradesh", "ghaziabad": "Uttar Pradesh",
    "mathura": "Uttar Pradesh", "bareilly": "Uttar Pradesh", "moradabad": "Uttar Pradesh",
    "gorakhpur": "Uttar Pradesh", "aligarh": "Uttar Pradesh", "saharanpur": "Uttar Pradesh",
    # Rajasthan
    "jaipur": "Rajasthan", "jodhpur": "Rajasthan", "udaipur": "Rajasthan",
    "ajmer": "Rajasthan", "kota": "Rajasthan", "bikaner": "Rajasthan", "alwar": "Rajasthan",
    # Gujarat
    "ahmedabad": "Gujarat", "surat": "Gujarat", "vadodara": "Gujarat",
    "rajkot": "Gujarat", "gandhinagar": "Gujarat", "bhavnagar": "Gujarat", "jamnagar": "Gujarat",
    # Maharashtra
    "mumbai": "Maharashtra", "pune": "Maharashtra", "nagpur": "Maharashtra",
    "nashik": "Maharashtra", "aurangabad": "Maharashtra", "solapur": "Maharashtra",
    "kolhapur": "Maharashtra", "thane": "Maharashtra", "nanded": "Maharashtra",
    # Karnataka
    "bengaluru": "Karnataka", "bangalore": "Karnataka", "mysuru": "Karnataka",
    "mysore": "Karnataka", "hubli": "Karnataka", "mangaluru": "Karnataka",
    "belagavi": "Karnataka", "davanagere": "Karnataka",
    # Tamil Nadu
    "chennai": "Tamil Nadu", "coimbatore": "Tamil Nadu", "madurai": "Tamil Nadu",
    "tiruchirappalli": "Tamil Nadu", "salem": "Tamil Nadu", "vellore": "Tamil Nadu",
    # Andhra Pradesh
    "visakhapatnam": "Andhra Pradesh", "vijayawada": "Andhra Pradesh",
    "guntur": "Andhra Pradesh", "tirupati": "Andhra Pradesh", "kurnool": "Andhra Pradesh",
    # Telangana
    "hyderabad": "Telangana", "warangal": "Telangana", "nizamabad": "Telangana",
    # West Bengal
    "kolkata": "West Bengal", "howrah": "West Bengal", "durgapur": "West Bengal",
    "siliguri": "West Bengal", "asansol": "West Bengal", "darjeeling": "West Bengal",
    # Bihar
    "patna": "Bihar", "gaya": "Bihar", "muzaffarpur": "Bihar", "bhagalpur": "Bihar",
    # Madhya Pradesh
    "bhopal": "Madhya Pradesh", "indore": "Madhya Pradesh", "jabalpur": "Madhya Pradesh",
    "gwalior": "Madhya Pradesh", "ujjain": "Madhya Pradesh",
    # Odisha
    "bhubaneswar": "Odisha", "cuttack": "Odisha", "rourkela": "Odisha", "puri": "Odisha",
    # Assam
    "guwahati": "Assam", "dibrugarh": "Assam", "silchar": "Assam", "jorhat": "Assam",
    # Delhi / NCR
    "delhi": "Delhi", "new delhi": "Delhi",
    # Jharkhand
    "ranchi": "Jharkhand", "jamshedpur": "Jharkhand", "dhanbad": "Jharkhand",
    # Chhattisgarh
    "raipur": "Chhattisgarh", "bilaspur": "Chhattisgarh",
    # Kerala
    "thiruvananthapuram": "Kerala", "kochi": "Kerala", "kozhikode": "Kerala",
    "thrissur": "Kerala", "kannur": "Kerala",
    # Goa
    "panaji": "Goa", "margao": "Goa", "vasco": "Goa",
    # Jammu & Kashmir
    "srinagar": "Jammu & Kashmir", "jammu": "Jammu & Kashmir", "anantnag": "Jammu & Kashmir",
    # Sikkim
    "gangtok": "Sikkim",
    # Meghalaya
    "shillong": "Meghalaya",
    # Tripura
    "agartala": "Tripura",
    # Manipur
    "imphal": "Manipur",
    # Nagaland
    "kohima": "Nagaland",
    # Arunachal Pradesh
    "itanagar": "Arunachal Pradesh",
    # Mizoram
    "aizawl": "Mizoram",
}

CITY_COORDS_MAP: dict[str, tuple[float, float]] = {
    # Uttarakhand
    "dehradun":     (30.3165, 78.0322),
    "haridwar":     (29.9457, 78.1642),
    "rishikesh":    (30.0869, 78.2676),
    "mussoorie":    (30.4598, 78.0664),
    "roorkee":      (29.8543, 77.8880),
    "haldwani":     (29.2183, 79.5130),
    "nainital":     (29.3803, 79.4636),
    "almora":       (29.5971, 79.6591),
    "pithoragarh":  (29.5832, 80.2180),
    "rudrapur":     (28.9815, 79.4020),
    "kashipur":     (29.2104, 78.9619),
    "pantnagar":    (29.0000, 79.4833),
    "chamoli":      (30.4167, 79.3333),
    "tehri":        (30.3800, 78.4800),
    "uttarkashi":   (30.7268, 78.4354),
    "kotdwar":      (29.7460, 78.5284),
    # Himachal Pradesh
    "shimla":       (31.1048, 77.1734),
    "manali":       (32.2396, 77.1887),
    "dharamshala":  (32.2190, 76.3234),
    "solan":        (30.9045, 77.0967),
    "mandi":        (31.7080, 76.9320),
    "palampur":     (32.1109, 76.5363),
    # Punjab
    "ludhiana":     (30.9010, 75.8573),
    "amritsar":     (31.6340, 74.8723),
    "jalandhar":    (31.3260, 75.5762),
    "patiala":      (30.3398, 76.3869),
    "bathinda":     (30.2070, 74.9455),
    "mohali":       (30.7046, 76.7179),
    # Haryana
    "gurugram":     (28.4595, 77.0266),
    "faridabad":    (28.4089, 77.3178),
    "hisar":        (29.1492, 75.7217),
    "panipat":      (29.3909, 76.9635),
    "ambala":       (30.3782, 76.7767),
    "karnal":       (29.6857, 76.9905),
    # Uttar Pradesh
    "lucknow":      (26.8467, 80.9462),
    "kanpur":       (26.4499, 80.3319),
    "agra":         (27.1767, 78.0081),
    "varanasi":     (25.3176, 82.9739),
    "prayagraj":    (25.4358, 81.8463),
    "allahabad":    (25.4358, 81.8463),
    "meerut":       (28.9845, 77.7064),
    "noida":        (28.5355, 77.3910),
    "ghaziabad":    (28.6692, 77.4538),
    "mathura":      (27.4924, 77.6737),
    "bareilly":     (28.3670, 79.4304),
    "gorakhpur":    (26.7606, 83.3732),
    "saharanpur":   (29.9679, 77.5452),
    # Rajasthan
    "jaipur":       (26.9124, 75.7873),
    "jodhpur":      (26.2389, 73.0243),
    "udaipur":      (24.5854, 73.7125),
    "ajmer":        (26.4499, 74.6399),
    "kota":         (25.2138, 75.8648),
    "bikaner":      (28.0229, 73.3119),
    # Gujarat
    "ahmedabad":    (23.0225, 72.5714),
    "surat":        (21.1702, 72.8311),
    "vadodara":     (22.3072, 73.1812),
    "rajkot":       (22.3039, 70.8022),
    "gandhinagar":  (23.2156, 72.6369),
    # Maharashtra
    "mumbai":       (19.0760, 72.8777),
    "pune":         (18.5204, 73.8567),
    "nagpur":       (21.1458, 79.0882),
    "nashik":       (19.9975, 73.7898),
    "aurangabad":   (19.8762, 75.3433),
    "solapur":      (17.6805, 75.9064),
    "kolhapur":     (16.7050, 74.2433),
    # Karnataka
    "bengaluru":    (12.9716, 77.5946),
    "bangalore":    (12.9716, 77.5946),
    "mysuru":       (12.2958, 76.6394),
    "mysore":       (12.2958, 76.6394),
    "hubli":        (15.3647, 75.1240),
    "mangaluru":    (12.9141, 74.8560),
    # Tamil Nadu
    "chennai":      (13.0827, 80.2707),
    "coimbatore":   (11.0168, 76.9558),
    "madurai":      (9.9252, 78.1198),
    # Andhra Pradesh
    "visakhapatnam": (17.6868, 83.2185),
    "vijayawada":   (16.5062, 80.6480),
    # Telangana
    "hyderabad":    (17.3850, 78.4867),
    # West Bengal
    "kolkata":      (22.5726, 88.3639),
    "siliguri":     (26.7271, 88.3953),
    # Bihar
    "patna":        (25.5941, 85.1376),
    # Madhya Pradesh
    "bhopal":       (23.2599, 77.4126),
    "indore":       (22.7196, 75.8577),
    # Delhi
    "delhi":        (28.7041, 77.1025),
    "new delhi":    (28.6139, 77.2090),
    # Jammu & Kashmir
    "srinagar":     (34.0837, 74.7973),
    "jammu":        (32.7266, 74.8570),
}


def resolve_state(city: str, fallback: str = "Unknown") -> str:
    """Return the correct Indian state for any city name (case-insensitive)."""
    if not city or not str(city).strip():
        return fallback
    clean_city = str(city).strip().lower()
    return CITY_STATE_MAP.get(clean_city, fallback)


def resolve_coords(city: str) -> tuple[float, float]:
    """Return (lat, lon) coordinates for a city name, defaulting to Dehradun coordinates."""
    if not city or not str(city).strip():
        return (30.3165, 78.0322)
    clean_city = str(city).strip().lower()
    return CITY_COORDS_MAP.get(clean_city, (30.3165, 78.0322))


def save_detection_to_db(crop, disease, confidence, severity, lat=None, lon=None, city="Dehradun", state="", phone=""):
    """Persist a new field detection. State & coordinates are dynamically resolved if not provided."""
    city_clean = str(city).strip() if city else "Dehradun"
    if not state or state == "Unknown" or state == "Maharashtra" and city_clean.lower() != "pune":
        state = resolve_state(city_clean, fallback="Uttarakhand" if city_clean.lower() == "dehradun" else "Unknown")
    
    if lat is None or lon is None:
        lat, lon = resolve_coords(city_clean)
        
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO detections (timestamp, crop, disease, confidence, severity, lat, lon, city, state, status, farmer_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Expert Review', ?)
    """, (dt.datetime.now().strftime("%Y-%m-%d %H:%M"), crop, disease, confidence, severity, lat, lon, city_clean, state, phone))
    conn.commit()
    inserted_id = c.lastrowid
    conn.close()
    return inserted_id


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# Initialize database and clean any bad records
init_db()
clean_legacy_records()


# ─────────────────────────────────────────────────────────────────────────────
# 3. RESPONSIVE CSS STYLES (MOBILE & PC OPTIMIZED)
# ─────────────────────────────────────────────────────────────────────────────
def _inject_styles():
    st.markdown("""
    <style>
    /* Section header cards */
    .km-section-header {
        background: linear-gradient(135deg, rgba(22,193,150,0.14) 0%, rgba(13,122,112,0.08) 100%);
        border: 1px solid rgba(22,193,150,0.28);
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 1.2rem;
    }
    .km-section-header h2 { margin: 0 0 .25rem 0; font-size: 1.35rem; color: #16C196; font-weight: 700; }
    .km-section-header p  { margin: 0; color: #9BBFB8; font-size: 0.88rem; line-height: 1.4; }

    /* Responsive KPI metric tiles */
    .km-kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 0.9rem;
        margin-bottom: 1.2rem;
    }
    .km-kpi {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        text-align: center;
        transition: transform 0.18s ease, border-color 0.18s ease;
    }
    .km-kpi:hover {
        border-color: rgba(22,193,150,0.4);
        transform: translateY(-2px);
    }
    .km-kpi .val  { font-size: 2rem; font-weight: 800; color: #16C196; line-height: 1.1; }
    .km-kpi .lbl  { font-size: 0.78rem; color: #9BBFB8; margin-top: 0.35rem; font-weight: 500; }
    .km-kpi.danger .val  { color: #FF4D6D; }
    .km-kpi.warning .val { color: #FFB347; }

    /* Dosage result card */
    .km-dosage-card {
        background: rgba(13,122,112,0.14);
        border: 1.5px solid rgba(22,193,150,0.32);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        color: #E2FAF6;
        margin-top: 1rem;
    }
    .km-dosage-card h4 { color: #16C196; margin-top: 0; margin-bottom: 0.6rem; font-size: 1.1rem; }
    .km-dosage-card ul { margin: 0; padding-left: 1.2rem; }
    .km-dosage-card li { margin-bottom: 0.45rem; line-height: 1.45; font-size: 0.9rem; }
    .km-phi { color: #FF4D6D; font-weight: 700; }

    /* Outbreak Alert banners */
    .km-alert-danger {
        background: rgba(255,77,109,0.12);
        border: 1.5px solid rgba(255,77,109,0.42);
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        color: #FF708D;
        margin-bottom: 1rem;
        font-size: 0.92rem;
    }
    .km-alert-ok {
        background: rgba(22,193,150,0.10);
        border: 1.5px solid rgba(22,193,150,0.32);
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        color: #16C196;
        margin-bottom: 1rem;
        font-size: 0.92rem;
    }

    /* Location detection pill badge */
    .km-loc-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(22,193,150,0.12);
        border: 1px solid rgba(22,193,150,0.30);
        border-radius: 20px;
        padding: 0.35rem 0.85rem;
        color: #16C196;
        font-size: 0.88rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }

    /* Empty state friendly box */
    .km-empty-box {
        background: rgba(255,255,255,0.025);
        border: 1px dashed rgba(255,255,255,0.12);
        border-radius: 12px;
        padding: 1.4rem 1.2rem;
        text-align: center;
        color: #9BBFB8;
        font-size: 0.9rem;
        margin: 1rem 0;
    }

    .km-divider { border-top: 1px solid rgba(255,255,255,0.08); margin: 1.4rem 0; }

    /* ── Mobile and Tablet Responsiveness ── */
    @media (max-width: 768px) {
        .km-section-header { padding: 0.9rem 1.1rem; border-radius: 11px; }
        .km-section-header h2 { font-size: 1.2rem; }
        .km-kpi-grid { grid-template-columns: repeat(2, 1fr); gap: 0.6rem; }
        .km-kpi { padding: 0.75rem 0.8rem; }
        .km-kpi .val { font-size: 1.6rem; }
        .km-dosage-card { padding: 0.9rem 1rem; }
        [data-testid="column"] { min-width: 100% !important; }
    }

    @media (max-width: 480px) {
        .km-kpi-grid { grid-template-columns: 1fr; }
        .km-section-header h2 { font-size: 1.1rem; }
        .km-loc-pill { font-size: 0.8rem; padding: 0.3rem 0.65rem; }
    }
    </style>
    """, unsafe_allow_html=True)


def _section_header(icon: str, title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="km-section-header">
        <h2>{icon} {title}</h2>
        {'<p>' + subtitle + '</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 1 — GEOSPATIAL HOTSPOT MAPPING & PROXIMITY ALERTS
# ─────────────────────────────────────────────────────────────────────────────
def render_geospatial_hotspots():
    _section_header(
        "🗺️", "Disease Outbreak Hotspot Map & Farm Alert",
        "Spatial clustering of field disease reports — enter your city to get proactive outbreak alerts."
    )

    conn = get_db_connection()
    df_det = pd.read_sql_query("SELECT * FROM detections", conn)
    conn.close()

    # ── User Location Input
    st.markdown("#### 🚨 Check Outbreak Risk Near Your Location")
    
    col_input, col_rad = st.columns([1.6, 1])
    with col_input:
        city_input = st.text_input(
            "📍 Enter Your City / Town",
            value="Dehradun",
            placeholder="e.g. Dehradun, Haridwar, Shimla, Lucknow...",
            help="Type your city or town name. Regional coordinates and state are resolved automatically."
        )
    with col_rad:
        radius_km = st.slider(
            "Search Radius (km)", min_value=5, max_value=100, value=30,
            help="Scan this area around your location for reported outbreaks."
        )

    # Resolve city info
    target_city = city_input.strip() if city_input else "Dehradun"
    resolved_state = resolve_state(target_city, fallback="Uttarakhand" if target_city.lower() == "dehradun" else "Unknown")
    def_lat, def_lon = resolve_coords(target_city)

    # Display clean location badge
    state_txt = f", {resolved_state}" if resolved_state and resolved_state != "Unknown" else ""
    st.markdown(
        f"""<div class="km-loc-pill">
            <span>📍</span> <span>Selected Location: <b>{target_city.title()}{state_txt}</b></span>
        </div>""",
        unsafe_allow_html=True
    )

    # Optional manual coordinate adjustment (hidden by default)
    user_lat, user_lon = def_lat, def_lon
    with st.expander("📍 Fine-tune GPS Coordinates (Optional — for precise field coordinates)", expanded=False):
        c_lat, c_lon = st.columns(2)
        with c_lat:
            user_lat = st.number_input("Latitude", value=float(def_lat), format="%.4f",
                                       help="Decimal degrees (N is positive)")
        with c_lon:
            user_lon = st.number_input("Longitude", value=float(def_lon), format="%.4f",
                                       help="Decimal degrees (E is positive)")

    # ── Proximity Calculation
    if not df_det.empty:
        # Guarantee state is accurate for every row
        def _get_row_state(row):
            s = str(row.get("state", "")).strip()
            if s and s != "Unknown" and not (s == "Maharashtra" and str(row.get("city", "")).lower() != "pune"):
                return s
            return resolve_state(str(row.get("city", "")), fallback="Unknown")

        df_det = df_det.copy()
        df_det["state"] = df_det.apply(_get_row_state, axis=1)

        nearby_cases = []
        for _, row in df_det.iterrows():
            try:
                r_lat = float(row["lat"])
                r_lon = float(row["lon"])
                dist = haversine_km(user_lat, user_lon, r_lat, r_lon)
                if dist <= radius_km:
                    nearby_cases.append((row, dist))
            except Exception:
                continue

        if nearby_cases:
            st.markdown(f"""
            <div class="km-alert-danger">
                &#9888; <strong>Outbreak Alert:</strong> &nbsp;{len(nearby_cases)} disease report(s) found within {radius_km} km of {target_city.title()}.
            </div>
            """, unsafe_allow_html=True)
            for case, d in sorted(nearby_cases, key=lambda x: x[1])[:5]:
                c_st = case['state'] if case['state'] and case['state'] != "Unknown" else resolve_state(case['city'])
                st.markdown(
                    f"&nbsp;&nbsp;&nbsp;🔴 **{case['disease']}** on *{case['crop']}* — "
                    f"**{d:.1f} km away** · {case['city']}, {c_st} · "
                    f"Severity: **{case['severity']}**"
                )
        else:
            st.markdown(f"""
            <div class="km-alert-ok">
                &#10003; <strong>Safe Zone:</strong> No active disease outbreaks reported within {radius_km} km of {target_city.title()}.
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="km-divider"></div>', unsafe_allow_html=True)

        # ── Live Cluster Map
        st.markdown("#### 📍 Regional Disease Outbreak Map")
        map_df = (df_det[["lat", "lon", "disease", "crop", "severity", "city"]]
                  .rename(columns={"lat": "latitude", "lon": "longitude"}))
        st.map(map_df, size=20, color="#FF4D6D")

        # ── Recent Reports Table
        st.markdown("#### 📋 Recent Regional Outbreak Reports")
        display_df = (
            df_det[["timestamp", "city", "state", "crop", "disease", "severity", "status"]]
            .sort_values(by="timestamp", ascending=False)
            .rename(columns={
                "timestamp": "Date & Time", "city": "City", "state": "State",
                "crop": "Crop", "disease": "Disease", "severity": "Severity",
                "status": "Verification Status"
            })
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    else:
        st.markdown(f"""
        <div class="km-alert-ok">
            &#10003; <strong>All Clear:</strong> No disease outbreaks currently recorded for this region.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="km-empty-box">
            🌱 <b>No field disease reports have been logged yet.</b><br/>
            When farmers or extension workers analyze infected crops in the AI Crop Doctor, 
            geolocated detections will appear here and on the regional surveillance map in real-time.
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 2 — AGRICULTURE OFFICIALS' SURVEILLANCE DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def render_officials_dashboard():
    _section_header(
        "📊", "Officials' Surveillance Dashboard",
        "Decision support portal for district & state agricultural officers — monitor trends and prioritize field interventions."
    )

    conn = get_db_connection()
    df_det = pd.read_sql_query("SELECT * FROM detections", conn)
    conn.close()

    if df_det.empty:
        st.markdown("""
        <div class="km-empty-box">
            📊 <b>Surveillance Database is Empty</b><br/>
            Real-time analytics and district breakdown charts will activate automatically as soon as field reports are submitted.
        </div>
        """, unsafe_allow_html=True)
        return

    # Dynamic state fix
    def _fix_state(row):
        s = str(row.get("state", "")).strip()
        if s and s != "Unknown" and not (s == "Maharashtra" and str(row.get("city", "")).lower() != "pune"):
            return s
        return resolve_state(str(row.get("city", "")), fallback="Unknown")

    df_det["state"] = df_det.apply(_fix_state, axis=1)

    # ── KPI Cards
    total_cases    = len(df_det)
    high_sev       = len(df_det[df_det["severity"] == "High"])
    pending_rev    = len(df_det[df_det["status"] == "Pending Expert Review"])
    verified_cases = len(df_det[df_det["status"] == "Verified"])

    st.markdown(f"""
    <div class="km-kpi-grid">
        <div class="km-kpi">
            <div class="val">{total_cases}</div>
            <div class="lbl">Total Disease Reports</div>
        </div>
        <div class="km-kpi danger">
            <div class="val">{high_sev}</div>
            <div class="lbl">High Severity Outbreaks</div>
        </div>
        <div class="km-kpi warning">
            <div class="val">{pending_rev}</div>
            <div class="lbl">Awaiting Expert Review</div>
        </div>
        <div class="km-kpi">
            <div class="val">{verified_cases}</div>
            <div class="lbl">Verified Diagnoses</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="km-divider"></div>', unsafe_allow_html=True)

    # ── Charts
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("##### 🌾 Outbreaks by Crop Type")
        st.bar_chart(df_det["crop"].value_counts())
    with col_c2:
        st.markdown("##### 🦠 Top Detected Diseases")
        st.bar_chart(df_det["disease"].value_counts().head(5))

    # ── District summary
    st.markdown("##### 🏙️ District & State Outbreak Breakdown")
    dist_summary = (
        df_det.groupby(["state", "city", "crop"])
        .agg(
            Total_Reports=("id", "count"),
            High_Severity=("severity", lambda x: (x == "High").sum())
        )
        .reset_index()
        .rename(columns={"state": "State", "city": "City", "crop": "Crop"})
    )
    st.dataframe(dist_summary, use_container_width=True, hide_index=True)

    st.markdown('<div class="km-divider"></div>', unsafe_allow_html=True)

    # ── Export
    csv_buf = io.StringIO()
    df_det.to_csv(csv_buf, index=False)
    st.download_button(
        label="📥 Export Full Surveillance Report (CSV)",
        data=csv_buf.getvalue(),
        file_name=f"crop_health_surveillance_{dt.date.today()}.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 3 — EXPERT VALIDATION LOOP & KVK / LAB REFERRAL DIRECTORY
# ─────────────────────────────────────────────────────────────────────────────
def render_expert_validation_and_referral():
    _section_header(
        "✅", "Expert Validation & KVK Referral Network",
        "Plant pathologist review queue and laboratory / Krishi Vigyan Kendra referral network."
    )

    conn = get_db_connection()
    tab_review, tab_kvk = st.tabs(["🔎 Expert Review Queue", "🏛️ KVK & Lab Directory"])

    # ── Tab 1: Expert review queue
    with tab_review:
        st.markdown("#### 👨‍🔬 AI Diagnosis Verification Queue")
        st.caption("Plant pathologists can confirm, correct, or reject AI-generated field diagnoses.")

        df_pending = pd.read_sql_query(
            "SELECT * FROM detections WHERE status = 'Pending Expert Review'", conn)

        if df_pending.empty:
            st.success("🎉 All AI diagnoses have been reviewed — the queue is clear!")
        else:
            st.info(f"**{len(df_pending)} report(s)** are awaiting expert verification.")
            for _, row in df_pending.iterrows():
                row_state = row['state'] if row['state'] and row['state'] != "Unknown" else resolve_state(row['city'])
                with st.expander(
                    f"📄 Report #{row['id']} — {row['crop']}: **{row['disease']}** · {row['city']}, {row_state}"
                ):
                    info_col, action_col = st.columns([2, 3])
                    with info_col:
                        st.markdown(f"**Date Logged:** `{row['timestamp']}`")
                        st.markdown(f"**AI Confidence:** `{row['confidence']*100:.1f}%`")
                        st.markdown(f"**Severity:** `{row['severity']}`")
                        st.markdown(f"**Farmer Phone:** `{row['farmer_phone'] or 'Not provided'}`")
                    with action_col:
                        notes_input = st.text_area(
                            "Expert Notes / Agronomic Guidance",
                            key=f"notes_{row['id']}",
                            value="Diagnosis verified. Follow recommended safety guidelines.",
                            height=100
                        )
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            if st.button("✅ Confirm & Verify", key=f"acc_{row['id']}",
                                         use_container_width=True):
                                c = conn.cursor()
                                c.execute(
                                    "UPDATE detections SET status = 'Verified', expert_notes = ? WHERE id = ?",
                                    (notes_input, row['id'])
                                )
                                conn.commit()
                                st.success(f"Report #{row['id']} verified.")
                                st.rerun()
                        with btn_col2:
                            if st.button("❌ Correct / Reject", key=f"rej_{row['id']}",
                                         use_container_width=True):
                                c = conn.cursor()
                                c.execute(
                                    "UPDATE detections SET status = 'Rejected / Corrected', expert_notes = ? WHERE id = ?",
                                    (notes_input, row['id'])
                                )
                                conn.commit()
                                st.warning(f"Report #{row['id']} marked as corrected.")
                                st.rerun()

    # ── Tab 2: KVK & Lab directory
    with tab_kvk:
        st.markdown("#### 🧪 Krishi Vigyan Kendra & Soil/Plant Testing Labs")
        st.write(
            "If leaf symptoms require PCR confirmation or microscopic soil/tissue analysis, "
            "refer to the nearest accredited testing laboratory:"
        )

        df_kvk = pd.read_sql_query("SELECT * FROM kvk_labs", conn)
        state_filter = st.selectbox(
            "🔍 Filter Labs by State",
            ["All States"] + sorted(df_kvk["state"].unique().tolist())
        )
        if state_filter != "All States":
            df_kvk = df_kvk[df_kvk["state"] == state_filter]

        st.dataframe(
            df_kvk[["name", "type", "district", "state", "contact", "address"]]
            .rename(columns={
                "name": "Centre Name", "type": "Type", "district": "District",
                "state": "State", "contact": "Contact", "address": "Address"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown('<div class="km-divider"></div>', unsafe_allow_html=True)
        st.markdown("##### 📝 Book a Laboratory Sample Referral")
        with st.form("kvk_booking_form", border=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                c_name = st.text_input("Your Name / Extension Worker Name",
                                       placeholder="e.g. Ramesh Chandra")
                c_crop = st.text_input("Crop Name & Variety",
                                       placeholder="e.g. Tomato — Arka Rakshak")
            with f_col2:
                c_center = st.selectbox(
                    "Select Laboratory / KVK",
                    df_kvk["name"].tolist() if not df_kvk.empty else ["Default KVK"]
                )
                c_date = st.date_input("Preferred Visit Date",
                                       min_value=dt.date.today())
            submitted = st.form_submit_button("📋 Submit Referral Request",
                                              use_container_width=True)
            if submitted:
                ref_id = f"REF-KVK-{np.random.randint(1000, 9999)}"
                st.success(
                    f"✅ Referral **{ref_id}** booked for **{c_name}** at **{c_center}** "
                    f"on **{c_date}**. Please bring a fresh leaf/soil sample."
                )

    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 4 — CHEMICAL SAFETY / PHI GUARDRAILS & FOLLOW-UP TRACKER
# ─────────────────────────────────────────────────────────────────────────────
CHEMICAL_DATA = {
    "Mancozeb 75% WP (Fungicide)": {
        "rate_lo": 600, "rate_hi": 800, "unit": "grams",
        "water_per_acre": 200, "phi_days": 14,
        "safety": "Wear protective gloves & mask. Do not harvest within 14 days of spraying."
    },
    "Copper Hydroxide 77% WP (Bactericide/Fungicide)": {
        "rate_lo": 500, "rate_hi": 500, "unit": "grams",
        "water_per_acre": 200, "phi_days": 7,
        "safety": "Avoid spraying during high bloom stage to protect pollinators."
    },
    "Cymoxanil 8% + Mancozeb 64% WP (Late Blight Curative)": {
        "rate_lo": 600, "rate_hi": 600, "unit": "grams",
        "water_per_acre": 200, "phi_days": 10,
        "safety": "Emergency curative spray. Maximum 2 applications per crop season."
    },
    "Imidacloprid 17.8% SL (Vector Insecticide)": {
        "rate_lo": 60, "rate_hi": 80, "unit": "ml",
        "water_per_acre": 150, "phi_days": 15,
        "safety": "Toxic to honeybees. Spray strictly during late evening hours."
    },
    "Azoxystrobin 23% SC (Broad Spectrum Fungicide)": {
        "rate_lo": 200, "rate_hi": 200, "unit": "ml",
        "water_per_acre": 200, "phi_days": 5,
        "safety": "Rotate with alternative chemical groups to prevent fungal resistance."
    },
}


def render_safety_and_followup():
    _section_header(
        "🧪", "Chemical Safety & Recovery Tracker",
        "Safe pesticide dosage calculator, Pre-Harvest Interval (PHI) warnings, and recovery follow-up scheduling."
    )

    tab_calc, tab_follow = st.tabs(["🧮 Dosage & PHI Calculator", "📅 Recovery Follow-Up Tracker"])

    # ── Tab 1: Dosage & PHI calculator
    with tab_calc:
        st.markdown("#### 🛡️ Safe Chemical Dosage & Pre-Harvest Interval Calculator")
        st.write(
            "Enter your farm area and select the chemical to calculate exact quantities "
            "and mandatory harvest waiting periods."
        )

        col_c, col_a = st.columns([3, 2])
        with col_c:
            selected_chem = st.selectbox("Select Chemical Spray", list(CHEMICAL_DATA.keys()))
        with col_a:
            land_acres = st.number_input(
                "Farm Area (Acres)", min_value=0.25, max_value=50.0,
                value=1.0, step=0.25
            )

        info = CHEMICAL_DATA[selected_chem]
        qty_lo = info["rate_lo"] * land_acres
        qty_hi = info["rate_hi"] * land_acres
        qty_str = (f"{qty_lo:.0f} - {qty_hi:.0f} {info['unit']}"
                   if qty_lo != qty_hi else f"{qty_lo:.0f} {info['unit']}")
        water_needed  = info["water_per_acre"] * land_acres
        safe_harvest  = dt.date.today() + dt.timedelta(days=info["phi_days"])

        st.markdown(f"""
        <div class="km-dosage-card">
            <h4>&#128203; Calculated Dosage for {land_acres:.2f} Acre(s)</h4>
            <ul>
                <li><b>Chemical Quantity Required:</b> &nbsp; <b>{qty_str}</b></li>
                <li><b>Spray Water Volume:</b> &nbsp; <b>{water_needed:.0f} Litres</b></li>
                <li><b>&#9888; Pre-Harvest Interval (PHI):</b> &nbsp;
                    <span class="km-phi">{info['phi_days']} Days</span>
                    &mdash; earliest safe harvest date: <b>{safe_harvest.strftime('%d %b %Y')}</b>
                </li>
                <li><b>&#128737; Safety Directive:</b> &nbsp; {info['safety']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # ── Tab 2: Recovery follow-up tracker
    with tab_follow:
        st.markdown("#### 📅 Post-Treatment Recovery Monitoring")
        st.write(
            "Schedule a follow-up check-in after spraying to track plant recovery and record field progress."
        )

        conn = get_db_connection()

        with st.form("followup_schedule_form", border=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                f_name  = st.text_input("Farmer Name", placeholder="e.g. Suresh Rawat")
                f_phone = st.text_input("Mobile Number", placeholder="e.g. 98765XXXXX")
            with f_col2:
                f_crop    = st.selectbox("Crop", ["Tomato", "Potato", "Corn (Maize)",
                                                 "Chili / Capsicum", "Grape", "Apple", "Rice", "Wheat"])
                f_disease = st.text_input("Disease Treated", value="Early Blight")

            f_days = st.radio(
                "Follow-Up Interval",
                [3, 7, 14],
                format_func=lambda x: f"{x} Days Post-Spraying",
                horizontal=True
            )
            f_submit = st.form_submit_button("📅 Schedule Follow-Up", use_container_width=True)

            if f_submit:
                sch_date = (dt.date.today() + dt.timedelta(days=f_days)).strftime("%Y-%m-%d")
                c = conn.cursor()
                c.execute("""
                    INSERT INTO followups (farmer_name, phone, crop, disease, scheduled_date, status)
                    VALUES (?, ?, ?, ?, ?, 'Scheduled')
                """, (f_name, f_phone, f_crop, f_disease, sch_date))
                conn.commit()
                st.success(
                    f"✅ Follow-up for **{f_name}** scheduled on **{sch_date}** "
                    f"({f_days} days from today)."
                )

        st.markdown('<div class="km-divider"></div>', unsafe_allow_html=True)
        st.markdown("##### 📋 Active Recovery Monitoring List")
        df_fol = pd.read_sql_query("SELECT * FROM followups", conn)
        conn.close()

        if not df_fol.empty:
            st.dataframe(
                df_fol[["id", "farmer_name", "phone", "crop", "disease", "scheduled_date", "status"]]
                .rename(columns={
                    "id": "#", "farmer_name": "Farmer", "phone": "Mobile",
                    "crop": "Crop", "disease": "Disease",
                    "scheduled_date": "Scheduled Date", "status": "Status"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.markdown("""
            <div class="km-empty-box">
                📅 No recovery follow-ups scheduled yet. Use the form above to schedule your first post-treatment monitoring date.
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN RENDER FUNCTION  (called from app.py or standalone)
# ─────────────────────────────────────────────────────────────────────────────
def render_sih_pillars_tab():
    """
    Renders all advanced feature modules in a unified Streamlit tab container.
    Call from app.py or use: streamlit run sih_pillars_addon.py
    """
    _inject_styles()

    st.markdown("""
    <div style="text-align:center; padding: 0.4rem 0 1.2rem 0;">
        <h1 style="font-size:1.85rem; color:#16C196; margin-bottom:.25rem; font-weight:800;">
            &#127807; Kisan Mitra &mdash; Agricultural Surveillance & Support
        </h1>
        <p style="color:#9BBFB8; font-size:0.92rem; margin:0;">
            Real-time geospatial hotspot mapping &nbsp;&middot;&nbsp; Surveillance analytics
            &nbsp;&middot;&nbsp; Expert validation &nbsp;&middot;&nbsp; Chemical safety
        </p>
    </div>
    """, unsafe_allow_html=True)

    pillar_tabs = st.tabs([
        "🗺️ Hotspot Map",
        "📊 Officials' Dashboard",
        "✅ Expert Validation & KVKs",
        "🧪 Safety & Follow-Up",
    ])

    with pillar_tabs[0]:
        render_geospatial_hotspots()

    with pillar_tabs[1]:
        render_officials_dashboard()

    with pillar_tabs[2]:
        render_expert_validation_and_referral()

    with pillar_tabs[3]:
        render_safety_and_followup()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    st.set_page_config(
        page_title="Kisan Mitra — Advanced Features",
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    render_sih_pillars_tab()
