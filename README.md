# Kisan Mitra AI — Prototype
Made by AmanTomar
A working end-to-end precision agri-tech application: leaf photo → **38-Class Deep Learning Vision Diagnosis (ResNet-50)** → live weather (Open-Meteo) → outbreak risk forecasting → planting advice → (simulated/live) SMS alert, in English/Hindi with voice read-out and interactive Crop Doctor Chat.

**AI Vision Model Active:** The app now runs a real 38-class ResNet-50 convolutional neural network (`models/cropguard.onnx`) trained on the PlantVillage crop dataset for instant offline/edge inference.

## 1. Run it locally (5 minutes)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

It opens at `http://localhost:8501`. Upload a leaf photo (any photo works for the
demo — try a plain green background vs. a brownish one to see the risk/diagnosis
change), type a town/city name, and pick a crop.

## 2. Put it in front of your team/mentors today

Easiest free options, no server management:
- **Streamlit Community Cloud** (streamlit.io/cloud): push this folder to a public
  GitHub repo, connect the repo, deploy — you get a shareable `*.streamlit.app` link.
- **Hugging Face Spaces**: create a Space with the Streamlit SDK, upload these files.

Either gives you a live link you can share instead of screen-sharing.

## 3. Building this further with Google Antigravity (free)

[Antigravity](https://antigravity.google) is Google's free agentic IDE (VS Code-based)
— you give it a task, it plans, writes, and tests code across files while you review.
It's a good fit for extending this prototype because you can hand it one feature at a
time and check its work.

Steps:
1. Install Antigravity from antigravity.google/download and sign in with a Google account.
2. Open this project folder in Antigravity.
3. Use the agent panel for scoped tasks, e.g.:
   - *"Replace the classify_leaf() heuristic in app.py with a real Keras model loaded
     from keras_model.h5, keeping the same function signature and CLASS_NAMES list."*
   - *"Add a third language (e.g. Marathi) to the TEXT dictionary in app.py, translating
     every key from the English block."*
   - *"Add a results-history page that shows the last 5 diagnoses cached in
     st.session_state, for the offline-mode story."*
4. Review every diff before accepting — treat it like a junior developer's PR, not
   an autopilot. Ask it to explain any function you don't follow.
5. Keep tasks small and testable (one feature per request) rather than "build the
   whole app" — it stays easier to review and debug that way.

## 4. Next step for a real disease model (still free)

1. Go to https://teachablemachine.withgoogle.com/ → "Image Project".
2. Get a labeled leaf dataset — the PlantVillage dataset on Kaggle is the standard
   free starting point (search "PlantVillage dataset kaggle").
3. Upload a few hundred images per class (healthy / early blight / late blight / etc.),
   train in-browser (a few minutes), export as **TensorFlow → Keras**.
4. Drop the exported `keras_model.h5` and `labels.txt` next to `app.py`, and swap in
   the real-model version of `classify_leaf()` (code snippet is in `app.py`'s comments).

This gets you from "heuristic demo" to "real trained model" without writing training
code yourself — good enough to show meaningful accuracy numbers to mentors.

## 5. Turning the risk score into a real forecasting model (later)

The current `compute_outbreak_risk()` uses simple, transparent thresholds (humid
days, wet days, average min temperature) loosely based on the fact that many fungal
blights favor cool, humid, wet spells. For the full product, replace this with a
calibrated epidemiological model (e.g., a degree-day accumulation or infection-period
model specific to each disease), ideally reviewed with an agronomist, and back-test it
against real reported outbreak dates before trusting its lead-time claims.

## 6. Real SMS alerts

Sign up for a free Twilio trial (twilio.com/try-twilio), grab your Account SID, Auth
Token, and trial phone number, then add to `.streamlit/secrets.toml`:

```toml
TWILIO_SID = "..."
TWILIO_TOKEN = "..."
TWILIO_FROM = "+1..."
```

`send_sms()` in `app.py` will automatically start sending real messages once these
secrets are present — no code change needed. `pip install twilio` first.

## File overview

| File | Purpose |
|---|---|
| `app.py` | The whole app — UI, heuristic classifier, weather, risk logic, planting advice, TTS, SMS |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |
