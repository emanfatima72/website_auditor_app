# ==============================================================================
# REQUIRED LIBRARIES INSTALLATION INSTRUCTIONS:
# Run the following command in your terminal/command prompt to install dependencies:
# pip install streamlit requests beautifulsoup4 python-dotenv google-genai urllib3
# ==============================================================================

import concurrent.futures
import os
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET

import requests
import streamlit as st
import urllib3
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Streamlit Page Config
st.set_page_config(
    page_title="SitePulse Enterprise | Website Auditor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- ADVANCED 3D GLASSMORPHIC ENTERPRISE THEME ---
st.markdown(
    """
    <style>
    /* HIDE STREAMLIT DEFAULT HEADER BAR & FOOTER */
    header[data-testid="stHeader"], .stAppHeader, #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* 3D KEYFRAME ANIMATIONS */
    @keyframes fadeInUp3D {
        0% {
            opacity: 0;
            transform: translateY(30px) scale(0.97) rotateX(4deg);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1) rotateX(0deg);
        }
    }

    @keyframes pulseGlow3D {
        0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4), 0 8px 20px rgba(0,0,0,0.06); }
        70% { box-shadow: 0 0 0 14px rgba(99, 102, 241, 0), 0 12px 25px rgba(0,0,0,0.12); }
        100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0), 0 8px 20px rgba(0,0,0,0.06); }
    }

    @keyframes radarScan {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    @keyframes radarPulse {
        0% { transform: scale(0.8); opacity: 0.8; }
        50% { transform: scale(1.15); opacity: 0.4; }
        100% { transform: scale(0.8); opacity: 0.8; }
    }

    /* Global Soft Lavender 3D Gradient Background Force */
    .stApp, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 20%, #f5f3ff 0%, #eef2ff 60%, #e0e7ff 100%) !important;
        color: #1e1b4b !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        perspective: 1000px;
    }
    
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1280px !important;
        animation: fadeInUp3D 0.7s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    /* Top Header Navbar with 3D Depth & Radar Animation */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 14px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .logo-container:hover {
        transform: translateY(-2px) scale(1.02);
    }
    
    .logo-icon-3d {
        position: relative;
        width: 46px;
        height: 46px;
        background: linear-gradient(135deg, #6366f1 0%, #312e81 100%);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.3);
        overflow: hidden;
    }

    .radar-sweep {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: conic-gradient(from 0deg, transparent 0%, transparent 75%, rgba(255, 255, 255, 0.6) 100%);
        animation: radarScan 2.5s linear infinite;
    }

    .radar-pulse-ring {
        position: absolute;
        width: 24px;
        height: 24px;
        border: 1.5px solid rgba(255, 255, 255, 0.7);
        border-radius: 50%;
        animation: radarPulse 2s ease-in-out infinite;
    }
    
    .logo-text {
        font-weight: 800;
        font-size: 1.28rem;
        color: #1e1b4b;
        letter-spacing: -0.3px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .logo-subtext {
        color: #64748b;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .status-badge {
        border: 1px solid rgba(255, 255, 255, 0.8);
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(8px);
        color: #059669;
        padding: 0.48rem 1.1rem;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.9);
        transition: all 0.3s ease;
    }
    .status-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.15);
    }
    
    .status-badge::before {
        content: "";
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        animation: pulseGlow3D 2s infinite;
    }

    /* DOWNLOAD BUTTON 3D STYLING */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        height: 44px !important;
        padding: 0 1.4rem !important;
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
        box-shadow: 0 12px 28px rgba(79, 70, 229, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
        color: #ffffff !important;
        transform: translateY(-3px) scale(1.02);
    }
    
    /* Audit New Target Button */
    .audit-new-btn > button {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1.5px solid #c7d2fe !important;
        color: #4338ca !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        border-radius: 12px !important;
        height: 44px !important;
        padding: 0 1.2rem !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1), inset 0 1px 0 #ffffff !important;
        transition: all 0.3s ease !important;
    }
    .audit-new-btn > button:hover {
        background: #ffffff !important;
        border-color: #818cf8 !important;
        color: #312e81 !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(99, 102, 241, 0.18) !important;
    }

    /* Hero Section 3D */
    .hero-container {
        animation: fadeInUp3D 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .badge-capsule {
        display: inline-block;
        padding: 0.45rem 1.2rem;
        border: 1px solid rgba(199, 210, 254, 0.8);
        border-radius: 20px;
        background: rgba(224, 231, 255, 0.7);
        backdrop-filter: blur(10px);
        color: #4338ca;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.9px;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.8);
        transition: all 0.3s ease;
    }
    .badge-capsule:hover {
        transform: scale(1.05) translateY(-2px);
        border-color: #818cf8;
    }
    
    .hero-heading {
        color: #1e1b4b;
        font-size: 2.9rem;
        font-weight: 900;
        line-height: 1.2;
        margin-top: 1rem;
        margin-bottom: 0.8rem;
        text-align: center;
        letter-spacing: -0.8px;
        text-shadow: 0 4px 12px rgba(30, 27, 75, 0.08);
    }
    
    .hero-subtitle {
        color: #475569;
        font-size: 1.08rem;
        max-width: 630px;
        margin: 0 auto 2.2rem auto;
        text-align: center;
        line-height: 1.6;
        font-weight: 500;
    }

    /* INPUT & STYLISH MATCHING PURPLE SELECTBOX CONTROLS */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
    }
    
    .stTextInput, .stSelectbox {
        width: 100% !important;
        margin-bottom: 0px !important;
    }

    /* 3D Text Input Field */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1e1b4b !important;
        border: 1.5px solid #c7d2fe !important;
        border-radius: 14px !important;
        font-size: 0.98rem !important;
        height: 52px !important;
        padding-left: 1.1rem !important;
        box-shadow: 0 6px 16px rgba(99, 102, 241, 0.08), inset 0 2px 4px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #94a3b8 !important;
        opacity: 1 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.22), 0 8px 24px rgba(99, 102, 241, 0.15) !important;
        transform: translateY(-2px);
    }

    /* MATCHED SELECTBOX BUTTON STYLING (PURPLE GRADIENT WITH CLEAR TEXT) */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 14px !important;
        height: 52px !important;
        box-shadow: 0 8px 22px rgba(79, 70, 229, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .stSelectbox > div > div:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
        box-shadow: 0 12px 28px rgba(79, 70, 229, 0.45) !important;
        transform: translateY(-2px);
    }
    
    /* Force clear white text & arrow inside the Selectbox header */
    .stSelectbox div[data-baseweb="select"] span {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 0.94rem !important;
    }
    .stSelectbox div[data-baseweb="select"] svg {
        fill: #ffffff !important;
    }
    
    /* Popover dropdown styling for visible text items */
    div[data-baseweb="popover"] {
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.15) !important;
    }
    div[data-baseweb="popover"] ul {
        background-color: #ffffff !important;
        padding: 6px !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="popover"] li {
        color: #1e1b4b !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: #e0e7ff !important;
        color: #4338ca !important;
    }

    /* 3D Dynamic Glowing Button */
    .stButton {
        width: 100% !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 0.98rem !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 14px !important;
        height: 52px !important;
        box-shadow: 0 8px 22px rgba(79, 70, 229, 0.38), inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 0px !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
        box-shadow: 0 14px 30px rgba(79, 70, 229, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
        transform: translateY(-3px) scale(1.02);
    }
    .stButton > button:active {
        transform: translateY(-1px) scale(0.99);
    }

    /* Metric Cards with Dynamic 3D Depth */
    .metric-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border: 1.5px solid rgba(224, 231, 255, 0.8);
        border-radius: 16px;
        padding: 1.4rem 1rem;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.01), inset 0 1px 0 #ffffff;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: fadeInUp3D 0.6s ease;
    }
    .metric-card:hover {
        transform: translateY(-6px) translateZ(10px);
        border-color: #a5b4fc;
        box-shadow: 0 18px 35px -5px rgba(99, 102, 241, 0.2), inset 0 1px 0 #ffffff;
    }
    .metric-card-title {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 0.4rem;
    }
    .metric-card-value {
        color: #1e1b4b;
        font-size: 1.7rem;
        font-weight: 900;
        text-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }

    /* Outer Card Glassmorphic Box */
    .outer-card-box {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(16px);
        border: 1.5px solid rgba(224, 231, 255, 0.8);
        border-radius: 18px;
        padding: 1.8rem;
        margin-top: 1.6rem;
        margin-bottom: 1.6rem;
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.08), inset 0 1px 0 #ffffff;
        animation: fadeInUp3D 0.7s ease;
    }
    .outer-card-title {
        color: #1e1b4b;
        font-size: 1.2rem;
        font-weight: 900;
        margin-bottom: 1.2rem;
    }
    .meta-inner-box {
        background: rgba(248, 250, 252, 0.8);
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.3rem;
        height: 100%;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.02);
        transition: all 0.3s ease;
    }
    .meta-inner-box:hover {
        border-color: #c7d2fe;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(99, 102, 241, 0.08);
    }
    .meta-inner-title {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 800;
        margin-bottom: 0.6rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .meta-inner-val {
        color: #0f172a;
        font-size: 1rem;
        font-weight: 700;
        word-break: break-word;
        line-height: 1.5;
    }
    .meta-badge-missing {
        background: #fef2f2;
        color: #ef4444;
        border: 1px solid #fee2e2;
        font-size: 0.72rem;
        font-weight: 800;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
    }
    .meta-badge-ok {
        background: #f0fdf4;
        color: #16a34a;
        border: 1px solid #dcfce7;
        font-size: 0.72rem;
        font-weight: 800;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
    }

    /* 3D Technical Report Container */
    .report-card-box {
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(16px);
        border: 1.5px solid rgba(224, 231, 255, 0.8);
        border-radius: 20px;
        padding: 2.2rem;
        margin-top: 1.6rem;
        box-shadow: 0 14px 35px rgba(99, 102, 241, 0.09), inset 0 1px 0 #ffffff;
        animation: fadeInUp3D 0.8s ease;
    }

    .stMarkdown h3 {
        color: #312e81 !important;
        font-size: 1.25rem !important;
        font-weight: 900 !important;
        margin-top: 1.6rem !important;
        margin-bottom: 0.8rem !important;
        border-bottom: 1.5px solid #e0e7ff;
        padding-bottom: 0.4rem;
    }
    .stMarkdown p, .stMarkdown li {
        color: #334155 !important;
        font-size: 0.96rem !important;
        line-height: 1.65 !important;
    }
    .stMarkdown strong {
        color: #4f46e5 !important;
        font-weight: 800 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state setup
if "scanned" not in st.session_state:
    st.session_state.scanned = False
if "audit_data" not in st.session_state:
    st.session_state.audit_data = {}
if "loading" not in st.session_state:
    st.session_state.loading = False


def get_clean_filename(url):
    """Generates a clean Notepad (.txt) filename derived from the target website URL."""
    netloc = urllib.parse.urlparse(url).netloc or url
    clean_domain = re.sub(r"[^a-zA-Z0-9]", "_", netloc).strip("_")
    if not clean_domain:
        clean_domain = "website"
    return f"{clean_domain}_audit_report.txt"


def generate_txt_bytes(data):
    """Generates a comprehensive full-screen report content for Notepad download."""
    flaws_text = (
        "\n".join([f"  - {f}" for f in data.get("flaws", [])])
        if data.get("flaws")
        else "  - No major critical flaws detected."
    )
    recs_text = (
        "\n".join([f"  - {r}" for r in data.get("recommendations", [])])
        if data.get("recommendations")
        else "  - Maintain current technical standards."
    )
    missing_text = (
        "\n".join([f"  - {m}" for m in data.get("missing_critical", [])])
        if data.get("missing_critical")
        else "  - None detected."
    )

    pages_breakdown = ""
    if data.get("scanned_pages"):
        pages_breakdown = (
            "\n----------------------------------------------------\n"
            "SCANNED SUB-PAGES CRAWL LOG\n"
            "----------------------------------------------------\n"
        )
        for idx, p in enumerate(data.get("scanned_pages", []), 1):
            pages_breakdown += f"[{idx}] {p['url']} | Status: {p['status']} | Latency: {p['rt']}s | Flaws: {len(p['flaws'])}\n"

    full_report = f"""====================================================================
SITEPULSE ENTERPRISE - TECHNICAL SEO & DIAGNOSTIC REPORT
====================================================================
Target URL          : {data.get('url')}
Scan Scope          : {data.get('scan_mode', 'Single Page')}
Pages Scanned       : {data.get('total_pages_scanned', 1)}
Calculated Score    : {data.get('health_score')}/100
HTTP Response Status: {data.get('status')}
Server Latency      : {data.get('rt')} seconds
Payload Size        : {data.get('size_kb')} KB

--------------------------------------------------------------------
1. SCRAPED TECHNICAL METRICS (MAIN PAGE)
--------------------------------------------------------------------
- Page Title: {data.get('title')}
- Meta Description: {data.get('meta')}
- H1 Headings Count: {data.get('h1')}
- Image Count: {data.get('tot_img')}
- Missing Image Alt Attributes: {data.get('no_alt')}
{pages_breakdown}
--------------------------------------------------------------------
2. DETECTED FLAWS & ISSUES
--------------------------------------------------------------------
{flaws_text}

--------------------------------------------------------------------
3. ACTIONABLE RECOMMENDATIONS
--------------------------------------------------------------------
{recs_text}

--------------------------------------------------------------------
4. CRITICAL MISSING ELEMENTS & SECURITY DEFICIENCIES
--------------------------------------------------------------------
{missing_text}

--------------------------------------------------------------------
5. COMPLETE AI DIAGNOSTIC REPORT BREAKDOWN
--------------------------------------------------------------------
{data.get('report', '')}

--------------------------------------------------------------------
6. RESPONSE HEADERS
--------------------------------------------------------------------
{data.get('headers_str', 'N/A')}

====================================================================
End of SitePulse Enterprise Diagnostic Report
====================================================================
"""
    return full_report.encode("utf-8")


def scan_individual_url(page_url):
    """Scans an individual URL and extracts DOM elements and flaws."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    t0 = time.time()
    try:
        r = requests.get(
            page_url, headers=headers, timeout=10, verify=False, allow_redirects=True
        )
        status_code = r.status_code
        raw_html = r.text
        response_headers = r.headers
        content_size_kb = round(len(r.content) / 1024, 2)
    except Exception:
        status_code = 504
        raw_html = ""
        response_headers = {}
        content_size_kb = 0.0

    latency = round(time.time() - t0, 2)
    flaws = []
    recommendations = []
    missing_critical = []

    if raw_html:
        soup = BeautifulSoup(raw_html, "html.parser")

        # Title
        title_tag = soup.title
        title = (
            title_tag.string.strip()
            if title_tag and title_tag.string
            else "Title Tag Missing"
        )
        if title == "Title Tag Missing":
            flaws.append("Page Title `<title>` tag is completely missing.")
            missing_critical.append("Document Title `<title>` tag")
            recommendations.append(
                "Add a concise `<title>` tag (50-60 characters) relevant to target keywords."
            )
        elif len(title) < 20 or len(title) > 70:
            flaws.append(
                f"Page Title length ({len(title)} chars) is non-optimal (recommended: 50-60 chars)."
            )

        # Meta Description
        meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find(
            "meta", attrs={"property": "og:description"}
        )
        meta_desc = (
            meta_tag.get("content", "").strip()
            if meta_tag and meta_tag.get("content")
            else "Meta Description Tag Missing"
        )
        if meta_desc == "Meta Description Tag Missing":
            flaws.append("Meta description tag is absent or empty.")
            missing_critical.append("Meta Description Tag")
            recommendations.append(
                "Add a compelling meta description tag (140-160 characters) to improve Search CTR."
            )

        # H1 Tag Count
        h1_tags = soup.find_all("h1")
        h1_count = len(h1_tags)
        if h1_count == 0:
            flaws.append("No primary `<h1>` heading tag found on the page.")
            missing_critical.append("Main `<h1>` Heading Tag")
            recommendations.append(
                "Include exactly one primary `<h1>` tag containing the main page topic."
            )
        elif h1_count > 1:
            flaws.append(
                f"Multiple ({h1_count}) `<h1>` tags detected (best practice is 1 per page)."
            )
            recommendations.append(
                "Consolidate headings so there is only one top-level `<h1>` per page."
            )

        # Images & Alt
        imgs = soup.find_all("img")
        tot_img = len(imgs)
        no_alt = sum(
            1 for img in imgs if not img.get("alt") or not img.get("alt").strip()
        )
        if no_alt > 0:
            flaws.append(
                f"{no_alt} out of {tot_img} image elements lack accessibility descriptive `alt` text."
            )
            recommendations.append(
                f"Add descriptive `alt` attributes to all {no_alt} missing image elements."
            )

        # Viewport Tag
        viewport = soup.find("meta", attrs={"name": "viewport"})
        if not viewport:
            flaws.append("Mobile viewport meta tag `<meta name=\"viewport\">` is missing.")
            missing_critical.append("Mobile Viewport Configuration Tag")
            recommendations.append(
                'Add `<meta name="viewport" content="width=device-width, initial-scale=1">` for mobile responsiveness.'
            )

        # Open Graph
        og_title = soup.find("meta", attrs={"property": "og:title"})
        if not og_title:
            flaws.append("Open Graph `og:title` social media tag is not configured.")

        # Canonical URL
        canonical = soup.find("link", attrs={"rel": "canonical"})
        if not canonical:
            flaws.append("Canonical URL link `<link rel=\"canonical\">` is missing.")
            recommendations.append(
                "Add a canonical tag to prevent duplicate content indexing issues."
            )

        body_text = soup.get_text(separator=" ", strip=True)[:2500]

    else:
        title = "Title Tag Missing"
        meta_desc = "Meta Description Tag Missing"
        h1_count = 0
        tot_img = 0
        no_alt = 0
        body_text = ""
        flaws.append("Failed to establish a valid HTTP connection or received empty payload.")

    if latency > 1.5:
        flaws.append(f"High server response latency detected ({latency}s).")
        recommendations.append(
            "Optimize server-side execution, leverage CDN caching, or optimize web host response time."
        )

    if not page_url.startswith("https://"):
        flaws.append("Target URL is served over insecure HTTP instead of encrypted HTTPS.")
        missing_critical.append("HTTPS / SSL Encryption")
        recommendations.append(
            "Enforce SSL/TLS encryption and redirect all HTTP traffic to HTTPS."
        )

    sec_headers = [
        "Strict-Transport-Security",
        "X-Frame-Options",
        "Content-Security-Policy",
    ]
    missing_sec_headers = [
        sh
        for sh in sec_headers
        if sh not in response_headers and sh.lower() not in response_headers
    ]
    if missing_sec_headers:
        flaws.append(f"Missing security headers: {', '.join(missing_sec_headers)}.")
        recommendations.append(
            f"Configure server response headers: {', '.join(missing_sec_headers)}."
        )

    return {
        "url": page_url,
        "status": status_code,
        "rt": latency,
        "title": title,
        "meta": meta_desc,
        "h1": h1_count,
        "tot_img": tot_img,
        "no_alt": no_alt,
        "size_kb": content_size_kb,
        "flaws": flaws,
        "recommendations": recommendations,
        "missing_critical": missing_critical,
        "body_text": body_text,
        "headers_str": "\n".join([f"{k}: {v}" for k, v in response_headers.items()]),
    }


def extract_sitemap_urls(base_url, max_urls=8):
    """Parses XML sitemaps or falls back to internal homepage link extraction."""
    parsed = urllib.parse.urlparse(base_url)
    domain_base = f"{parsed.scheme}://{parsed.netloc}"
    sitemap_url = f"{domain_base}/sitemap.xml"

    urls = []
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(sitemap_url, headers=headers, timeout=4, verify=False)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            for elem in root.iter():
                if elem.tag.endswith("loc") and elem.text:
                    if not elem.text.endswith(".xml") and elem.text not in urls:
                        urls.append(elem.text)
                    if len(urls) >= max_urls:
                        break
    except Exception:
        pass

    if not urls:
        try:
            res = requests.get(base_url, headers=headers, timeout=4, verify=False)
            soup = BeautifulSoup(res.text, "html.parser")
            urls.append(base_url)
            for a in soup.find_all("a", href=True):
                full_link = urllib.parse.urljoin(base_url, a["href"])
                link_parsed = urllib.parse.urlparse(full_link)
                if (
                    link_parsed.netloc == parsed.netloc
                    and full_link not in urls
                    and not full_link.endswith(
                        (".jpg", ".png", ".pdf", ".zip", "#")
                    )
                ):
                    urls.append(full_link)
                if len(urls) >= max_urls:
                    break
        except Exception:
            urls = [base_url]

    return urls if urls else [base_url]


def perform_website_audit(target_url, scan_mode="Single Page"):
    """Main Orchestration Function (Multi-Threaded Parallel Execution)"""
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    if scan_mode == "Single Page":
        urls_to_scan = [target_url]
    else:
        urls_to_scan = extract_sitemap_urls(target_url, max_urls=8)

    # Multi-threading for fast multi-page scanning
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        scanned_pages = list(executor.map(scan_individual_url, urls_to_scan))

    main_page = scanned_pages[0]

    all_flaws = []
    all_recs = []
    all_missing = []

    for page in scanned_pages:
        for f in page["flaws"]:
            formatted_f = f"[{page['url']}] {f}" if scan_mode != "Single Page" else f
            if formatted_f not in all_flaws:
                all_flaws.append(formatted_f)
        for r in page["recommendations"]:
            if r not in all_recs:
                all_recs.append(r)
        for m in page["missing_critical"]:
            if m not in all_missing:
                all_missing.append(m)

    deductions = len(all_flaws) * 8 if scan_mode != "Single Page" else len(all_flaws) * 12
    health_score = max(20, min(100, 100 - deductions))

    return {
        "url": target_url,
        "scan_mode": scan_mode,
        "total_pages_scanned": len(scanned_pages),
        "scanned_pages": scanned_pages,
        "status": main_page["status"],
        "rt": main_page["rt"],
        "title": main_page["title"],
        "meta": main_page["meta"],
        "h1": main_page["h1"],
        "tot_img": main_page["tot_img"],
        "no_alt": main_page["no_alt"],
        "size_kb": main_page["size_kb"],
        "health_score": health_score,
        "flaws": all_flaws,
        "recommendations": all_recs,
        "missing_critical": all_missing,
        "headers_str": main_page["headers_str"],
    }


def generate_ai_report(data):
    prompt = f"""
You are an expert Enterprise Web Auditor. Perform a deep technical audit for: {data['url']}

=== DOMAIN METRICS ===
- Scan Scope: {data['scan_mode']} ({data['total_pages_scanned']} Pages Scanned)
- HTTP Response Status: {data['status']}
- Server Latency: {data['rt']} seconds
- Page Size: {data['size_kb']} KB
- Calculated Health Score: {data['health_score']}/100
- Page Title: "{data['title']}"
- Meta Description: "{data['meta']}"
- H1 Tags Found: {data['h1']}
- Images: {data['tot_img']} (Missing Alt: {data['no_alt']})

=== DETECTED FLAWS ===
{chr(10).join(['- ' + f for f in data['flaws']])}

=== RECOMMENDATIONS ===
{chr(10).join(['- ' + r for r in data['recommendations']])}

Format the response strictly with Markdown:
### Executive Summary
**Overall Calculated Health Score: {data['health_score']}/100**

Live runtime scan performed for **{data['url']}** (Mode: {data['scan_mode']}). The analysis indicates a server response latency of **{data['rt']}s** with **{len(data['flaws'])} primary structural/technical issue(s)** detected during real-time DOM parsing.

### 1. Real-Time Flaws & Identified Issues
(List all detected flaws with bullets)

### 2. Domain & Page Quality Analysis
- **Server Latency:** Recorded response time of **{data['rt']}s** via direct HTTP request.
- **Semantic Structure:** Headings parsed with **{data['h1']} H1 tags** found in the body container.
- **Media Assets:** Scanned **{data['tot_img']} image elements**, where **{data['no_alt']}** lack descriptive ALT text tags.
- **Metadata Indexing:** Title recorded as *"{data['title']}"*.

### 3. Actionable Recommendations
(List top 3-5 recommendations)

### 4. Critical Missing Elements & Security Deficiencies
(List critical missing items)
"""

    if GEMINI_API_KEY:
        try:
            from google import genai

            client = genai.Client(api_key=GEMINI_API_KEY)
            res = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            if res and res.text:
                return res.text
        except Exception:
            pass

    if OPENROUTER_API_KEY:
        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek/deepseek-r1:free",
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=18,
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    flaws_formatted = (
        "\n".join([f"- {f}" for f in data["flaws"]])
        if data["flaws"]
        else "- No major critical flaws detected during DOM sweep."
    )
    recs_formatted = (
        "\n".join([f"- {r}" for r in data["recommendations"]])
        if data["recommendations"]
        else "- Maintain current technical standards and monitor performance."
    )
    missing_formatted = (
        "\n".join([f"- {m}" for m in data["missing_critical"]])
        if data["missing_critical"]
        else "- No high-severity missing structural tags detected."
    )

    return f"""### Executive Summary
**Overall Calculated Health Score: {data['health_score']}/100**

Live runtime scan performed for **{data['url']}**. The analysis indicates a server response latency of **{data['rt']}s** with **{len(data['flaws'])} primary structural/technical issue(s)** detected during real-time DOM parsing.

### 1. Real-Time Flaws & Identified Issues
{flaws_formatted}

### 2. Domain & Page Quality Analysis
- **Server Latency:** Recorded response time of **{data['rt']}s** via direct HTTP request.
- **Payload & Size:** Page download payload recorded at **{data['size_kb']} KB**.
- **Semantic Structure:** Headings parsed with **{data['h1']} H1 tag(s)** found in the body container.
- **Media Assets:** Scanned **{data['tot_img']} image element(s)**, where **{data['no_alt']}** lack descriptive `alt` tags.
- **Metadata Indexing:** Title tag recorded as *"{data['title']}"*.

### 3. Actionable Recommendations
{recs_formatted}

### 4. Critical Missing Elements & Security Deficiencies
{missing_formatted}
"""


# --- UNIFIED HEADER NAVBAR WITH ANIMATED WEB AUDIT RADAR ICON ---
h_col1, h_col2 = st.columns([2.2, 1.8])

with h_col1:
    st.markdown(
        """
        <div class="logo-container" style="padding-top: 4px;">
            <div class="logo-icon-3d">
                <div class="radar-pulse-ring"></div>
                <div class="radar-sweep"></div>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="z-index: 2;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="2" x2="12" y2="6"></line>
                    <line x1="12" y1="18" x2="12" y2="22"></line>
                    <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
                    <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
                    <circle cx="12" cy="12" r="3" fill="#ffffff"></circle>
                </svg>
            </div>
            <span class="logo-text">SitePulse Enterprise</span>
            <span class="logo-subtext">| Website Auditor</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with h_col2:
    if st.session_state.scanned and "txt_data" in st.session_state.audit_data:
        btn_c, badge_c = st.columns([1.4, 1])
        with btn_c:
            dynamic_filename = get_clean_filename(
                st.session_state.audit_data.get("url", "website")
            )
            st.download_button(
                label="Download Report",
                data=st.session_state.audit_data["txt_data"],
                file_name=dynamic_filename,
                mime="text/plain",
                use_container_width=True,
            )
        with badge_c:
            st.markdown(
                '<div class="status-badge" style="float: right;">System Operational</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div style="display: flex; justify-content: flex-end;"><div class="status-badge">System Operational</div></div>',
            unsafe_allow_html=True,
        )

st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)


# --- PAGE 1: AUDIT INPUT SCREEN ---
if not st.session_state.scanned:
    st.markdown(
        """
        <div class="hero-container" style="text-align: center; margin-top: 2rem;">
            <div class="badge-capsule">ENTERPRISE DIAGNOSTICS PLATFORM</div>
            <div class="hero-heading">
                Enterprise Website Audit &<br>Diagnostics
            </div>
            <div class="hero-subtitle">
                Deep-tier structural inspection, technical flaw detection, and live AI quality analysis
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_input, col_mode, col_btn, col_right = st.columns(
        [0.4, 3.4, 1.8, 1.4, 0.4]
    )

    with col_input:
        url_input = st.text_input(
            "", placeholder="https://example.com", label_visibility="collapsed"
        )

    with col_mode:
        scan_mode_choice = st.selectbox(
            "",
            ["Single Page", "Full Site (Fast Multi-Page)"],
            label_visibility="collapsed",
        )

    with col_btn:
        button_label = (
            "⚡ Analyzing..." if st.session_state.loading else "Run Analysis"
        )
        btn_click = st.button(
            button_label,
            use_container_width=True,
            disabled=st.session_state.loading,
        )

    if btn_click and url_input.strip():
        st.session_state.loading = True
        st.rerun()

    if st.session_state.loading:
        target = url_input.strip()
        if not target.startswith(("http://", "https://")):
            target = "https://" + target

        audit_res = perform_website_audit(target, scan_mode=scan_mode_choice)
        report_md = generate_ai_report(audit_res)
        audit_res["report"] = report_md

        txt_bytes = generate_txt_bytes(audit_res)
        audit_res["txt_data"] = txt_bytes

        st.session_state.audit_data = audit_res
        st.session_state.scanned = True
        st.session_state.loading = False
        st.rerun()


# --- PAGE 2: AUDIT RESULTS SCREEN ---
else:
    d = st.session_state.audit_data

    # Audit Title Bar
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            f"""
            <div style="margin-bottom: 1.5rem; animation: fadeInUp3D 0.5s ease;">
                <h1 style="color: #1e1b4b; font-size: 2.1rem; font-weight: 900; margin: 0; letter-spacing: -0.5px;">Audit Results for {d['url']}</h1>
                <p style="color: #64748b; font-size: 0.95rem; margin-top: 4px; font-weight: 600;">Scope: {d['scan_mode']} ({d['total_pages_scanned']} Pages Scanned) | Comprehensive live structural & AI analysis</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown('<div class="audit-new-btn">', unsafe_allow_html=True)
        if st.button("Audit New Target", use_container_width=True):
            st.session_state.scanned = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 4 Diagnostic Metric Cards with 3D Float
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-card-title">HTTP Status Code</div><div class="metric-card-value">{d["status"]}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-card-title">Server Latency</div><div class="metric-card-value">{d["rt"]}s</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-card-title">H1 Tags Count</div><div class="metric-card-value">{d["h1"]} Detected</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-card-title">Missing Alt Attributes</div><div class="metric-card-value">{d["no_alt"]} / {d["tot_img"]}</div></div>',
            unsafe_allow_html=True,
        )

    # Scraped Metadata Overview 3D Card Box
    meta_badge_html = (
        '<span class="meta-badge-missing">Missing Tag</span>'
        if d["meta"] == "Meta Description Tag Missing"
        else '<span class="meta-badge-ok">Valid</span>'
    )
    meta_color = (
        "#ef4444" if d["meta"] == "Meta Description Tag Missing" else "#0f172a"
    )

    st.markdown(
        f"""
        <div class="outer-card-box">
            <div class="outer-card-title">Scraped Metadata Overview</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="meta-inner-box">
                    <div class="meta-inner-title"><span>Page Title</span></div>
                    <div class="meta-inner-val">{d["title"]}</div>
                </div>
                <div class="meta-inner-box">
                    <div class="meta-inner-title">
                        <span>Meta Description</span>
                        {meta_badge_html}
                    </div>
                    <div class="meta-inner-val" style="color: {meta_color};">{d["meta"]}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Multi-Page Crawl Results Table (if Full Site mode was selected)
    if d.get("total_pages_scanned", 1) > 1:
        st.markdown(
            '<div style="color: #1e1b4b; font-size: 1.2rem; font-weight: 800; margin-bottom: 0.8rem;">🌐 Scanned Sub-Pages Overview</div>',
            unsafe_allow_html=True,
        )
        page_summary = []
        for p in d.get("scanned_pages", []):
            page_summary.append(
                {
                    "Scanned Page URL": p["url"],
                    "Status": p["status"],
                    "Latency (s)": p["rt"],
                    "Title Tag": p["title"],
                    "Flaws Count": len(p["flaws"]),
                }
            )
        st.dataframe(page_summary, use_container_width=True)

    # 3D Technical Diagnostic & Inspection Report Box
    st.markdown('<div class="report-card-box">', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #1e1b4b; font-size: 1.28rem; font-weight: 900; margin-bottom: 1rem;">Technical Diagnostic & Inspection Report</div>',
        unsafe_allow_html=True,
    )
    st.markdown(d["report"])
    st.markdown("</div>", unsafe_allow_html=True)