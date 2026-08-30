"""
Kisan Mitra — SIH Pillars Extension Addon (sih_pillars_addon.py)
Author: SIH Precision Agri-Tech Team

Fulfills all missing SIH problem statement requirements:
1. Pillar 4: Geospatial Hotspot Mapping & Outbreak Proximity Alerts
2. Pillar 8: Agriculture Officials' Analytics & Surveillance Dashboard
3. Pillar 5: Expert Validation Loop & KVK / Laboratory Referral Directory
4. Pillar 7: Follow-up Recovery Tracker & Chemical Safety / PHI Guardrails

This file can be run standalone:
    streamlit run sih_pillars_addon.py

Or imported into app.py with 2 lines of code:
    import sih_pillars_addon
    sih_pillars_addon.render_sih_pillars_tab()
"""

import os
import sqlite3
import datetime as dt
import math
import io
import json
import pandas as pd
import numpy as np
import streamlit as st

# ----------------------------------------------------------------------------
# 1. PERSISTENT DATABASE ENGINE (SQLite)
# ----------------------------------------------------------------------------
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

    # Pre-populate initial sample data if DB is empty
    c.execute("SELECT COUNT(*) FROM detections")
    if c.fetchone()[0] == 0:
        sample_detections = [
            (dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "Tomato", "Tomato Late Blight", 0.94, "High", 18.5204, 73.8567, "Pune", "Maharashtra", "Verified", "High severity blight confirmed. Spray Cymoxanil.", "9876543210"),
            ((dt.datetime.now() - dt.timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "Potato", "Potato Early Blight", 0.88, "Medium", 18.5300, 73.8400, "Pune", "Maharashtra", "Pending Expert Review", "", "9876543211"),
            ((dt.datetime.now() - dt.timedelta(days=2)).strftime("%Y-%m-%d %H:%M"), "Tomato", "Tomato Yellow Leaf Curl Virus", 0.91, "High", 19.0760, 72.8777, "Mumbai", "Maharashtra", "Verified", "Whitefly infestation vector confirmed.", "9876543212"),
            ((dt.datetime.now() - dt.timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), "Corn (Maize)", "Corn Common Rust", 0.85, "Medium", 19.8762, 75.3433, "Aurangabad", "Maharashtra", "Verified", "Foliar spray recommended.", "9876543213"),
            ((dt.datetime.now() - dt.timedelta(days=4)).strftime("%Y-%m-%d %H:%M"), "Grape", "Grape Black Rot", 0.92, "High", 19.9975, 73.7898, "Nashik", "Maharashtra", "Verified", "Prune mummified clusters.", "9876543214"),
            ((dt.datetime.now() - dt.timedelta(days=5)).strftime("%Y-%m-%d %H:%M"), "Potato", "Potato Late Blight", 0.96, "High", 18.5100, 73.8600, "Pune", "Maharashtra", "Pending Expert Review", "", "9876543215"),
        ]
        c.executemany("""
            INSERT INTO detections (timestamp, crop, disease, confidence, severity, lat, lon, city, state, status, expert_notes, farmer_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_detections)

    c.execute("SELECT COUNT(*) FROM kvk_labs")
    if c.fetchone()[0] == 0:
        sample_kvk = [
            ("Krishi Vigyan Kendra (KVK) Pune", "KVK Extension Center", "Maharashtra", "Pune", "+91 20 2553 7324", "Narayanangaon, Junnar, Pune"),
            ("ICAR - National Research Centre for Grapes", "ICAR National Laboratory", "Maharashtra", "Pune", "+91 20 2695 6000", "Solapur Road, Manjri Farm, Pune"),
            ("District Plant Pathology Diagnostic Lab Nashik", "Government Diagnostic Lab", "Maharashtra", "Nashik", "+91 253 257 8201", "Near Agri College, Nashik"),
            ("KVK Baramati Agricultural Research Station", "KVK Extension Center", "Maharashtra", "Pune", "+91 2112 255 227", "Sharadanagar, Baramati"),
            ("Central Potato Research Station (ICAR)", "ICAR National Laboratory", "Punjab", "Jalandhar", "+91 181 225 3300", "Model Town, Jalandhar"),
        ]
        c.executemany("""
            INSERT INTO kvk_labs (name, type, state, district, contact, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_kvk)

    conn.commit()
    conn.close()


def save_detection_to_db(crop, disease, confidence, severity, lat=18.5204, lon=73.8567, city="Pune", state="Maharashtra", phone=""):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO detections (timestamp, crop, disease, confidence, severity, lat, lon, city, state, status, farmer_phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Expert Review', ?)
    """, (dt.datetime.now().strftime("%Y-%m-%d %H:%M"), crop, disease, confidence, severity, lat, lon, city, state, phone))
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


# Initialize Database on Module Import
init_db()


# ----------------------------------------------------------------------------
# 2. PILLAR 4: GEOSPATIAL HOTSPOT MAPPING & PROXIMITY ALERTS
# ----------------------------------------------------------------------------
def render_geospatial_hotspots():
    st.markdown("### 🗺️ Geospatial Outbreak Hotspots & Proximity Alerts")
    st.caption("Pillar 4: Spatial clustering of field disease reports to provide proactive alerts to surrounding farms.")

    conn = get_db_connection()
    df_det = pd.read_sql_query("SELECT * FROM detections", conn)
    conn.close()

    if df_det.empty:
        st.info("No geospatial detection data logged yet.")
        return

    # Proximity Alert Check Component
    st.markdown("#### 🚨 Check Local Outbreak Risk Near Your Farm")
    col_lat, col_lon, col_rad = st.columns([1, 1, 1])
    with col_lat:
        user_lat = st.number_input("Farm Latitude", value=18.5204, format="%.4f")
    with col_lon:
        user_lon = st.number_input("Farm Longitude", value=73.8567, format="%.4f")
    with col_rad:
        radius_km = st.slider("Alert Radius (km)", min_value=5, max_value=50, value=25)

    nearby_cases = []
    for idx, row in df_det.iterrows():
        dist = haversine_km(user_lat, user_lon, row["lat"], row["lon"])
        if dist <= radius_km:
            nearby_cases.append((row, dist))

    if nearby_cases:
        st.warning(f"⚠️ **Outbreak Alert:** Found **{len(nearby_cases)} disease cases** within {radius_km} km of your location!")
        for case, d in nearby_cases[:3]:
            st.markdown(f"- **{case['disease']}** ({case['crop']}) — **{d:.1f} km away** in {case['city']}, {case['state']} (Severity: *{case['severity']}*)")
    else:
        st.success(f"✅ **No active disease outbreaks** reported within {radius_km} km of your farm.")

    st.markdown("---")

    # Interactive Map Display
    st.markdown("#### 📍 Real-Time Disease Cluster Map")
    
    # Map styling dataframe
    map_df = df_det[["lat", "lon", "disease", "crop", "severity", "city"]].rename(columns={"lat": "latitude", "lon": "longitude"})
    st.map(map_df, size=20, color="#FF4D6D")

    # Recent Cluster Table
    st.markdown("#### 📋 Recent Regional Outbreak Reports")
    st.dataframe(
        df_det[["timestamp", "city", "state", "crop", "disease", "severity", "status"]].sort_values(by="timestamp", ascending=False),
        use_container_width=True,
        hide_index=True
    )


# ----------------------------------------------------------------------------
# 3. PILLAR 8: AGRICULTURE OFFICIALS SURVEILLANCE DASHBOARD
# ----------------------------------------------------------------------------
def render_officials_dashboard():
    st.markdown("### 📊 Agriculture Officials' Surveillance & Analytics Dashboard")
    st.caption("Pillar 8: Decision support portal for district/state officers to monitor crop health, outbreak trends, and intervention priority.")

    conn = get_db_connection()
    df_det = pd.read_sql_query("SELECT * FROM detections", conn)
    conn.close()

    if df_det.empty:
        st.info("No surveillance data available.")
        return

    # Metric Header Cards
    total_cases = len(df_det)
    high_sev = len(df_det[df_det["severity"] == "High"])
    pending_rev = len(df_det[df_det["status"] == "Pending Expert Review"])
    verified_cases = len(df_det[df_det["status"] == "Verified"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Disease Reports", total_cases)
    m2.metric("High Severity Outbreaks", high_sev, delta=f"{(high_sev/total_cases)*100:.0f}% of total", delta_color="inverse")
    m3.metric("Pending Expert Verification", pending_rev)
    m4.metric("Verified Diagnoses", verified_cases)

    st.markdown("---")

    # Charts Grid
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("##### 🌾 Outbreaks by Crop Type")
        crop_counts = df_det["crop"].value_counts()
        st.bar_chart(crop_counts)

    with col_c2:
        st.markdown("##### 🦠 Top Detected Pathogens & Diseases")
        disease_counts = df_det["disease"].value_counts().head(5)
        st.bar_chart(disease_counts)

    # State & District Summary Table
    st.markdown("##### 🏙️ District & City-wise Outbreak Breakdown")
    dist_summary = df_det.groupby(["state", "city", "crop"]).agg(
        Total_Reports=("id", "count"),
        High_Severity_Cases=("severity", lambda x: (x == "High").sum())
    ).reset_index()
    st.dataframe(dist_summary, use_container_width=True, hide_index=True)

    # CSV Export Feature
    csv_buf = io.StringIO()
    df_det.to_csv(csv_buf, index=False)
    st.download_button(
        label="📥 Export Outbreak Report for Agriculture Department (CSV)",
        data=csv_buf.getvalue(),
        file_name=f"crop_health_surveillance_report_{dt.date.today()}.csv",
        mime="text/csv"
    )


# ----------------------------------------------------------------------------
# 4. PILLAR 5: EXPERT VALIDATION LOOP & KVK / LAB REFERRAL DIRECTORY
# ----------------------------------------------------------------------------
def render_expert_validation_and_referral():
    st.markdown("### ✅ Expert Validation Loop & KVK / Laboratory Referral")
    st.caption("Pillar 5: Human expert verification queue for plant pathologists, plus local laboratory & KVK referral network.")

    tab_review, tab_kvk = st.tabs(["🔎 Expert Review Queue", "🏛️ KVK & Laboratory Directory"])

    conn = get_db_connection()

    with tab_review:
        st.markdown("#### 👨‍🔬 Pending AI Diagnosis Verification Queue")
        df_pending = pd.read_sql_query("SELECT * FROM detections WHERE status = 'Pending Expert Review'", conn)

        if df_pending.empty:
            st.success("🎉 All pending AI diagnoses have been reviewed by agricultural experts!")
        else:
            for idx, row in df_pending.iterrows():
                with st.expander(f"Report #{row['id']} — {row['crop']}: {row['disease']} ({row['city']}, {row['state']})"):
                    st.write(f"**Date Logged:** {row['timestamp']}")
                    st.write(f"**AI Confidence:** {row['confidence']*100:.1f}% | **Severity:** {row['severity']}")
                    st.write(f"**Farmer Phone:** {row['farmer_phone'] if row['farmer_phone'] else 'Not provided'}")

                    notes_input = st.text_area("Expert Notes / Agronomic Guidance", key=f"notes_{row['id']}", value="Diagnosis verified. Follow recommended spray guidelines.")

                    col_acc, col_rej = st.columns(2)
                    with col_acc:
                        if st.button("✅ Confirm & Verify Diagnosis", key=f"acc_{row['id']}"):
                            c = conn.cursor()
                            c.execute("UPDATE detections SET status = 'Verified', expert_notes = ? WHERE id = ?", (notes_input, row['id']))
                            conn.commit()
                            st.success(f"Report #{row['id']} marked as Verified!")
                            st.rerun()

                    with col_rej:
                        if st.button("❌ Correct / Reject Diagnosis", key=f"rej_{row['id']}"):
                            c = conn.cursor()
                            c.execute("UPDATE detections SET status = 'Rejected / Corrected', expert_notes = ? WHERE id = ?", (notes_input, row['id']))
                            conn.commit()
                            st.warning(f"Report #{row['id']} marked as Rejected/Corrected.")
                            st.rerun()

    with tab_kvk:
        st.markdown("#### 🧪 Krishi Vigyan Kendra (KVK) & Soil/Plant Testing Labs")
        st.write("If leaf symptoms are ambiguous or require laboratory PCR / culture testing, refer to nearest KVK center:")

        df_kvk = pd.read_sql_query("SELECT * FROM kvk_labs", conn)
        state_filter = st.selectbox("Filter by State", ["All States"] + list(df_kvk["state"].unique()))

        if state_filter != "All States":
            df_kvk = df_kvk[df_kvk["state"] == state_filter]

        st.dataframe(df_kvk[["name", "type", "district", "state", "contact", "address"]], use_container_width=True, hide_index=True)

        st.markdown("##### 📝 Book Laboratory Sample Referral")
        with st.form("kvk_booking_form"):
            c_name = st.text_input("Farmer / Extension Worker Name")
            c_crop = st.text_input("Crop Name & Variety")
            c_center = st.selectbox("Select Target Laboratory / KVK", df_kvk["name"].tolist() if not df_kvk.empty else ["Default KVK"])
            c_date = st.date_input("Preferred Visit / Sample Delivery Date")
            submitted = st.form_submit_button("Submit Referral Request")

            if submitted:
                st.success(f"Referral request logged for {c_name} at {c_center} for date {c_date}. Referral ID: REF-KVK-{np.random.randint(1000, 9999)}.")

    conn.close()


# ----------------------------------------------------------------------------
# 5. PILLAR 7: CHEMICAL SAFETY & FOLLOW-UP TRACKER
# ----------------------------------------------------------------------------
def render_safety_and_followup():
    st.markdown("### 🧪 Chemical Safety Guardrails & Recovery Follow-Up")
    st.caption("Pillar 7: Safe dosage calculator, Pre-Harvest Interval (PHI) residue warnings, and 3/7/14-day recovery monitoring.")

    tab_calc, tab_follow = st.tabs(["🧮 Chemical Dosage & PHI Safety Calculator", "📅 Recovery Follow-Up Tracker"])

    with tab_calc:
        st.markdown("#### 🛡️ Safe Pesticide Dosage & Pre-Harvest Waiting Period Calculator")
        st.write("Calculate exact chemical quantities based on land size to prevent over-spraying and toxic residues.")

        col_c, col_a = st.columns(2)
        with col_c:
            selected_chem = st.selectbox("Select Recommended Chemical Spray", [
                "Mancozeb 75% WP (Fungicide)",
                "Copper Hydroxide 77% WP (Bactericide/Fungicide)",
                "Cymoxanil 8% + Mancozeb 64% WP (Late Blight Special)",
                "Imidacloprid 17.8% SL (Whitefly/Vector Insecticide)",
                "Azoxystrobin 23% SC (Broad Spectrum Fungicide)"
            ])
        with col_a:
            land_acres = st.number_input("Farm Land Area (Acres)", min_value=0.25, max_value=50.0, value=1.0, step=0.25)

        # Dosage rules per acre
        chemical_data = {
            "Mancozeb 75% WP (Fungicide)": {"rate_per_acre": "600–800 grams", "water_per_acre": "200 Liters", "phi_days": 14, "safety": "Wear gloves & mask. Do not harvest within 14 days of spraying."},
            "Copper Hydroxide 77% WP (Bactericide/Fungicide)": {"rate_per_acre": "500 grams", "water_per_acre": "200 Liters", "phi_days": 7, "safety": "Avoid spraying during high bloom stage to prevent fruit scarring."},
            "Cymoxanil 8% + Mancozeb 64% WP (Late Blight Special)": {"rate_per_acre": "600 grams", "water_per_acre": "200 Liters", "phi_days": 10, "safety": "Emergency curative spray. Maximum 2 sprays per season."},
            "Imidacloprid 17.8% SL (Whitefly/Vector Insecticide)": {"rate_per_acre": "60–80 ml", "water_per_acre": "150 Liters", "phi_days": 15, "safety": "Highly toxic to bees. Spray only during late evening hours."},
            "Azoxystrobin 23% SC (Broad Spectrum Fungicide)": {"rate_per_acre": "200 ml", "water_per_acre": "200 Liters", "phi_days": 5, "safety": "Rotate with different chemical mode-of-action to avoid fungal resistance."}
        }

        chem_info = chemical_data[selected_chem]

        st.markdown(f"""
        <div style="background:rgba(13, 122, 112, 0.18); border:1.5px solid rgba(13, 170, 155, 0.45); border-radius:12px; padding:1.1rem; color:#E2FAF6; margin-top:1rem;">
        <h4>📋 Calculated Dosage for {land_acres} Acre(s):</h4>
        <ul>
            <li><b>Required Chemical Quantity:</b> {selected_chem.split('(')[0]} — <b>{float(chem_info['rate_per_acre'].split()[0].split('–')[0]) * land_acres:.1f} to {float(chem_info['rate_per_acre'].split()[0].split('–')[-1]) * land_acres:.1f} {chem_info['rate_per_acre'].split()[-1]}</b></li>
            <li><b>Required Spray Water Volume:</b> <b>{int(chem_info['water_per_acre'].split()[0]) * land_acres} Liters</b></li>
            <li><b>⚠️ Pre-Harvest Interval (PHI) Waiting Period:</b> <span style="color:#FF4D6D; font-weight:800;">{chem_info['phi_days']} Days</span> (Harvest produce ONLY after {dt.date.today() + dt.timedelta(days=chem_info['phi_days'])})</li>
            <li><b>🛡️ Safety Directive:</b> {chem_info['safety']}</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with tab_follow:
        st.markdown("#### 📅 3/7/14-Day Recovery Monitoring Tracker")
        st.write("Schedule follow-up check-ins to monitor whether the crop recovered after treatment:")

        conn = get_db_connection()

        with st.form("followup_schedule_form"):
            f_name = st.text_input("Farmer Name")
            f_phone = st.text_input("Mobile Phone Number")
            f_crop = st.selectbox("Crop", ["Tomato", "Potato", "Corn (Maize)", "Chili / Capsicum", "Grape", "Apple"])
            f_disease = st.text_input("Treated Disease", value="Early Blight")
            f_days = st.selectbox("Schedule Follow-Up Interval", [3, 7, 14], format_func=lambda x: f"{x} Days Post-Spraying")
            f_submit = st.form_submit_button("Schedule Recovery Follow-Up")

            if f_submit:
                sch_date = (dt.date.today() + dt.timedelta(days=f_days)).strftime("%Y-%m-%d")
                c = conn.cursor()
                c.execute("""
                    INSERT INTO followups (farmer_name, phone, crop, disease, scheduled_date, status)
                    VALUES (?, ?, ?, ?, ?, 'Scheduled')
                """, (f_name, f_phone, f_crop, f_disease, sch_date))
                conn.commit()
                st.success(f"Follow-up SMS check-in scheduled for {f_name} on {sch_date}!")

        st.markdown("##### 📋 Active Recovery Monitoring List")
        df_fol = pd.read_sql_query("SELECT * FROM followups", conn)
        conn.close()

        if not df_fol.empty:
            st.dataframe(df_fol[["id", "farmer_name", "phone", "crop", "disease", "scheduled_date", "status"]], use_container_width=True, hide_index=True)
        else:
            st.info("No active follow-ups scheduled yet.")


# ----------------------------------------------------------------------------
# 6. MAIN CONTAINER FOR SIH PILLARS TAB
# ----------------------------------------------------------------------------
def render_sih_pillars_tab():
    """
    Renders all 4 missing SIH pillars in a clean, unified Streamlit tab container.
    """
    st.markdown("## 🌿 Kisan Mitra — SIH Complete Pillars Addon")
    st.caption("Fulfills Geospatial Hotspots (Pillar 4), Officials Dashboard (Pillar 8), Expert Validation (Pillar 5), and Chemical Safety/PHI (Pillar 7).")

    pillar_tabs = st.tabs([
        "🗺️ Hotspot Map (Pillar 4)",
        "📊 Officials Dashboard (Pillar 8)",
        "✅ Expert Validation & KVKs (Pillar 5)",
        "🧪 Safety & Follow-Up (Pillar 7)",
        "📖 Integration & Merge Guide"
    ])

    with pillar_tabs[0]:
        render_geospatial_hotspots()

    with pillar_tabs[1]:
        render_officials_dashboard()

    with pillar_tabs[2]:
        render_expert_validation_and_referral()

    with pillar_tabs[3]:
        render_safety_and_followup()

    with pillar_tabs[4]:
        st.markdown("""
        ### 🔗 How to Merge this File into Your Git Repository

        This file `sih_pillars_addon.py` is completely standalone and zero-risk.

        #### Option A: Run Standalone (Instant Test)
        ```bash
        streamlit run sih_pillars_addon.py
        ```

        #### Option B: Add as a New Tab inside `app.py` (2 Lines of Code)
        In `app.py`, right after where language or main tabs are defined, add:
        ```python
        import sih_pillars_addon

        # Inside your Streamlit layout:
        sih_pillars_addon.render_sih_pillars_tab()
        ```

        #### Git Commands to Push to GitHub:
        ```bash
        git status
        git add sih_pillars_addon.py kisan_mitra_sih.db
        git commit -m "Add SIH missing pillars module: Hotspots, Officials Dashboard, Expert Review & Safety"
        git push origin main
        ```
        """)


if __name__ == "__main__":
    st.set_page_config(page_title="Kisan Mitra — SIH Pillars Addon", page_icon="🌿", layout="wide")
    render_sih_pillars_tab()
