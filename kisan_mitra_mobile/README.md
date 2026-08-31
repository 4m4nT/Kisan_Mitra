# Kisan Mitra Mobile (किसान मित्र) 🌾📱
### 100% Standalone Offline AI Crop Doctor & Mobile Application

This folder contains the complete standalone mobile application project with on-device AI model inference, zero server dependency, and automated APK build workflows.

---

## 🌟 Architecture Overview

```
kisan_mitra_mobile/
├── standalone/                  # 100% Offline On-Device Mobile App
│   ├── index.html               # Earthy Precision Glass Mobile UI
│   ├── styles.css               # Responsive Glassmorphic Mobile Design
│   ├── app_offline.js           # In-browser/On-device ONNX vision inference
│   ├── disease_data.json        # 38-class agronomic guide & remedies (HI & EN)
│   ├── classes.json             # 38 disease labels
│   ├── manifest.json & sw.js    # Progressive Web App offline caching
│   └── models/
│       └── cropguard.onnx       # 94MB Deep Learning Vision Model
│
├── backend/                     # Optional High-Speed FastAPI Service (if hosted)
│   ├── main.py                  # REST API endpoints
│   ├── model_optimizer.py       # Graph-optimized ONNX runtime engine
│   └── database.py              # SQLite storage
│
└── .github/workflows/
    └── build_apk.yml            # Automated GitHub Actions Cloud APK Builder
```

---

## 📲 How to Get & Install the Standalone APK

### Method 1: Automatic GitHub Actions APK Builder (Zero Setup)
1. Push this repository to your GitHub account (`git push origin main`).
2. Go to your GitHub repository $\rightarrow$ click the **Actions** tab.
3. The **"Build Android APK (Kisan Mitra)"** workflow will run automatically.
4. Click on the completed workflow run $\rightarrow$ download the **`KisanMitra-AI-Doctor.apk`** artifact.
5. Send the `.apk` file to any Android phone via WhatsApp, Bluetooth, or Google Drive, tap to install, and run!

---

### Method 2: Instant 100% Offline PWA (No Build Needed)
1. Open `kisan_mitra_mobile/standalone/index.html` in your phone browser (Chrome on Android / Safari on iOS).
2. Tap **Menu (⋮)** $\rightarrow$ **"Add to Home screen"** or **"Install App"**.
3. It installs directly on the phone launcher with full native camera and offline on-device AI support!

---

### Method 3: Build Locally with Android Studio (If Android SDK installed)
```bash
cd kisan_mitra_mobile/standalone
npm install -g @capacitor/cli @capacitor/core @capacitor/android
npx cap init "Kisan Mitra" "org.sih.kisanmitra" --web-dir "."
npx cap add android
npx cap open android
# In Android Studio: Click Build -> Build Bundle(s) / APK(s) -> Build APK(s)
```
