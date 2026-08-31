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
# 0. PAGE CONFIGURATION (Mobile App Viewport)
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Kisan Mitra — AI Precision Crop Doctor",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------------------------------
# THEME — Frosted Glassmorphism Mobile-Optimized Design System
# ----------------------------------------------------------------------------
GLASS_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,100..900;1,9..144,100..900&family=Plus+Jakarta+Sans:ital,wght@0,200..800;1,200..800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

:root {
  /* Earthy Precision Glass — Deep Forest Palette */
  --km-bg: #081611;
  --km-surface: rgba(8, 22, 17, 0.6);
  --km-surface-container: #14221d;
  --km-surface-container-low: #101e19;
  --km-surface-container-high: #1f2d27;
  --km-surface-container-highest: #293832;
  --km-surface-bright: #2e3c36;
  --km-primary: #7dd6ca;
  --km-primary-container: #0d7a70;
  --km-on-primary: #003732;
  --km-on-primary-container: #acfff3;
  --km-secondary: #ffb4a2;
  --km-secondary-container: #7f2f1a;
  --km-on-secondary: #5e1705;
  --km-tertiary: #f7bd4e;
  --km-tertiary-container: #8f6500;
  --km-error: #ffb4ab;
  --km-error-container: #93000a;
  --km-on-error-container: #ffdad6;
  --km-on-surface: #d6e6dd;
  --km-on-surface-variant: #bdc9c6;
  --km-outline: #889390;
  --km-outline-variant: #3e4947;
  --km-glass-border: rgba(125, 214, 202, 0.2);
  --km-glass-border-light: rgba(125, 214, 202, 0.35);
  --km-glass-card-bg: rgba(13, 122, 112, 0.15);
  --km-glass-blur: blur(40px);
}

html, body, [data-testid="stAppViewContainer"] {
  background: #081611 !important;
  background-image:
    linear-gradient(to bottom, rgba(8, 22, 17, 0.8), rgba(8, 22, 17, 0.95)),
    url('https://lh3.googleusercontent.com/aida-public/AB6AXuBOp55tEUenrJNVAw8j15lavmwFbHJ5k-4YpJkkmmD_AKM0Jm0qHAHOI0sKzuRvl_5QoS_72vDlHDUpJq5nzDuagM_TaombnLqe9FZBmY1U3obl5N_Le9O9cnv43XPuZf58m1z43tJCy3eyFp7lj4qSe6-o16S_vMwaREdUU5fYnHftCSZ-iO51OkGj91y0d2XjexYuqWbRJ95t2PaGNzyz5p2yP6f5hT5nfxn5UccO8aMs-I3hv7-Q') !important;
  background-size: cover !important;
  background-position: center !important;
  background-attachment: fixed !important;
  color: var(--km-on-surface) !important;
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
  letter-spacing: 0 !important;
}

[data-testid="stHeader"] {
  background: rgba(8, 22, 17, 0.80) !important;
  backdrop-filter: blur(40px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(40px) saturate(180%) !important;
  border-bottom: 1px solid rgba(255,255,255,0.05) !important;
}

/* Mobile App Viewport Framing */
section.main .block-container {
  max-width: 680px !important;
  width: 100%;
  padding-top: 0.65rem;
  padding-bottom: 3.5rem;
  padding-left: clamp(0.75rem, 3.5vw, 1.25rem);
  padding-right: clamp(0.75rem, 3.5vw, 1.25rem);
  margin: 0 auto;
}

/* ═══════ Welcome / Splash Screen ═══════ */
.km-welcome-wrapper {
  position: relative;
  width: 100%;
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  padding-bottom: 2.5rem;
  overflow: hidden;
  border-radius: 24px;
}
.km-welcome-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  border-radius: 24px;
  overflow: hidden;
}
.km-welcome-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.km-welcome-bg .km-welcome-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(8,22,17,0.85) 0%, rgba(8,22,17,0.25) 40%, transparent 70%);
}
.km-welcome-card {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 400px;
  background: var(--km-surface);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 2.5rem;
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 32px 64px rgba(0,0,0,0.3);
}
.km-welcome-pretitle {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 1rem;
  font-weight: 500;
  color: var(--km-on-surface-variant);
  margin-bottom: 0.15rem;
}
.km-welcome-title {
  font-family: 'Fraunces', serif;
  font-size: clamp(2.2rem, 8vw, 3rem);
  font-weight: 700;
  color: var(--km-primary);
  letter-spacing: -0.02em;
  line-height: 1.15;
  margin-bottom: 0.45rem;
}
.km-welcome-sub {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--km-on-surface-variant);
  margin-bottom: 2rem;
}
.km-welcome-leaf {
  display: inline-block;
  margin-bottom: 0.5rem;
  font-size: 1.6rem;
}

/* ═══════ Glass Top App Bar ═══════ */
.km-glass-app-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(8, 22, 17, 0.50);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding: 0.65rem 1.15rem;
  border-radius: 0;
  margin-bottom: 1rem;
  margin-left: calc(-1 * clamp(0.75rem, 3.5vw, 1.25rem));
  margin-right: calc(-1 * clamp(0.75rem, 3.5vw, 1.25rem));
  margin-top: -0.65rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}
.km-brand-wrap {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.km-glass-logo {
  font-size: 1.5rem;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.km-brand-name {
  font-family: 'Fraunces', serif;
  font-weight: 700;
  font-size: 1.3rem;
  color: var(--km-primary);
  line-height: 1.15;
  letter-spacing: -0.02em;
}
.km-brand-sub {
  font-size: 0.7rem;
  color: var(--km-on-surface-variant);
  font-weight: 500;
}
.km-glass-status {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--km-primary);
  background: rgba(13, 122, 112, 0.15);
  border: 1px solid rgba(125, 214, 202, 0.25);
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.km-status-beacon {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--km-primary);
  box-shadow: 0 0 8px var(--km-primary);
  animation: pulse-beacon 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
}
@keyframes pulse-beacon {
  0% { transform: scale(0.8); opacity: 0.5; }
  80%, 100% { transform: scale(2); opacity: 0; }
}

/* ═══════ Earthy Glass Card Architecture ═══════ */
.km-glass-card {
  background: var(--km-glass-card-bg) !important;
  backdrop-filter: var(--km-glass-blur) !important;
  -webkit-backdrop-filter: var(--km-glass-blur) !important;
  border: 1px solid var(--km-glass-border) !important;
  border-radius: 1rem !important;
  padding: clamp(1rem, 3.5vw, 1.5rem);
  margin-bottom: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37) !important;
  position: relative;
  overflow: hidden;
  transition: all 0.25s ease;
}
.km-glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, rgba(125,214,202,0.4), transparent);
  pointer-events: none;
}

/* ═══════ Glass Hero Banner ═══════ */
.km-glass-hero {
  background: var(--km-glass-card-bg);
  backdrop-filter: var(--km-glass-blur);
  -webkit-backdrop-filter: var(--km-glass-blur);
  border: 1px solid var(--km-glass-border);
  border-radius: 1rem;
  padding: clamp(1.2rem, 3.5vw, 1.6rem) clamp(1rem, 3vw, 1.35rem);
  text-align: center;
  position: relative;
  overflow: hidden;
  margin-bottom: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}
.km-glass-hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(125, 214, 202, 0.1) 0%, transparent 50%);
  pointer-events: none;
}
.km-hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--km-primary);
  background: rgba(13, 122, 112, 0.15);
  border: 1px solid rgba(125, 214, 202, 0.25);
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.km-hero-title {
  font-family: 'Fraunces', serif;
  font-weight: 600;
  font-size: clamp(1.55rem, 5vw, 2rem);
  line-height: 1.24;
  color: #FFFFFF;
  margin-bottom: 0.45rem;
  letter-spacing: -0.02em;
}
.km-hero-sub {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: clamp(0.82rem, 2.5vw, 0.9rem);
  color: var(--km-on-surface-variant);
  max-width: 520px;
  margin: 0 auto 1.1rem auto;
  line-height: 1.55;
}

/* ═══════ Glass Pipeline Strip ═══════ */
.km-pipeline {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  margin-top: 1rem;
}
@media (max-width: 520px) {
  .km-pipeline {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.45rem;
  }
}
.km-pipe-node {
  background: rgba(20, 34, 29, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid var(--km-outline-variant);
  border-radius: 1rem;
  padding: 0.65rem 0.4rem;
  text-align: center;
  transition: all 0.2s ease;
}
.km-pipe-node:hover {
  background: rgba(13, 122, 112, 0.12);
  border-color: var(--km-glass-border-light);
}
.km-pipe-icon {
  font-size: 1.15rem;
  margin-bottom: 0.2rem;
}
.km-pipe-title {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 700;
  font-size: 0.76rem;
  color: var(--km-on-surface);
}
.km-pipe-sub {
  font-size: 0.66rem;
  color: var(--km-outline);
}

/* ═══════ Card Header ═══════ */
.km-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.95rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--km-outline-variant);
}
.km-card-title {
  font-family: 'Fraunces', serif;
  font-weight: 600;
  font-size: clamp(1.1rem, 3vw, 1.25rem);
  color: var(--km-primary);
  display: flex;
  align-items: center;
  gap: 0.45rem;
}
.km-card-sub {
  font-size: 0.78rem;
  color: var(--km-on-surface-variant);
}

/* ═══════ Glass Dropzone & Form Controls ═══════ */
[data-testid="stFileUploaderDropzone"], [data-testid="stCameraInput"] {
  background: rgba(20, 34, 29, 0.5) !important;
  backdrop-filter: blur(24px) !important;
  border: 2px dashed var(--km-outline-variant) !important;
  border-radius: 1rem !important;
  padding: 1.2rem 1rem !important;
  transition: all 0.3s ease !important;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.15) !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: var(--km-primary) !important;
  background: rgba(13, 122, 112, 0.08) !important;
  box-shadow: 0 0 20px rgba(125, 214, 202, 0.15) !important;
}
.stTextInput input, .stSelectbox [data-baseweb="select"] {
  background: rgba(20, 34, 29, 0.5) !important;
  backdrop-filter: blur(12px) !important;
  color: var(--km-on-surface) !important;
  border: 1px solid var(--km-outline-variant) !important;
  border-radius: 1rem !important;
  font-size: 0.88rem !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stTextInput input:focus, .stSelectbox [data-baseweb="select"]:focus {
  border-color: var(--km-primary) !important;
  box-shadow: 0 0 12px rgba(125, 214, 202, 0.25) !important;
}

/* ═══════ Primary Button — Terracotta Gradient ═══════ */
.stButton>button {
  background: linear-gradient(135deg, var(--km-secondary-container), #631906) !important;
  color: #FFFFFF !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 700 !important;
  border: 1px solid rgba(255, 180, 162, 0.20) !important;
  border-radius: 999px !important;
  padding: 0.7rem 1.5rem !important;
  font-size: 0.88rem !important;
  letter-spacing: 0.01em !important;
  width: 100% !important;
  box-shadow: 0 4px 12px rgba(255, 180, 162, 0.2) !important;
  transition: all 0.3s ease !important;
}
.stButton>button:hover {
  transform: translateY(-1px) !important;
  box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.2), 0 6px 18px rgba(255, 180, 162, 0.3) !important;
}

/* ═══════ Secondary / Outline Button ═══════ */
.km-btn-outline {
  background: transparent !important;
  border: 1.5px solid var(--km-primary) !important;
  color: var(--km-primary) !important;
  border-radius: 999px;
  padding: 0.6rem 1.4rem;
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.3s ease;
}
.km-btn-outline:hover {
  background: rgba(125, 214, 202, 0.1) !important;
}

/* ═══════ Diagnostic Report ═══════ */
.km-diag-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.km-glass-pill {
  background: var(--km-glass-card-bg);
  backdrop-filter: var(--km-glass-blur);
  border: 1px solid var(--km-glass-border);
  border-radius: 1rem;
  padding: 1rem 1.15rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
}
.km-glass-pill::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(125,214,202,0.08) 0%, transparent 50%);
  pointer-events: none;
}
.km-glass-pill.danger {
  background: rgba(147, 0, 10, 0.15);
  border-color: rgba(255, 180, 171, 0.30);
}
.km-glass-pill.danger::before {
  background: linear-gradient(135deg, rgba(255, 180, 171, 0.08) 0%, transparent 50%);
}
.km-glass-pill.healthy {
  background: rgba(13, 122, 112, 0.15);
  border-color: rgba(125, 214, 202, 0.30);
}

.km-diag-header-tag {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.35rem;
}
.km-glass-pill.danger .km-diag-header-tag { color: var(--km-error); }
.km-glass-pill.healthy .km-diag-header-tag { color: var(--km-primary); }

.km-diag-name {
  font-family: 'Fraunces', serif;
  font-weight: 600;
  font-size: clamp(1.15rem, 3.5vw, 1.35rem);
  color: var(--km-on-surface);
  line-height: 1.3;
}
.km-diag-desc {
  font-size: 0.85rem;
  color: var(--km-on-surface-variant);
  margin-top: 0.4rem;
  line-height: 1.5;
}

/* ═══════ Confidence Gauge — Harvest Gold Ring ═══════ */
.km-conf-container {
  margin: 0.55rem 0 0.2rem 0;
}
.km-conf-bar-bg {
  background: var(--km-surface-container-highest);
  border-radius: 999px;
  height: 8px;
  width: 100%;
  overflow: hidden;
}
.km-conf-bar-fill {
  background: linear-gradient(90deg, var(--km-primary) 0%, var(--km-tertiary) 100%);
  height: 100%;
  border-radius: 999px;
  box-shadow: 0 0 8px rgba(247, 189, 78, 0.5);
}

/* ═══════ Microclimate Weather Ribbon ═══════ */
.km-weather-ribbon {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-bottom: 0.8rem;
}
.km-w-chip {
  background: rgba(20, 34, 29, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid var(--km-outline-variant);
  border-radius: 999px;
  padding: 0.32rem 0.8rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--km-on-surface);
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

/* ═══════ Glass Chat Container ═══════ */
.km-chat-container {
  background: var(--km-glass-card-bg);
  backdrop-filter: var(--km-glass-blur);
  -webkit-backdrop-filter: var(--km-glass-blur);
  border: 1px solid var(--km-glass-border);
  border-radius: 1rem;
  padding: 1.15rem;
  margin-top: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}
.km-chat-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, rgba(125,214,202,0.4), transparent);
  pointer-events: none;
}
[data-testid="stChatMessage"] {
  background: rgba(20, 34, 29, 0.45) !important;
  backdrop-filter: blur(12px) !important;
  border: 1px solid var(--km-outline-variant) !important;
  border-radius: 1rem !important;
  margin-bottom: 0.5rem !important;
  padding: 0.75rem 1rem !important;
}

/* ═══════ Glass Tabs — Earthy Nav Bar ═══════ */
[data-testid="stTabs"] {
  margin-bottom: 1rem;
}
[data-baseweb="tab-list"] {
  background: rgba(8, 22, 17, 0.50) !important;
  backdrop-filter: blur(40px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(40px) saturate(180%) !important;
  border: 1px solid rgba(255, 255, 255, 0.05) !important;
  padding: 4px !important;
  border-radius: 1rem !important;
  gap: 3px !important;
  box-shadow: 0 8px 26px rgba(0, 0, 0, 0.25) !important;
  overflow-x: auto !important;
}
[data-baseweb="tab"] {
  border-radius: 0.75rem !important;
  color: var(--km-on-surface-variant) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.78rem !important;
  padding: 0.45rem 0.85rem !important;
  border: 1px solid transparent !important;
  background: transparent !important;
  white-space: nowrap !important;
  transition: all 0.2s ease !important;
}
[data-baseweb="tab"]:hover {
  color: var(--km-on-surface) !important;
  background: rgba(125, 214, 202, 0.06) !important;
}
[aria-selected="true"] {
  background: var(--km-primary-container) !important;
  color: var(--km-on-primary-container) !important;
  border: 1px solid transparent !important;
  font-weight: 700 !important;
  box-shadow: 0 2px 8px rgba(13, 122, 112, 0.3) !important;
}

/* ═══════ Glass Error Alert ═══════ */
.km-glass-error {
  background: rgba(147, 0, 10, 0.15);
  backdrop-filter: blur(24px);
  border: 1.5px solid rgba(255, 180, 171, 0.30);
  border-radius: 1rem;
  padding: 1.2rem;
  text-align: center;
  margin-bottom: 1rem;
  box-shadow: 0 8px 24px rgba(147, 0, 10, 0.15);
  position: relative;
  overflow: hidden;
}
.km-glass-error::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, rgba(255,180,171,0.4), transparent);
  pointer-events: none;
}
.km-error-badge {
  display: inline-block;
  background: var(--km-error-container);
  color: var(--km-on-error-container);
  font-weight: 700;
  font-size: 0.68rem;
  padding: 0.2rem 0.75rem;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.4rem;
  border: 1px solid rgba(255, 180, 171, 0.2);
}

/* ═══════ Global Overrides ═══════ */
h1, h2, h3, h4, h5, h6 {
  font-family: 'Fraunces', serif !important;
  color: var(--km-on-surface) !important;
}
p, span, div, label {
  font-family: 'Plus Jakarta Sans', sans-serif;
}
[data-testid="stSidebar"] {
  background: var(--km-surface-container-low) !important;
  border-right: 1px solid var(--km-outline-variant) !important;
}
</style>
"""
st.markdown(GLASS_THEME_CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# LOCALIZATION (English & Hindi)
# ----------------------------------------------------------------------------
TEXT = {
    "en": {
        "app_name": "Kisan Mitra",
        "app_tagline": "AI Precision Crop Doctor",
        "system_ready": "AI Model Ready",
        "hero_badge": "ResNet-50 Vision • Outbreak Radar",
        "hero_title": "Instant AI Crop Disease Diagnosis",
        "hero_sub": "Scan plant leaves for instant pathology classification across 38+ crop conditions, tailored curative treatment, and microclimate risk alerts.",
        "how_title": "Diagnostic Workflow",
        "how1_title": "1. Leaf Scan",
        "how1_desc": "Camera / Upload",
        "how2_title": "2. Neural Net",
        "how2_desc": "Tissue scan",
        "how3_title": "3. Diagnosis",
        "how3_desc": "Identifies pathogen",
        "how4_title": "4. Treatment",
        "how4_desc": "Prescription & Chat",
        "camera_tab": "📷 Phone Camera (Snap Photo)",
        "upload_tab": "📁 Gallery / File Upload",
        "upload_title": "Leaf Scanner",
        "upload_sub": "Use your phone camera or upload a clear leaf photo for neural network analysis",
        "detect_btn": "Diagnose Crop Disease",
        "results_title": "Diagnostic Report",
        "disease_identified": "Pathology Identified",
        "confidence_level": "Confidence Level",
        "expert_advice": "Clinical Treatment Plan",
        "invalid_photo_title": "Non-Crop Image Detected",
        "invalid_photo_badge": "Validation Alert",
        "invalid_photo_msg": "The image uploaded does not contain sufficient organic crop leaf tissue.",
        "invalid_photo_sub": "Please take a close, well-lit photo of a single crop leaf.",
        "weather_title": "Microclimate & Outbreak Forecast",
        "planting_title": "Sowing & Agricultural Advisory",
        "listen_btn": "🔊 Voice Prescription",
        "chat_title": "Kisan Mitra Clinical AI Assistant",
        "chat_placeholder": "Ask about spray dosages, organic remedies, PHI wait times...",
    },
    "hi": {
        "app_name": "किसान मित्र",
        "app_tagline": "एआई फसल डॉक्टर व सर्विलांस",
        "system_ready": "एआई इंजन तैयार",
        "hero_badge": "न्यूरल विजन • लाइव मौसम रडार",
        "hero_title": "एआई द्वारा सटीक फसल रोग जांच",
        "hero_sub": "पत्ती की फोटो खींचें और 38+ फसल रोगों की तुरंत पहचान, विशेषज्ञ दवा उपचार, छिड़काव खुराक व मौसम आधारित चेतावनी पाएं।",
        "how_title": "जांच प्रक्रिया",
        "how1_title": "1. फोटो लें",
        "how1_desc": "कैमरा / गैलरी",
        "how2_title": "2. एआई जांच",
        "how2_desc": "न्यूरल विश्लेषण",
        "how3_title": "3. रोग रिपोर्ट",
        "how3_desc": "सटीक परिणाम",
        "how4_title": "4. समाधान",
        "how4_desc": "दवा व सलाह",
        "camera_tab": "📷 मोबाइल कैमरा (लाइव फोटो लें)",
        "upload_tab": "📁 गैलरी से फोटो चुनें",
        "upload_title": "लीफ स्कैनर",
        "upload_sub": "फोन कैमरे से फोटो खींचें या गैलरी से फसल की पत्ती अपलोड करें",
        "detect_btn": "फसल रोग की पहचान करें",
        "results_title": "रोग निदान रिपोर्ट",
        "disease_identified": "पहचाना गया रोग",
        "confidence_level": "विश्वसनीयता स्तर",
        "expert_advice": "उपचार व छिड़काव सलाह",
        "invalid_photo_title": "अमान्य फोटो अपलोड हुई",
        "invalid_photo_badge": "जांच सूचना",
        "invalid_photo_msg": "अपलोड की गई फोटो किसी फसल की पत्ती की प्रतीत नहीं होती।",
        "invalid_photo_sub": "कृपया अच्छी रोशनी में केवल फसल की पत्ती की स्पष्ट फोटो अपलोड करें।",
        "weather_title": "लाइव मौसम व रोग प्रकोप जोखिम",
        "planting_title": "बुवाई व कृषि कैलेंडर सलाह",
        "listen_btn": "🔊 बोलकर सुनें",
        "chat_title": "किसान मित्र एआई सहायक",
        "chat_placeholder": "फसल रोग, दवा की खुराक या जैविक उपचार के बारे में पूछें...",
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


def is_valid_crop_leaf(image: Image.Image, lang: str = "en"):
    """
    Advanced Botanical Leaf Validation & Synthetic Non-Plant Object (OOD) Filter.
    Rejects green cars, plastic toys, painted walls, textiles, animals, screens, and vehicles.
    """
    img_rgb = image.convert("RGB")
    arr_224 = np.asarray(img_rgb.resize((224, 224)), dtype=np.float32) / 255.0
    r, g, b = arr_224[..., 0], arr_224[..., 1], arr_224[..., 2]

    # HSV Botanical Color Space Analysis
    hsv = img_rgb.resize((224, 224)).convert("HSV")
    hsv_arr = np.asarray(hsv, dtype=np.float32)
    h = hsv_arr[..., 0] / 255.0 * 360.0
    s = hsv_arr[..., 1] / 255.0
    v = hsv_arr[..., 2] / 255.0

    # 1. Photosynthetic Chlorophyll
    exg = 2.0 * g - r - b
    green_veg = (exg > 0.025) & (s >= 0.12) & (v >= 0.08) & (v <= 0.94) & (h >= 35) & (h <= 160)

    # 2. Organic Foliar Chlorosis
    yellow_chlorosis = (h >= 28) & (h <= 65) & (s >= 0.18) & (v >= 0.20) & (r > b + 0.08)

    # 3. Organic Necrotic Blight / Rust / Brown Lesions
    brown_necrosis = (
        (h >= 10) & (h <= 38) & (s >= 0.18) & (v >= 0.10) & (v <= 0.75) & (r > g) & (g > b * 1.10)
    )

    plant_mask = green_veg | yellow_chlorosis | brown_necrosis
    foliage_ratio = float(plant_mask.sum()) / (224.0 * 224.0)

    # 4. Specular Metallic / Vehicle Paint / Glass Reflections
    # Cars & plastic exhibit intense specular gloss highlights surrounded by solid paint
    specular_metallic = (v > 0.90) & (s < 0.15) & (r > 0.80) & (g > 0.80) & (b > 0.80)
    specular_ratio = float(specular_metallic.sum()) / (224.0 * 224.0)

    # 5. Non-organic Sky / Blue Surface
    blue_cyan = (b > r * 1.25) & (b > g * 1.10) & (b > 0.25) & (h >= 180) & (h <= 265)
    blue_ratio = float(blue_cyan.sum()) / (224.0 * 224.0)

    # 6. Synthetic Violet / Magenta / Neon
    synthetic_violet = (h >= 270) & (h <= 340) & (s >= 0.25)
    synthetic_ratio = float(synthetic_violet.sum()) / (224.0 * 224.0)

    # 7. Biological Micro-Texture & Gradient Complexity
    # Plant leaf tissue contains natural cellular veins, stomata, and mesophyll micro-gradients.
    # Synthetic flat painted surfaces (like cars, plastic, walls) have unnaturally flat, uniform patches.
    grad_x = np.abs(arr_224[:, 1:, :] - arr_224[:, :-1, :])
    grad_y = np.abs(arr_224[1:, :, :] - arr_224[:-1, :, :])
    texture_complexity = float(np.mean(grad_x) + np.mean(grad_y))

    # 8. Biological Chlorophyll Hue Variance
    # Real leaves have biological hue gradients (veins, lighting, leaf edges).
    # Synthetic car paint or plastic has unnaturally monolithic hue with zero biological variance.
    if foliage_ratio > 0.15:
        green_hues = h[green_veg]
        hue_std = float(np.std(green_hues)) if len(green_hues) > 50 else 0.0
    else:
        hue_std = 0.0

    # Rule A: Insufficient plant foliage
    if foliage_ratio < 0.12:
        reason = (
            "Non-plant object detected. Insufficient crop leaf tissue."
            if lang != "hi"
            else "गाड़ी, वस्तु या गैर-पौधे की फोटो पहचानी गई। केवल फसल की पत्ती अपलोड करें।"
        )
        return False, reason

    # Rule B: High Sky/Screen Blue or Synthetic Colors
    if blue_ratio > 0.30 and foliage_ratio < 0.20:
        reason = (
            "Detected sky, digital screen, or blue non-plant surface."
            if lang != "hi"
            else "स्क्रीन, आसमान या नीली गैर-जैविक वस्तु पहचानी गई।"
        )
        return False, reason

    if synthetic_ratio > 0.18:
        reason = (
            "Detected synthetic non-botanical colors."
            if lang != "hi"
            else "अप्राकृतिक कृत्रिम रंग पहचाना गया।"
        )
        return False, reason

    # Rule C: Synthetic Green Object / Car Paint Rejection
    # Flat texture + metallic specular highlights OR unnaturally monolithic synthetic paint hue
    if (specular_ratio > 0.08 and texture_complexity < 0.038) or (hue_std < 3.2 and foliage_ratio > 0.40 and texture_complexity < 0.032):
        reason = (
            "Synthetic painted object or vehicle detected. Please upload a real botanical crop leaf."
            if lang != "hi"
            else "कृत्रिम रंग, गाड़ी या धातु की सतह पहचानी गई। कृपया असली फसल की पत्ती की फोटो अपलोड करें।"
        )
        return False, reason

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

        # Botanical lesion morphology calibration
        r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
        brown_spots = (r > 0.28) & (g > 0.18) & (b < 0.26) & (r > b * 1.35)
        brown_ratio = float(brown_spots.sum()) / (224.0 * 224.0)

        calibrated_logits = raw_logits.copy()
        if brown_ratio > 0.12:
            for i, c in enumerate(classes):
                if "Early_blight" in c:
                    calibrated_logits[i] += 3.4
                elif "Target_Spot" in c or "Septoria" in c:
                    calibrated_logits[i] += 1.4
                elif c == "Grape___Black_rot" and selected_crop != "Grape":
                    calibrated_logits[i] -= 2.2

        global_max_logit = float(np.max(calibrated_logits))
        global_exp = np.exp((calibrated_logits - global_max_logit) / 0.65)
        global_probs = global_exp / global_exp.sum()
        global_top_idx = int(np.argmax(global_probs))
        global_top_prob = float(global_probs[global_top_idx])
        global_top_class = classes[global_top_idx]

        prefix = CROP_PREFIX_MAP.get(selected_crop)
        if prefix:
            matching_indices = [i for i, c in enumerate(classes) if c.startswith(prefix)]
            if matching_indices:
                sub_logits = calibrated_logits[matching_indices]
                max_sub_logit = float(np.max(sub_logits))

                if global_max_logit > 3.5 and not global_top_class.startswith(prefix) and global_top_prob > 0.75:
                    top_idx = global_top_idx
                    confidence = global_top_prob
                else:
                    sub_exp = np.exp((sub_logits - max_sub_logit) / 0.65)
                    norm_sub_probs = sub_exp / sub_exp.sum()
                    sub_top_idx = int(np.argmax(norm_sub_probs))
                    top_idx = matching_indices[sub_top_idx]
                    confidence = float(norm_sub_probs[sub_top_idx])
            else:
                top_idx = global_top_idx
                confidence = global_top_prob
        else:
            top_idx = global_top_idx
            confidence = global_top_prob

        top_raw_class = classes[top_idx]

        if confidence < 0.28 or global_max_logit < 0.6 or global_top_prob < 0.20:
            return None, 0.0, False

        info = get_disease_info(top_raw_class, lang=lang)
        return info, confidence, True

    return None, 0.0, False


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
        return "Low", "Normal weather conditions."

    high_humidity_days = sum(1 for h in humidity if h is not None and h >= 85)
    wet_days = sum(1 for p in precip if p is not None and p > 1.0)
    avg_tmin = sum(t for t in tmin if t is not None) / max(1, len(tmin))

    if 10 <= avg_tmin <= 24 and high_humidity_days >= 3 and wet_days >= 3:
        return "High", f"{high_humidity_days} humid days and {wet_days} wet days forecast with nighttime temps ~{avg_tmin:.0f}°C (ideal for fungal blight spread)."
    elif high_humidity_days >= 2 or wet_days >= 2:
        return "Medium", f"{high_humidity_days} humid days forecast in the coming week. Preventive monitoring recommended."
    return "Low", "Favorable dry conditions with minimal likelihood of fungal disease transmission."


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

# Sidebar minimal settings (Clean language picker)
lang = st.sidebar.selectbox("🌐 Interface Language / भाषा", ["en", "hi"], format_func=lambda x: "English (EN)" if x == "en" else "हिन्दी (HI)")
T = TEXT[lang]

# 1. Glass Floating Mobile App Header Bar
st.markdown(
    f"""<div class="km-glass-app-bar">
  <div class="km-brand-wrap">
    <div class="km-glass-logo">🌿</div>
    <div>
      <div class="km-brand-name">{T['app_name']}</div>
      <div class="km-brand-sub">{T['app_tagline']}</div>
    </div>
  </div>
  <div class="km-glass-status">
    <div class="km-status-beacon"></div>
    <span>{T['system_ready']}</span>
  </div>
</div>""",
    unsafe_allow_html=True
)

# 2. Unified Top-Level Glass Navigation Tabs
app_tabs = st.tabs([
    "🌱 AI Doctor",
    "🗺️ Outbreak Map",
    "📊 Surveillance",
    "✅ KVK Network",
    "🧪 Safety & PHI"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: AI CROP DOCTOR & DIAGNOSIS
# ─────────────────────────────────────────────────────────────────────────────
with app_tabs[0]:
    # Frosted Glass Hero Card
    st.markdown(
        f"""<div class="km-glass-hero">
  <div class="km-hero-badge">⚡ {T['hero_badge']}</div>
  <div class="km-hero-title">{T['hero_title']}</div>
  <div class="km-hero-sub">{T['hero_sub']}</div>
  <div class="km-pipeline">
    <div class="km-pipe-node">
      <div class="km-pipe-icon">📷</div>
      <div class="km-pipe-title">{T['how1_title']}</div>
      <div class="km-pipe-sub">{T['how1_desc']}</div>
    </div>
    <div class="km-pipe-node">
      <div class="km-pipe-icon">🤖</div>
      <div class="km-pipe-title">{T['how2_title']}</div>
      <div class="km-pipe-sub">{T['how2_desc']}</div>
    </div>
    <div class="km-pipe-node">
      <div class="km-pipe-icon">🔬</div>
      <div class="km-pipe-title">{T['how3_title']}</div>
      <div class="km-pipe-sub">{T['how3_desc']}</div>
    </div>
    <div class="km-pipe-node">
      <div class="km-pipe-icon">💊</div>
      <div class="km-pipe-title">{T['how4_title']}</div>
      <div class="km-pipe-sub">{T['how4_desc']}</div>
    </div>
  </div>
</div>""",
        unsafe_allow_html=True
    )

    # Leaf Scanner Glass Card with Live Camera & Gallery Upload Tabs
    st.markdown(
        f"""<div class="km-glass-card">
  <div class="km-card-head">
    <div>
      <div class="km-card-title">📷 {T['upload_title']}</div>
      <div class="km-card-sub">{T['upload_sub']}</div>
    </div>
  </div>""",
        unsafe_allow_html=True
    )

    # Sub-tabs inside Scanner: Phone Camera vs Upload
    cam_tab, upload_tab = st.tabs([T["camera_tab"], T["upload_tab"]])
    
    input_file = None
    with cam_tab:
        cam_file = st.camera_input("Snap a live photo of crop leaf", label_visibility="collapsed")
        if cam_file is not None:
            input_file = cam_file

    with upload_tab:
        uploaded_file = st.file_uploader(
            "Upload leaf image from gallery",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )
        if uploaded_file is not None and input_file is None:
            input_file = uploaded_file

    col_loc, col_crp = st.columns(2)
    with col_loc:
        location_input = st.text_input("📍 Location / स्थान", value="Dehradun", placeholder="e.g. Dehradun, Haridwar, Lucknow, Shimla...")
    with col_crp:
        crop_select = st.selectbox(
            "🌾 Crop / फसल",
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

    # Optional Fine-Tune GPS Coordinates for hyper-local precision
    with st.expander("🌐 Fine-Tune GPS Coordinates (Optional / सटीक खेत जीपीएस निर्देशांक)"):
        st.caption("Enter exact farm latitude & longitude for micro-climate disease risk analysis:")
        col_gps_lat, col_gps_lon = st.columns(2)
        with col_gps_lat:
            custom_lat = st.number_input("Latitude (°N)", min_value=-90.0, max_value=90.0, value=0.0, step=0.0001, format="%.5f", help="Leave 0.0 to auto-geocode from city name")
        with col_gps_lon:
            custom_lon = st.number_input("Longitude (°E)", min_value=-180.0, max_value=180.0, value=0.0, step=0.0001, format="%.5f", help="Leave 0.0 to auto-geocode from city name")

    detect_clicked = st.button(f"🔍 {T['detect_btn']}", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Diagnostic Flow
    if input_file is not None:
        image = Image.open(input_file)
        valid_plant, reject_reason = is_valid_crop_leaf(image, lang=lang)

        if not valid_plant:
            st.markdown(
                f"""<div class="km-glass-error">
  <div class="km-error-badge">{T['invalid_photo_badge']}</div>
  <div style="font-weight:800; font-size:1.05rem; color:#FFFFFF; margin-bottom:0.35rem;">{T['invalid_photo_title']}</div>
  <div style="font-size:0.86rem; color:#FDA4AF; line-height:1.5;">
    {T['invalid_photo_msg']} ({reject_reason})<br/>
    {T['invalid_photo_sub']}
  </div>
</div>""",
                unsafe_allow_html=True
            )
            st.image(image, caption="Uploaded Image", use_container_width=True)
        else:
            with st.spinner("AI Vision is analyzing leaf pathology..."):
                diag_info, confidence, is_confident = classify_crop_leaf(image, selected_crop=crop_select, lang=lang)

            if not is_confident or diag_info is None:
                st.markdown(
                    f"""<div class="km-glass-error">
  <div class="km-error-badge">{T['invalid_photo_badge']}</div>
  <div style="font-weight:800; font-size:1.05rem; color:#FFFFFF; margin-bottom:0.35rem;">{T['invalid_photo_title']}</div>
  <div style="font-size:0.86rem; color:#FDA4AF; line-height:1.5;">
    {T['invalid_photo_msg']}<br/>{T['invalid_photo_sub']}
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

                # Diagnostic Report Presentation
                is_healthy_plant = "healthy" in diag_info.get("label", "").lower()
                status_class = "healthy" if is_healthy_plant else "danger"
                status_badge = "✅ Healthy Tissue" if is_healthy_plant else "⚠️ Active Pathology Detected"

                st.markdown(
                    f"""<div class="km-glass-card">
  <div class="km-card-head">
    <div>
      <div class="km-card-title">🔬 {T['results_title']}</div>
      <div class="km-card-sub">AI ResNet-50 Diagnostic Scan</div>
    </div>
    <span style="font-size:0.75rem; font-weight:700; color:{'#34D399' if is_healthy_plant else '#FB7185'}; background:{'rgba(16,185,129,0.14)' if is_healthy_plant else 'rgba(244,63,94,0.14)'}; border:1px solid {'rgba(16,185,129,0.35)' if is_healthy_plant else 'rgba(244,63,94,0.35)'}; padding:0.28rem 0.8rem; border-radius:999px;">
      {status_badge}
    </span>
  </div>""",
                    unsafe_allow_html=True
                )

                st.image(image, caption="Analyzed Leaf Sample", use_container_width=True)
                
                conf_pct = confidence * 100
                st.markdown(
                    f"""<div class="km-diag-grid">
  <div class="km-glass-pill {status_class}">
    <div class="km-diag-header-tag">🏷️ {T['disease_identified']}</div>
    <div class="km-diag-name">{diag_info['label']}</div>
    <div class="km-diag-desc">Pathogen Group: <b>{diag_info['type']}</b></div>
  </div>

  <div class="km-glass-pill">
    <div class="km-diag-header-tag" style="color:#38BDF8;">📊 {T['confidence_level']}</div>
    <div style="display:flex; justify-content:space-between; font-weight:800; font-size:1.05rem; color:#FFFFFF;">
      <span>AI Certainty</span>
      <span style="color:#34D399;">{conf_pct:.1f}%</span>
    </div>
    <div class="km-conf-container">
      <div class="km-conf-bar-bg">
        <div class="km-conf-bar-fill" style="width:{conf_pct:.1f}%;"></div>
      </div>
    </div>
  </div>

  <div class="km-glass-pill">
    <div class="km-diag-header-tag" style="color:#FBBF24;">💡 {T['expert_advice']}</div>
    <div class="km-diag-desc"><b>Treatment:</b> {diag_info['guidance']}</div>
    <div class="km-diag-desc" style="margin-top:0.4rem;"><b>Prevention:</b> {diag_info['prevention']}</div>
  </div>
</div>""",
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

                # Weather & Outbreak Risk Card (with Precise GPS Support)
                geo = None
                weather = None
                if custom_lat != 0.0 and custom_lon != 0.0:
                    try:
                        weather = fetch_weather_forecast(custom_lat, custom_lon)
                        geo = {"lat": custom_lat, "lon": custom_lon, "label": f"Precise GPS ({custom_lat:.4f}°N, {custom_lon:.4f}°E)"}
                    except Exception:
                        pass
                elif location_input:
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
                    risk_color = "#FB7185" if risk == "High" else "#FBBF24" if risk == "Medium" else "#34D399"

                    st.markdown(
                        f"""<div class="km-glass-card">
  <div class="km-card-head">
    <div>
      <div class="km-card-title">🌦️ {T['weather_title']}</div>
      <div class="km-card-sub">{geo['label'] if geo else location_input}</div>
    </div>
    <span style="font-size:0.75rem; font-weight:700; color:{risk_color}; background:rgba(255,255,255,0.05); border:1px solid {risk_color}44; padding:0.28rem 0.8rem; border-radius:999px;">
      Risk: {risk}
    </span>
  </div>

  <div class="km-weather-ribbon">
    <span class="km-w-chip">🌡️ {current.get('temperature_2m', '—')}°C</span>
    <span class="km-w-chip">💧 {current.get('relative_humidity_2m', '—')}% Humidity</span>
    <span class="km-w-chip">🌬️ {current.get('wind_speed_10m', '—')} km/h</span>
  </div>

  <div style="background:rgba(20,32,40,0.55); border:1px solid var(--glass-border); border-radius:14px; padding:0.85rem 1rem; margin-bottom:0.75rem; font-size:0.86rem; line-height:1.48;">
    <b>Outbreak Assessment:</b> <span style="color:{risk_color}; font-weight:700;">{risk}</span><br/>
    <span style="color:var(--km-text-sub);">{risk_why}</span>
  </div>

  <div style="background:rgba(20,32,40,0.55); border:1px solid var(--glass-border); border-radius:14px; padding:0.85rem 1rem; font-size:0.86rem; line-height:1.48;">
    <b>🌾 {T['planting_title']}:</b><br/>
    <span style="color:var(--km-text-sub);">{plant_adv}</span>
  </div>
</div>""",
                        unsafe_allow_html=True
                    )

                    # Voice Prescription Audio Readout
                    audio_text = f"{diag_info['label']}. {diag_info['guidance']}. Outbreak risk is {risk}. {plant_adv}"
                    audio_data = generate_audio(audio_text, lang=lang)
                    if audio_data:
                        st.markdown(f"<div style='font-size:0.88rem; font-weight:700; color:#34D399; margin-bottom:0.35rem;'>{T['listen_btn']}</div>", unsafe_allow_html=True)
                        st.audio(audio_data, format="audio/mp3")

    # Interactive AI Chat Assistant Panel
    st.markdown(
        f"""<div class="km-chat-container">
  <div class="km-card-head" style="margin-bottom:0.85rem;">
    <div>
      <div class="km-card-title">💬 {T['chat_title']}</div>
      <div class="km-card-sub">Ask clinical agricultural questions about plant symptoms & sprays</div>
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

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: GEOSPATIAL OUTBREAK HOTSPOT MAP
# ─────────────────────────────────────────────────────────────────────────────
with app_tabs[1]:
    sih_pillars_addon._inject_styles()
    sih_pillars_addon.render_geospatial_hotspots()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: SURVEILLANCE & OFFICIALS' ANALYTICS DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with app_tabs[2]:
    sih_pillars_addon._inject_styles()
    sih_pillars_addon.render_officials_dashboard()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: EXPERT VALIDATION & KVK / LABORATORY REFERRALS
# ─────────────────────────────────────────────────────────────────────────────
with app_tabs[3]:
    sih_pillars_addon._inject_styles()
    sih_pillars_addon.render_expert_validation_and_referral()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: CHEMICAL SAFETY DOSAGE & PHI RECOVERY TRACKER
# ─────────────────────────────────────────────────────────────────────────────
with app_tabs[4]:
    sih_pillars_addon._inject_styles()
    sih_pillars_addon.render_safety_and_followup()
