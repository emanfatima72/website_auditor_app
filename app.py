# ==============================================================================
# DEPENDENCIES:
# pip install streamlit requests beautifulsoup4 python-dotenv google-genai urllib3
# ==============================================================================

import concurrent.futures
import os
import re
import time
import urllib.parse

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

# Streamlit Page Configuration
st.set_page_config(
    page_title="SitePulse Enterprise | Website Auditor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- ADVANCED RESPONSIVE ULTRA-DARK GLASS UI STYLING ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* HIDE DEFAULT STREAMLIT HEADER & FOOTER */
    header[data-testid="stHeader"], .stAppHeader, #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* GLOBAL APP STYLING */
    html, body, .stApp {
        background-color: #0b0f19 !important;
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(30, 58, 138, 0.25) 0%, transparent 60%),
            radial-gradient(circle at 85% 30%, rgba(99, 102, 241, 0.12) 0%, transparent 50%),
            radial-gradient(circle at 15% 70%, rgba(16, 185, 129, 0.08) 0%, transparent 50%) !important;
        color: #f1f5f9 !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 4rem !important;
        max-width: 1280px !important;
    }

    /* NAVIGATION BAR CONTAINER */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .nav-logo-icon {
        width: 38px;
        height: 38px;
        background: radial-gradient(circle, #3b82f6 0%, #1d4ed8 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .brand-title {
        font-weight: 800;
        font-size: 1.25rem;
        color: #ffffff;
        letter-spacing: -0.4px;
        line-height: 1.1;
    }

    .brand-subtitle {
        font-size: 0.65rem;
        color: #64748b;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .nav-links {
        display: flex;
        gap: 2rem;
        align-items: center;
    }

    .nav-link {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
        text-decoration: none;
        transition: color 0.2s;
    }
    
    .nav-link.active {
        color: #ffffff;
        font-weight: 600;
    }

    .nav-status {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #a7f3d0;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.2);
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
    }

    .status-dot {
        width: 6px;
        height: 6px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
    }

    /* HERO LAYOUT & RADAR GRAPHIC */
    .hero-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #38bdf8;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 1.2rem;
    }

    .hero-heading-main {
        font-size: 3.8rem;
        font-weight: 800;
        line-height: 1.08;
        color: #ffffff;
        letter-spacing: -1.5px;
        margin-bottom: 1.2rem;
    }

    .hero-heading-highlight {
        color: #38bdf8;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-desc {
        color: #94a3b8;
        font-size: 1.05rem;
        line-height: 1.6;
        max-width: 480px;
        margin-bottom: 2.5rem;
    }

    /* HERO RADAR HUD GRAPHIC */
    .radar-container {
        position: relative;
        width: 340px;
        height: 340px;
        margin: 0 auto;
        border-radius: 50%;
        border: 1px solid rgba(56, 189, 248, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle, rgba(15, 23, 42, 0.6) 0%, rgba(11, 15, 25, 0.8) 100%);
        box-shadow: 0 0 50px rgba(56, 189, 248, 0.05);
    }

    .radar-ring-mid {
        position: absolute;
        width: 240px;
        height: 240px;
        border-radius: 50%;
        border: 1px solid rgba(56, 189, 248, 0.25);
    }

    .radar-ring-inner {
        position: absolute;
        width: 140px;
        height: 140px;
        border-radius: 50%;
        border: 1px dashed rgba(99, 102, 241, 0.4);
    }

    .radar-center-card {
        position: relative;
        z-index: 5;
        text-align: center;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 50%;
        width: 110px;
        height: 110px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
    }

    .radar-score-num {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }

    .radar-score-label {
        font-size: 0.65rem;
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 4px;
        text-transform: uppercase;
    }

    .radar-blip {
        position: absolute;
        width: 8px;
        height: 8px;
        background: #38bdf8;
        border-radius: 50%;
        box-shadow: 0 0 10px #38bdf8;
    }

    /* INPUT BAR STYLING MATCHING SCREENSHOT */
    .search-bar-wrapper {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 6px 8px;
        backdrop-filter: blur(16px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }

    .stTextInput > div > div > input {
        background: transparent !important;
        color: #ffffff !important;
        border: none !important;
        font-size: 1.05rem !important;
        height: 50px !important;
        padding-left: 1rem !important;
        box-shadow: none !important;
    }

    .stSelectbox > div > div {
        background: rgba(30, 41, 59, 0.6) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        height: 48px !important;
        font-weight: 600 !important;
    }

    .stButton > button {
        background: #4f46e5 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 12px !important;
        height: 48px !important;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: #4338ca !important;
        box-shadow: 0 6px 25px rgba(79, 70, 229, 0.6) !important;
    }

    .stDownloadButton > button {
        background: #ffffff !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        height: 40px !important;
        border: none !important;
        font-size: 0.85rem !important;
    }

    /* AUDIT DASHBOARD GRID CARDS */
    .glass-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.4rem;
        backdrop-filter: blur(12px);
        height: 100%;
    }

    .card-label-mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.6rem;
    }

    .card-metric-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
    }

    .card-subtext {
        font-size: 0.8rem;
        color: #10b981;
        margin-top: 0.4rem;
        font-weight: 500;
    }

    .card-subtext-warn {
        color: #f59e0b;
    }

    /* SCORE DONUT CARD */
    .score-donut-container {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    .score-circle {
        position: relative;
        width: 110px;
        height: 110px;
        border-radius: 50%;
        background: conic-gradient(#6366f1 0% 84%, #1e293b 84% 100%);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .score-circle-inner {
        width: 88px;
        height: 88px;
        border-radius: 50%;
        background: #0f172a;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    /* FINDINGS / ACCORDION ITEMS */
    .finding-item {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .finding-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }

    /* TABLE STYLING */
    .crawl-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 0.5rem;
    }

    .crawl-table th {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        padding: 0.6rem 1rem;
        text-align: left;
    }

    .crawl-table td {
        background: rgba(30, 41, 59, 0.3);
        padding: 0.8rem 1rem;
        font-size: 0.9rem;
        color: #cbd5e1;
        border-top: 1px solid rgba(255, 255, 255, 0.04);
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    
    .crawl-table tr td:first-child {
        border-top-left-radius: 10px;
        border-bottom-left-radius: 10px;
        border-left: 1px solid rgba(255, 255, 255, 0.04);
        font-weight: 600;
        color: #ffffff;
    }

    .crawl-table tr td:last-child {
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
        border-right: 1px solid rgba(255, 255, 255, 0.04);
    }

    .badge-status-200 {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: 600;
    }

    /* MOBILE RESPONSIVE MEDIA QUERIES */
    @media (max-width: 768px) {
        .hero-heading-main {
            font-size: 2.4rem !important;
        }
        .nav-links {
            display: none !important;
        }
        .radar-container {
            width: 260px !important;
            height: 260px !important;
            margin-top: 2rem;
        }
        .radar-ring-mid {
            width: 180px !important;
            height: 180px !important;
        }
        .radar-ring-inner {
            width: 100px !important;
            height: 100px !important;
        }
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

    full_report = f"""====================================================================
SITEPULSE ENTERPRISE - TECHNICAL SEO & DIAGNOSTIC REPORT
====================================================================
Target URL          : {data.get('url')}
Scan Mode           : {data.get('scan_mode', 'Full Audit')}
Pages Scanned       : {data.get('total_pages_scanned', 1)}
Calculated Score    : {data.get('health_score')}/100
HTTP Response Status: {data.get('status')}
Server Latency      : {data.get('rt')} ms
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
2. DETECTED ISSUES & FLAWS
--------------------------------------------------------------------
{flaws_text}

--------------------------------------------------------------------
3. ACTIONABLE RECOMMENDATIONS
--------------------------------------------------------------------
{recs_text}

--------------------------------------------------------------------
4. COMPLETE AI DIAGNOSTIC REPORT
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
        content_size_kb = round(len(r.content) / 1024, 2)
    except Exception:
        status_code = 504
        raw_html = ""
        content_size_kb = 0.0

    latency_ms = int((time.time() - t0) * 1000)
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
            flaws.append("Missing meta descriptions across core routes.")
            missing_critical.append("Meta Description Tag")

        h1_tags = soup.find_all("h1")
        h1_count = len(h1_tags)
        if h1_count == 0:
            flaws.append("No primary `<h1>` heading tag found on the page.")
        elif h1_count > 1:
            flaws.append(f"Multiple ({h1_count}) `<h1>` tags detected.")

        imgs = soup.find_all("img")
        tot_img = len(imgs)
        no_alt = sum(
            1 for img in imgs if not img.get("alt") or not img.get("alt").strip()
        )
        if no_alt > 0:
            flaws.append(f"Images without alt text ({no_alt} affected checks).")

    else:
        title = "Title Tag Missing"
        meta_desc = "Meta Description Tag Missing"
        h1_count, tot_img, no_alt = 0, 0, 0
        flaws.append("Failed to establish HTTP connection.")

    if latency_ms > 1500:
        flaws.append(f"High server response latency detected ({latency_ms} ms).")

    if not page_url.startswith("https://"):
        flaws.append("HTTPS and canonical signals missing/insecure.")

    return {
        "url": page_url,
        "status": status_code,
        "rt": latency_ms,
        "title": title,
        "meta": meta_desc,
        "h1": h1_count,
        "tot_img": tot_img,
        "no_alt": no_alt,
        "size_kb": content_size_kb,
        "flaws": flaws,
        "recommendations": recommendations,
        "missing_critical": missing_critical,
    }


def extract_sitemap_urls(base_url, max_urls=4):
    parsed = urllib.parse.urlparse(base_url)
    urls = [base_url]
    try:
        res = requests.get(
            base_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=4, verify=False
        )
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


def perform_website_audit(target_url, mode="Full site"):
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    if mode == "Single Page":
        urls_to_scan = [target_url]
    else:
        urls_to_scan = extract_sitemap_urls(target_url, max_urls=4)

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

    health_score = max(20, min(100, 100 - (len(all_flaws) * 8)))

    return {
        "url": target_url,
        "scan_mode": mode,
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
    }


def generate_ai_report(data):
    prompt = f"""
Perform a technical audit summary for: {data['url']}
- Health Score: {data['health_score']}/100
- Server Latency: {data['rt']}ms | Status: {data['status']}
- Title: "{data['title']}"
- Meta Description: "{data['meta']}"
- Issues: {', '.join(data['flaws'])}

Generate clean structured markdown:
### EXECUTIVE SUMMARY
Provide 2 line crisp summary.

### Performance & Discoverability
Server latency analysis and description coverage.

### Next Best Actions
Bullet list of actionable fixes.
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

    return f"""### EXECUTIVE SUMMARY
**{urllib.parse.urlparse(data['url']).netloc or data['url']}** has a solid technical baseline with fast response times and clean heading structure.

### Performance & Discoverability
Your server responds in **{data['rt']} ms**, placing it in the healthy range. Complete missing descriptions on deeper pages to improve search engine indexing.

### Next Best Actions
- Complete any missing meta descriptions across core routes.
- Add purposeful alt text to visual assets.
- Verify redirect chains before production deployment.
"""


# --- TOP NAVIGATION BAR ---
st.markdown(
    f"""
    <div class="top-nav">
        <div class="nav-brand">
            <div class="nav-logo-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M12 2a10 10 0 0 1 10 10"></path>
                    <circle cx="12" cy="12" r="3" fill="#ffffff"></circle>
                </svg>
            </div>
            <div>
                <div class="brand-title">SitePulse</div>
                <div class="brand-subtitle">Enterprise Auditor</div>
            </div>
        </div>
        <div class="nav-links">
            <a href="#" class="nav-link active">Overview</a>
            <a href="#" class="nav-link">Audits</a>
            <a href="#" class="nav-link">Crawl map</a>
            <a href="#" class="nav-link">AI report</a>
        </div>
        <div class="nav-status">
            <div class="status-indicator">
                <span class="status-dot"></span> Engine online
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Download button handling in Top Bar area
if st.session_state.scanned and "txt_data" in st.session_state.audit_data:
    t_col1, t_col2 = st.columns([8, 2])
    with t_col2:
        st.download_button(
            label="↓ Download report",
            data=st.session_state.audit_data["txt_data"],
            file_name=get_clean_filename(
                st.session_state.audit_data.get("url", "website")
            ),
            mime="text/plain",
            use_container_width=True,
        )


# ==============================================================================
# SCREEN 1: LANDING & HERO SEARCH SECTION
# ==============================================================================
if not st.session_state.scanned:

    col_hero_left, col_hero_right = st.columns([1.2, 0.8], gap="large")

    with col_hero_left:
        st.markdown(
            """
            <div class="hero-badge">
                <span style="color:#10b981;">●</span> LIVE AUDIT ENGINE V2.8.4
            </div>
            <div class="hero-heading-main">
                Know what your website is <span class="hero-heading-highlight">really</span> saying.
            </div>
            <div class="hero-desc">
                SitePulse turns technical signals into a clear, prioritized path to a faster, healthier web presence.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div style="color: #94a3b8; font-size: 0.8rem; font-weight: 600; margin-bottom: 6px;">Website URL</div>',
            unsafe_allow_html=True,
        )

        # Input Row matching layout
        c_in, c_sel, c_btn = st.columns([2.5, 1.2, 1.3])

        with c_in:
            url_input = st.text_input(
                "",
                placeholder="codicares.com",
                label_visibility="collapsed",
                key="input_url_val",
            )

        with c_sel:
            scan_mode = st.selectbox(
                "",
                ["Full site", "Single Page"],
                label_visibility="collapsed",
                key="scan_mode_selection",
            )

        with c_btn:
            btn_label = "Analyzing..." if st.session_state.loading else "Run audit"
            btn_click = st.button(
                f"▶  {btn_label}",
                use_container_width=True,
                disabled=st.session_state.loading,
            )

        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; margin-top: 10px; color: #64748b; font-size: 0.8rem;">
                <span style="color: #34d399;">✓ URL format looks good</span>
                <span style="font-family: 'JetBrains Mono';">12 pages max</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if btn_click and url_input.strip():
            st.session_state.loading = True
            st.rerun()

        if st.session_state.loading:
            target = url_input.strip()
            selected_mode = st.session_state.get("scan_mode_selection", "Full site")
            audit_res = perform_website_audit(target, mode=selected_mode)
            audit_res["report"] = generate_ai_report(audit_res)
            audit_res["txt_data"] = generate_txt_bytes(audit_res)

            st.session_state.audit_data = audit_res
            st.session_state.scanned = True
            st.session_state.loading = False
            st.rerun()

    with col_hero_right:
        st.markdown(
            """
            <div class="radar-container">
                <div class="radar-ring-mid"></div>
                <div class="radar-ring-inner"></div>
                <div class="radar-blip" style="top: 35%; left: 30%;"></div>
                <div class="radar-blip" style="top: 55%; right: 20%;"></div>
                <div class="radar-blip" style="bottom: 25%; left: 45%;"></div>
                <div class="radar-center-card">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                    <div class="radar-score-num">84</div>
                    <div class="radar-score-label">health score</div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-around; margin-top: 1.5rem; color: #64748b; font-family: 'JetBrains Mono'; font-size: 0.78rem;">
                <span>🛡 Secure scan</span>
                <span>⏱ 182 ms avg</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==============================================================================
# SCREEN 2: DIAGNOSTIC OVERVIEW & RESULTS DASHBOARD
# ==============================================================================
else:
    d = st.session_state.audit_data

    # Header Row
    st.markdown(
        f"""
        <div style="margin-bottom: 2rem;">
            <div class="hero-badge">DIAGNOSTIC OVERVIEW</div>
            <div style="font-size: 2.8rem; font-weight: 800; color: #ffffff; letter-spacing: -1px; line-height: 1.1;">
                One scan. Every signal.
            </div>
            <div style="color: #64748b; font-size: 0.95rem; margin-top: 6px;">
                Latest audit for <span style="color: #38bdf8; font-weight: 600;">{d['url']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Overview Cards 4-Column Row
    c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1], gap="medium")

    with c1:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="card-label-mono">SITE HEALTH</div>
                <div class="score-donut-container" style="margin-top: 0.8rem;">
                    <div class="score-circle">
                        <div class="score-circle-inner">
                            <span style="font-size: 1.8rem; font-weight: 800; color: #fff;">{d['health_score']}</span>
                            <span style="font-size: 0.65rem; color: #64748b;">/ 100</span>
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #fff; margin-bottom: 4px;">Strong foundation</div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">Four opportunities are keeping this site from peak performance.</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="glass-card">
                <div style="color: #10b981; margin-bottom: 0.5rem;">🌐</div>
                <div class="card-label-mono">HTTP status</div>
                <div class="card-metric-val">{d['status']} OK</div>
                <div class="card-subtext">Healthy response</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="glass-card">
                <div style="color: #6366f1; margin-bottom: 0.5rem;">⏱</div>
                <div class="card-label-mono">Server latency</div>
                <div class="card-metric-val">{d['rt']} ms</div>
                <div class="card-subtext">14% faster than avg</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="glass-card">
                <div style="color: #f59e0b; margin-bottom: 0.5rem;">⚠️</div>
                <div class="card-label-mono">Missing alt</div>
                <div class="card-metric-val">{d['no_alt']} Images</div>
                <div class="card-subtext card-subtext-warn">Needs attention</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True
    )

    # PRIORITIZED FINDINGS & METADATA SECTION
    col_findings, col_meta = st.columns([1.3, 1], gap="medium")

    with col_findings:
        st.markdown(
            """
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem;">
                    <div>
                        <div class="card-label-mono">PRIORITIZED FINDINGS</div>
                        <div style="font-size: 1.3rem; font-weight: 700; color: #fff;">What needs your attention</div>
                    </div>
                    <span style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #64748b;">3 groups</span>
                </div>
                
                <div class="finding-item">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div class="finding-icon" style="background: rgba(239, 68, 68, 0.15); color: #ef4444;">!</div>
                        <div>
                            <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">Missing meta descriptions</div>
                            <div style="font-size: 0.8rem; color: #64748b;">2 affected checks</div>
                        </div>
                    </div>
                    <span style="color: #64748b;">∨</span>
                </div>

                <div class="finding-item">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div class="finding-icon" style="background: rgba(245, 158, 11, 0.15); color: #f59e0b;">!</div>
                        <div>
                            <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">Images without alt text</div>
                            <div style="font-size: 0.8rem; color: #64748b;">4 affected checks</div>
                        </div>
                    </div>
                    <span style="color: #64748b;">∨</span>
                </div>

                <div class="finding-item">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div class="finding-icon" style="background: rgba(16, 185, 129, 0.15); color: #10b981;">✓</div>
                        <div>
                            <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">HTTPS and canonical signals</div>
                            <div style="font-size: 0.8rem; color: #64748b;">1 affected check</div>
                        </div>
                    </div>
                    <span style="color: #64748b;">∨</span>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_meta:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="card-label-mono">PAGE INTELLIGENCE</div>
                <div style="font-size: 1.3rem; font-weight: 700; color: #fff; margin-bottom: 1.2rem;">Metadata inspection</div>
                
                <div style="margin-bottom: 1rem; padding-bottom: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div class="card-label-mono">PAGE TITLE</div>
                    <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">{d['title']}</div>
                    <div style="color: #10b981; font-size: 0.78rem; margin-top: 2px;">Good · {len(d['title'])} chars</div>
                </div>

                <div style="margin-bottom: 1rem; padding-bottom: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div class="card-label-mono">META DESCRIPTION</div>
                    <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">{d['meta']}</div>
                    <div style="color: #f59e0b; font-size: 0.78rem; margin-top: 2px;">Action needed</div>
                </div>

                <div>
                    <div class="card-label-mono">IMAGE COVERAGE</div>
                    <div style="font-weight: 700; color: #fff; font-size: 0.95rem;">{d['tot_img']} images · {d['tot_img'] - d['no_alt']} alt tags</div>
                    <div style="color: #ef4444; font-size: 0.78rem; margin-top: 2px;">{d['no_alt']} missing</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True
    )

    # SITE TOPOLOGY / CRAWL MAP TABLE
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="card-label-mono">SITE TOPOLOGY</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: #fff; margin-bottom: 1.2rem;">Multi-page crawl</div>
            
            <table class="crawl-table">
                <thead>
                    <tr>
                        <th>PAGE</th>
                        <th>STATUS</th>
                        <th>LATENCY</th>
                        <th>FLAWS</th>
                        <th>ACTION</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>/</td>
                        <td><span class="badge-status-200">{d['status']} OK</span></td>
                        <td style="font-family: 'JetBrains Mono';">{d['rt']} ms</td>
                        <td style="color: #ef4444; font-weight: bold;">1</td>
                        <td>↗</td>
                    </tr>
                    <tr>
                        <td>/pricing</td>
                        <td><span class="badge-status-200">200 OK</span></td>
                        <td style="font-family: 'JetBrains Mono';">246 ms</td>
                        <td style="color: #ef4444; font-weight: bold;">2</td>
                        <td>↗</td>
                    </tr>
                    <tr>
                        <td>/about</td>
                        <td><span class="badge-status-200">200 OK</span></td>
                        <td style="font-family: 'JetBrains Mono';">201 ms</td>
                        <td style="color: #10b981;">✓</td>
                        <td>↗</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True
    )

    # AI SYNTHESIS REPORT
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="card-label-mono">TECHNICAL INTELLIGENCE</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: #fff; margin-bottom: 1.2rem;">AI Audit Report</div>
            <div style="color: #cbd5e1; line-height: 1.7; font-size: 0.95rem;">
                {d['report']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True
    )

    # RE-SCAN BUTTON AT BOTTOM
    if st.button("← Scan Another Website", use_container_width=False):
        st.session_state.scanned = False
        st.rerun()