# ==============================================================================
# DEPENDENCIES:
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

# --- MODERN DARK GLASSMORPHIC THEME ---
st.markdown(
    """
    <style>
    /* HIDE DEFAULT HEADER & FOOTER */
    header[data-testid="stHeader"], .stAppHeader, #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
    }

    @keyframes fadeInUp3D {
        0% {
            opacity: 0;
            transform: translateY(25px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes radarScan {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* GLOBAL DARK GRADIENT BACKGROUND */
    .stApp, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 50% 10%, #1e1b4b 0%, #0f172a 60%, #020617 100%) !important;
        color: #f8fafc !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1200px !important;
        animation: fadeInUp3D 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* LOGO & BRANDING HEADER */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    
    .logo-icon-3d {
        position: relative;
        width: 44px;
        height: 44px;
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.2);
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
    
    .logo-text {
        font-weight: 800;
        font-size: 1.3rem;
        color: #ffffff;
        letter-spacing: -0.3px;
    }
    
    .logo-subtext {
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .status-badge {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        color: #10b981;
        padding: 0.45rem 1.1rem;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .status-badge::before {
        content: "";
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
    }

    /* HERO SECTION */
    .hero-heading {
        color: #ffffff;
        font-size: 2.8rem;
        font-weight: 900;
        line-height: 1.2;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
        text-align: center;
        letter-spacing: -0.8px;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        max-width: 620px;
        margin: 0 auto 2.5rem auto;
        text-align: center;
        line-height: 1.6;
    }

    /* INPUT CONTAINER & BUTTON CONTROL */
    .stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #ffffff !important;
        border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 14px !important;
        font-size: 1rem !important;
        height: 54px !important;
        padding-left: 1.2rem !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3) !important;
    }

    /* SINGLE BUTTON DESIGN */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4338ca 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 14px !important;
        height: 54px !important;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(79, 70, 229, 0.6) !important;
    }

    /* DOWNLOAD BUTTON */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        height: 44px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }

    /* METRIC & CARDS DISPLAY */
    .metric-card {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.4rem 1rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    .metric-card-title {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 0.4rem;
    }
    .metric-card-value {
        color: #ffffff;
        font-size: 1.7rem;
        font-weight: 900;
    }

    .outer-card-box {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 1.8rem;
        margin-top: 1.6rem;
        margin-bottom: 1.6rem;
    }
    .outer-card-title {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 1.2rem;
    }
    
    .meta-inner-box {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.2rem;
    }
    .meta-inner-title {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
    }
    .meta-inner-val {
        color: #f8fafc;
        font-size: 0.98rem;
        font-weight: 600;
        word-break: break-word;
    }

    .report-card-box {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 1.6rem;
    }

    .stMarkdown h3 {
        color: #818cf8 !important;
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        margin-top: 1.5rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.4rem;
    }
    .stMarkdown p, .stMarkdown li {
        color: #cbd5e1 !important;
        font-size: 0.96rem !important;
        line-height: 1.65 !important;
    }
    .stMarkdown strong {
        color: #38bdf8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session state initialization
if "scanned" not in st.session_state:
    st.session_state.scanned = False
if "audit_data" not in st.session_state:
    st.session_state.audit_data = {}
if "loading" not in st.session_state:
    st.session_state.loading = False


def get_clean_filename(url):
    netloc = urllib.parse.urlparse(url).netloc or url
    clean_domain = re.sub(r"[^a-zA-Z0-9]", "_", netloc).strip("_")
    return f"{clean_domain or 'website'}_audit_report.txt"


def generate_txt_bytes(data):
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

    full_report = f"""====================================================================
SITEPULSE ENTERPRISE - TECHNICAL SEO & DIAGNOSTIC REPORT
====================================================================
Target URL          : {data.get('url')}
Pages Scanned       : {data.get('total_pages_scanned', 1)}
Calculated Score    : {data.get('health_score')}/100
HTTP Response Status: {data.get('status')}
Server Latency      : {data.get('rt')} seconds
Payload Size        : {data.get('size_kb')} KB

--------------------------------------------------------------------
1. SCRAPED TECHNICAL METRICS
--------------------------------------------------------------------
- Page Title: {data.get('title')}
- Meta Description: {data.get('meta')}
- H1 Headings Count: {data.get('h1')}
- Image Count: {data.get('tot_img')}
- Missing Image Alt Attributes: {data.get('no_alt')}

--------------------------------------------------------------------
2. DETECTED FLAWS & ISSUES
--------------------------------------------------------------------
{flaws_text}

--------------------------------------------------------------------
3. ACTIONABLE RECOMMENDATIONS
--------------------------------------------------------------------
{recs_text}

--------------------------------------------------------------------
4. CRITICAL MISSING ELEMENTS
--------------------------------------------------------------------
{missing_text}

--------------------------------------------------------------------
5. COMPLETE AI DIAGNOSTIC REPORT
--------------------------------------------------------------------
{data.get('report', '')}
====================================================================
"""
    return full_report.encode("utf-8")


def scan_individual_url(page_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
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
    flaws, recommendations, missing_critical = [], [], []

    if raw_html:
        soup = BeautifulSoup(raw_html, "html.parser")

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

        h1_tags = soup.find_all("h1")
        h1_count = len(h1_tags)
        if h1_count == 0:
            flaws.append("No primary `<h1>` heading tag found on the page.")
        elif h1_count > 1:
            flaws.append(
                f"Multiple ({h1_count}) `<h1>` tags detected (best practice is 1 per page)."
            )

        imgs = soup.find_all("img")
        tot_img = len(imgs)
        no_alt = sum(
            1 for img in imgs if not img.get("alt") or not img.get("alt").strip()
        )
        if no_alt > 0:
            flaws.append(
                f"{no_alt} out of {tot_img} images lack descriptive `alt` text."
            )

    else:
        title = "Title Tag Missing"
        meta_desc = "Meta Description Tag Missing"
        h1_count, tot_img, no_alt = 0, 0, 0
        flaws.append("Failed to establish HTTP connection.")

    if latency > 1.5:
        flaws.append(f"High server response latency detected ({latency}s).")

    if not page_url.startswith("https://"):
        flaws.append("Target URL is served over insecure HTTP instead of HTTPS.")

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
        "headers_str": "\n".join([f"{k}: {v}" for k, v in response_headers.items()]),
    }


def extract_sitemap_urls(base_url, max_urls=5):
    parsed = urllib.parse.urlparse(base_url)
    urls = [base_url]
    try:
        res = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=4, verify=False)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            full_link = urllib.parse.urljoin(base_url, a["href"])
            link_parsed = urllib.parse.urlparse(full_link)
            if link_parsed.netloc == parsed.netloc and full_link not in urls:
                urls.append(full_link)
            if len(urls) >= max_urls:
                break
    except Exception:
        pass
    return urls


def perform_website_audit(target_url):
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    urls_to_scan = extract_sitemap_urls(target_url, max_urls=5)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        scanned_pages = list(executor.map(scan_individual_url, urls_to_scan))

    main_page = scanned_pages[0]

    all_flaws, all_recs, all_missing = [], [], []

    for page in scanned_pages:
        for f in page["flaws"]:
            if f not in all_flaws:
                all_flaws.append(f)
        for r in page["recommendations"]:
            if r not in all_recs:
                all_recs.append(r)
        for m in page["missing_critical"]:
            if m not in all_missing:
                all_missing.append(m)

    health_score = max(20, min(100, 100 - (len(all_flaws) * 10)))

    return {
        "url": target_url,
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
Perform a technical audit for: {data['url']}
- Latency: {data['rt']}s | Status: {data['status']} | Size: {data['size_kb']} KB
- Calculated Health Score: {data['health_score']}/100
- Title: "{data['title']}"
- Meta Description: "{data['meta']}"
- H1 Tags: {data['h1']} | Images: {data['tot_img']} (Missing Alt: {data['no_alt']})

FLAWS:
{chr(10).join(['- ' + f for f in data['flaws']])}

Provide formatted Markdown:
### Executive Summary
**Calculated Score: {data['health_score']}/100**

### 1. Detected Technical Flaws
### 2. Domain Quality Breakdown
### 3. Key Recommendations
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
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                json={
                    "model": "deepseek/deepseek-r1:free",
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=15,
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    return f"""### Executive Summary
**Calculated Score: {data['health_score']}/100**

Live runtime scan completed for **{data['url']}** with response time of **{data['rt']}s** and **{len(data['flaws'])} issues detected**.

### 1. Detected Technical Flaws
{chr(10).join(['- ' + f for f in data['flaws']]) if data['flaws'] else '- No major critical flaws found.'}

### 2. Domain Quality Breakdown
- **Server Speed:** {data['rt']} seconds
- **DOM Structure:** {data['h1']} H1 tag(s) found
- **Images:** {data['tot_img']} total ({data['no_alt']} missing alt text)

### 3. Key Recommendations
- Add missing image alt tags.
- Ensure proper title & meta description optimization.
"""


# --- HEADER ---
h_col1, h_col2 = st.columns([2.5, 1.5])
with h_col1:
    st.markdown(
        """
        <div class="logo-container">
            <div class="logo-icon-3d">
                <div class="radar-sweep"></div>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="z-index: 2;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="2" x2="12" y2="6"></line>
                    <line x1="12" y1="18" x2="12" y2="22"></line>
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
        st.download_button(
            label="Download Audit Report",
            data=st.session_state.audit_data["txt_data"],
            file_name=get_clean_filename(
                st.session_state.audit_data.get("url", "website")
            ),
            mime="text/plain",
            use_container_width=True,
        )
    else:
        st.markdown(
            '<div style="display: flex; justify-content: flex-end;"><div class="status-badge">System Ready</div></div>',
            unsafe_allow_html=True,
        )

st.markdown('<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True)


# --- PAGE 1: AUDIT INPUT SCREEN ---
if not st.session_state.scanned:
    st.markdown(
        """
        <div style="text-align: center;">
            <div class="hero-heading">Enterprise Website Auditor</div>
            <div class="hero-subtitle">Instantly analyze webpage health, SEO flaws, and technical response metrics</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_left, c_input, c_btn, c_right = st.columns([1, 4, 2, 1])

    with c_input:
        url_input = st.text_input(
            "", placeholder="https://example.com", label_visibility="collapsed"
        )

    with c_btn:
        button_label = (
            "⚡ Analyzing..." if st.session_state.loading else "Run Website Audit"
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
        audit_res = perform_website_audit(target)
        audit_res["report"] = generate_ai_report(audit_res)
        audit_res["txt_data"] = generate_txt_bytes(audit_res)

        st.session_state.audit_data = audit_res
        st.session_state.scanned = True
        st.session_state.loading = False
        st.rerun()


# --- PAGE 2: AUDIT RESULTS SCREEN ---
else:
    d = st.session_state.audit_data

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            f"""
            <div style="margin-bottom: 1.5rem;">
                <h2 style="color: #ffffff; font-size: 2rem; font-weight: 800; margin: 0;">Audit Results: {d['url']}</h2>
                <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 4px;">Scanned {d['total_pages_scanned']} core URL(s) in parallel</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        if st.button("Audit Another Site", use_container_width=True):
            st.session_state.scanned = False
            st.rerun()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-card-title">HTTP Status</div><div class="metric-card-value">{d["status"]}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-card-title">Latency</div><div class="metric-card-value">{d["rt"]}s</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-card-title">H1 Headings</div><div class="metric-card-value">{d["h1"]}</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f'<div class="metric-card"><div class="metric-card-title">Missing Alt Tags</div><div class="metric-card-value">{d["no_alt"]} / {d["tot_img"]}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="outer-card-box">
            <div class="outer-card-title">Scraped Metadata Overview</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="meta-inner-box">
                    <div class="meta-inner-title">Page Title</div>
                    <div class="meta-inner-val">{d["title"]}</div>
                </div>
                <div class="meta-inner-box">
                    <div class="meta-inner-title">Meta Description</div>
                    <div class="meta-inner-val">{d["meta"]}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="report-card-box">', unsafe_allow_html=True)
    st.markdown(
        '<div style="color: #ffffff; font-size: 1.25rem; font-weight: 800; margin-bottom: 1rem;">Technical Inspection & AI Analysis</div>',
        unsafe_allow_html=True,
    )
    st.markdown(d["report"])
    st.markdown("</div>", unsafe_allow_html=True)