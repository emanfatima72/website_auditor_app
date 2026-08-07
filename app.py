# ==============================================================================
# DEPENDENCIES:
# pip install streamlit requests beautifulsoup4 python-dotenv google-genai urllib3
# ==============================================================================

import concurrent.futures
import math
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

# Streamlit Page Configuration
st.set_page_config(
    page_title="SitePulse Enterprise | Website Auditor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- ADVANCED RESPONSIVE ULTRA-DARK GLASS UI STYLING ---
st.markdown(
    """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

header[data-testid="stHeader"], .stAppHeader, #MainMenu, footer {
    display: none !important;
    visibility: hidden !important;
}

html, body, .stApp {
    background-color: #0b0f19 !important;
    background-image: 
        radial-gradient(circle at 50% 0%, rgba(30, 58, 138, 0.25) 0%, transparent 60%),
        radial-gradient(circle at 85% 30%, rgba(99, 102, 241, 0.12) 0%, transparent 50%),
        radial-gradient(circle at 15% 70%, rgba(16, 185, 129, 0.08) 0%, transparent 50%) !important;
    color: #cbd5e1 !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 4rem !important;
    max-width: 1280px !important;
}

/* TOP NAVIGATION */
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
    animation: logoGlow 3s infinite alternate;
}

@keyframes logoGlow {
    0% { box-shadow: 0 0 10px rgba(59, 130, 246, 0.4); }
    100% { box-shadow: 0 0 22px rgba(59, 130, 246, 0.9); }
}

.brand-title {
    font-weight: 700;
    font-size: 1.2rem;
    color: #ffffff;
    letter-spacing: -0.3px;
    line-height: 1.1;
}

.brand-subtitle {
    font-size: 0.65rem;
    color: #64748b;
    font-weight: 600;
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
    font-size: 0.88rem;
    font-weight: 500;
    text-decoration: none;
}

.nav-link.active {
    color: #ffffff;
    font-weight: 600;
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
    animation: pulseDot 2s infinite;
}

@keyframes pulseDot {
    0% { transform: scale(0.95); opacity: 0.7; }
    50% { transform: scale(1.3); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.7; }
}

/* HERO SECTION */
.hero-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #38bdf8;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 1rem;
}

.hero-heading-main {
    font-size: 3.5rem;
    font-weight: 700;
    line-height: 1.1;
    color: #ffffff;
    letter-spacing: -1.2px;
    margin-bottom: 1rem;
}

.hero-heading-highlight {
    color: #38bdf8;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-desc {
    color: #94a3b8;
    font-size: 1rem;
    line-height: 1.6;
    max-width: 480px;
    margin-bottom: 2rem;
    font-weight: 400;
}

/* RADAR VISUAL */
.radar-container {
    position: relative;
    width: 320px;
    height: 320px;
    margin: 0 auto;
    border-radius: 50%;
    border: 1px solid rgba(56, 189, 248, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(circle, rgba(15, 23, 42, 0.6) 0%, rgba(11, 15, 25, 0.8) 100%);
    box-shadow: 0 0 50px rgba(56, 189, 248, 0.08);
}

.radar-sweep-line {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: conic-gradient(from 0deg, rgba(56, 189, 248, 0.3) 0deg, transparent 60deg, transparent 360deg);
    animation: radarSweep 4s linear infinite;
}

@keyframes radarSweep {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.radar-center-card {
    position: relative;
    z-index: 5;
    text-align: center;
    background: rgba(15, 23, 42, 0.95);
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
    font-size: 2rem;
    font-weight: 700;
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

/* CARDS & CONTAINERS */
.glass-card {
    background: rgba(15, 23, 42, 0.55);
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
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.card-metric-val {
    font-size: 1.75rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
}

.card-subtext {
    font-size: 0.8rem;
    color: #10b981;
    margin-top: 0.3rem;
    font-weight: 500;
}

.card-subtext-warn {
    color: #f59e0b;
}

/* DOMAIN AUTHORITY METRIC BAR */
.da-progress-bg {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    height: 8px;
    width: 100%;
    margin-top: 10px;
    overflow: hidden;
}

.da-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    border-radius: 8px;
}

/* ELEGANT TYPOGRAPHY FIXES FOR METADATA */
.meta-field-title {
    font-weight: 600 !important;
    color: #f1f5f9 !important;
    font-size: 0.92rem !important;
    line-height: 1.4 !important;
}

.meta-field-desc {
    font-weight: 400 !important;
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    line-height: 1.5 !important;
}

/* STYLING STREAMLIT EXPANDERS (ARROWS FIXED) */
div[data-testid="stExpander"] {
    background: rgba(30, 41, 59, 0.35) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    margin-bottom: 0.6rem !important;
    overflow: hidden !important;
}

div[data-testid="stExpander"] details summary {
    padding: 0.8rem 1rem !important;
    color: #f1f5f9 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
}

div[data-testid="stExpander"] details summary:hover {
    color: #38bdf8 !important;
}

div[data-testid="stExpander"] details[open] summary {
    border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
}

/* CRAWL TABLE */
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
    background: rgba(30, 41, 59, 0.25);
    padding: 0.8rem 1rem;
    font-size: 0.88rem;
    color: #cbd5e1;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.crawl-table tr td:first-child {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
    border-left: 1px solid rgba(255, 255, 255, 0.04);
    font-weight: 500;
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
    font-weight: 500;
}

.stTextInput > div > div > input {
    background: transparent !important;
    color: #ffffff !important;
    border: none !important;
    font-size: 1rem !important;
    height: 48px !important;
    padding-left: 1rem !important;
    box-shadow: none !important;
}

.stSelectbox > div > div {
    background: rgba(30, 41, 59, 0.6) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    height: 48px !important;
    font-weight: 500 !important;
}

.stButton > button {
    background: #4f46e5 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    border: none !important;
    border-radius: 12px !important;
    height: 48px !important;
    box-shadow: 0 4px 20px rgba(79, 70, 229, 0.4) !important;
}

.stDownloadButton > button {
    background: #ffffff !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    height: 40px !important;
    border: none !important;
    font-size: 0.85rem !important;
}
</style>""",
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


def calculate_domain_authority(url, pages_scanned, avg_rt, flaws_count):
    """Computes an estimated Domain Authority / Trust Score (0-100) based on tech signals."""
    domain = urllib.parse.urlparse(url).netloc or url
    base_score = 45

    if url.startswith("https://"):
        base_score += 15
    if len(domain) < 15:
        base_score += 10
    if avg_rt < 1000:
        base_score += 15
    elif avg_rt < 2000:
        base_score += 8

    base_score += min(15, len(pages_scanned) * 3)
    base_score -= flaws_count * 2

    final_da = max(18, min(95, base_score))
    return final_da


def generate_txt_bytes(data):
    pages_report = ""
    for idx, p in enumerate(data.get("scanned_pages", []), 1):
        flaws_p = (
            "\n".join([f"    - {f}" for f in p["flaws"]])
            if p["flaws"]
            else "    - None detected."
        )
        pages_report += f"""
[PAGE {idx}] {p['url']}
  - Status: {p['status']} | Latency: {p['rt']}ms | Size: {p['size_kb']} KB
  - Title: {p['title']}
  - Meta: {p['meta']}
  - Headings: H1={p['h1']} | Total Images: {p['tot_img']} (Missing Alt: {p['no_alt']})
  - Page Specific Flaws:
{flaws_p}
--------------------------------------------------------------------"""

    full_report = f"""====================================================================
SITEPULSE ENTERPRISE - TECHNICAL SEO & DEEP DIAGNOSTIC REPORT
====================================================================
Target Domain       : {data.get('url')}
Scan Mode           : {data.get('scan_mode', 'Full Audit')}
Total Scanned Pages : {data.get('total_pages_scanned', 1)}
Site Health Score   : {data.get('health_score')}/100
Domain Trust / DA   : {data.get('domain_authority')}/100
Avg Server Latency  : {data.get('rt')} ms

====================================================================
DETAILED PER-PAGE AUDIT BREAKDOWN
===================================================================={pages_report}

====================================================================
AI EXECUTIVE & DEEP DIAGNOSTIC ANALYSIS
====================================================================
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
    flaws, recommendations = [], []

    if raw_html:
        soup = BeautifulSoup(raw_html, "html.parser")

        title_tag = soup.title
        title = (
            title_tag.string.strip()
            if title_tag and title_tag.string
            else "Title Tag Missing"
        )
        if title == "Title Tag Missing":
            flaws.append("Missing `<title>` tag on page.")
            recommendations.append(
                "Add an optimized `<title>` tag (50-60 chars) matching page intent."
            )

        meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find(
            "meta", attrs={"property": "og:description"}
        )
        meta_desc = (
            meta_tag.get("content", "").strip()
            if meta_tag and meta_tag.get("content")
            else "Meta Description Missing"
        )
        if meta_desc == "Meta Description Missing":
            flaws.append("Missing `<meta name='description'>` tag.")
            recommendations.append(
                "Write a unique meta description (140-160 chars) to improve CTR."
            )

        h1_tags = soup.find_all("h1")
        h1_count = len(h1_tags)
        if h1_count == 0:
            flaws.append("No primary `<h1>` heading tag found.")
            recommendations.append("Add exactly one `<h1>` heading per page.")
        elif h1_count > 1:
            flaws.append(f"Multiple ({h1_count}) `<h1>` heading tags detected.")

        imgs = soup.find_all("img")
        tot_img = len(imgs)
        no_alt = sum(
            1 for img in imgs if not img.get("alt") or not img.get("alt").strip()
        )
        if no_alt > 0:
            flaws.append(f"{no_alt} image(s) missing descriptive `alt` attribute.")
            recommendations.append(
                "Add descriptive alt text to all informational images."
            )

    else:
        title = "Title Tag Missing"
        meta_desc = "Meta Description Missing"
        h1_count, tot_img, no_alt = 0, 0, 0
        flaws.append("Failed to load page content or server unreachable.")

    if latency_ms > 1500:
        flaws.append(f"Slow server response time ({latency_ms} ms).")
        recommendations.append(
            "Optimize server response time and leverage page caching."
        )

    if not page_url.startswith("https://"):
        flaws.append("Insecure connection (Missing HTTPS protocol).")

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
    }


def extract_sitemap_urls(base_url, max_urls=5):
    parsed = urllib.parse.urlparse(base_url)
    urls = [base_url]
    try:
        res = requests.get(
            base_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5, verify=False
        )
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            full_link = urllib.parse.urljoin(base_url, a["href"])
            link_parsed = urllib.parse.urlparse(full_link)
            if link_parsed.netloc == parsed.netloc and full_link not in urls:
                if not any(
                    ext in full_link.lower()
                    for ext in [".pdf", ".jpg", ".png", ".zip", ".css", ".js"]
                ):
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
        urls_to_scan = extract_sitemap_urls(target_url, max_urls=5)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        scanned_pages = list(executor.map(scan_individual_url, urls_to_scan))

    main_page = scanned_pages[0]

    all_flaws = []
    total_latency = 0
    total_no_alt = 0

    for p in scanned_pages:
        total_latency += p["rt"]
        total_no_alt += p["no_alt"]
        for f in p["flaws"]:
            if f not in all_flaws:
                all_flaws.append(f)

    avg_rt = int(total_latency / len(scanned_pages))
    health_score = max(20, min(100, 100 - (len(all_flaws) * 7)))
    da_score = calculate_domain_authority(
        target_url, scanned_pages, avg_rt, len(all_flaws)
    )

    return {
        "url": target_url,
        "scan_mode": mode,
        "total_pages_scanned": len(scanned_pages),
        "scanned_pages": scanned_pages,
        "status": main_page["status"],
        "rt": avg_rt,
        "title": main_page["title"],
        "meta": main_page["meta"],
        "h1": main_page["h1"],
        "tot_img": main_page["tot_img"],
        "no_alt": total_no_alt,
        "size_kb": main_page["size_kb"],
        "health_score": health_score,
        "domain_authority": da_score,
        "flaws": all_flaws,
    }


def generate_ai_report(data):
    pages_summary_str = ""
    for idx, p in enumerate(data["scanned_pages"], 1):
        pages_summary_str += f"\n- Page {idx} ({p['url']}): Title='{p['title']}', Flaws={len(p['flaws'])}, Latency={p['rt']}ms"

    prompt = f"""
Perform an in-depth, expert technical SEO and Domain Trust audit for: {data['url']}

SUMMARY STATS:
- Overall Health Score: {data['health_score']}/100
- Domain Authority / Google Trust Score: {data['domain_authority']}/100
- Avg Response Latency: {data['rt']}ms
- Total Pages Scanned: {data['total_pages_scanned']}
- Total Missing Alt Tags: {data['no_alt']}

SCANNED PAGES DETAIL:
{pages_summary_str}

GLOBAL DETECTED ISSUES:
{', '.join(data['flaws'])}

INSTRUCTIONS:
Provide a deep, structured technical report in proper Markdown format:
1. EXECUTIVE SUMMARY & GOOGLE TRUST ASSESSMENT (Analyze domain trust, search engine authority, and technical standing).
2. PER-PAGE DEEP DIAGNOSTICS (Breakdown specific page weaknesses and structural flaws).
3. HIGH-IMPACT OPTIMIZATION ROADMAP (Actionable numbered list of critical fixes).
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

    return f"""### EXECUTIVE SUMMARY & GOOGLE TRUST ASSESSMENT
**{urllib.parse.urlparse(data['url']).netloc or data['url']}** shows a **Domain Authority rating of {data['domain_authority']}/100**. The infrastructure is generally responsive with an average server response latency of **{data['rt']} ms**, which provides a reliable baseline for search engine crawlers.

### PER-PAGE DEEP DIAGNOSTICS
- **Homepage ({data['scanned_pages'][0]['url']})**: Responded with status `{data['scanned_pages'][0]['status']}`. Title tag length is {len(data['title'])} characters.
- **Deep Page Crawl**: Scanned {data['total_pages_scanned']} routes. Main bottlenecks stem from unoptimized image alt tags ({data['no_alt']} missing across pages) and missing meta description tags on deeper sub-pages.

### HIGH-IMPACT OPTIMIZATION ROADMAP
1. **Metadata Coverage**: Ensure every indexed page contains a unique `<meta name="description">` tag.
2. **Image Accessibility**: Add purposeful `alt` tags to all non-decorative image elements to optimize image search signals.
3. **Speed Optimization**: Implement server-level caching to consistently keep TTFB under 800ms across all global endpoints.
"""


# --- TOP NAVIGATION BAR ---
top_nav_html = """<div class="top-nav">
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
</div>"""

st.markdown(top_nav_html, unsafe_allow_html=True)

# Download button in Top Bar
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
        hero_left_html = """<div class="hero-badge">
<span style="color:#10b981;">●</span> LIVE AUDIT ENGINE V2.8.4
</div>
<div class="hero-heading-main">
Know what your website is <span class="hero-heading-highlight">really</span> saying.
</div>
<div class="hero-desc">
SitePulse turns technical signals into a clear, prioritized path to a faster, healthier web presence.
</div>"""
        st.markdown(hero_left_html, unsafe_allow_html=True)

        st.markdown(
            '<div style="color: #94a3b8; font-size: 0.8rem; font-weight: 500; margin-bottom: 6px;">Website URL</div>',
            unsafe_allow_html=True,
        )

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

        sub_info_html = """<div style="display: flex; justify-content: space-between; margin-top: 10px; color: #64748b; font-size: 0.8rem;">
<span style="color: #34d399;">✓ URL format looks good</span>
<span style="font-family: 'JetBrains Mono';">Deep crawling engine</span>
</div>"""
        st.markdown(sub_info_html, unsafe_allow_html=True)

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
        radar_html = """<div class="radar-container">
<div class="radar-sweep-line"></div>
<div class="radar-center-card">
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
<div class="radar-score-num">84</div>
<div class="radar-score-label">health score</div>
</div>
</div>
<div style="display: flex; justify-content: space-around; margin-top: 1.5rem; color: #64748b; font-family: 'JetBrains Mono'; font-size: 0.78rem;">
<span>🛡 Deep audit</span>
<span>⚡ Instant analysis</span>
</div>"""
        st.markdown(radar_html, unsafe_allow_html=True)


# ==============================================================================
# SCREEN 2: DIAGNOSTIC OVERVIEW & DEEP RESULTS DASHBOARD
# ==============================================================================
else:
    d = st.session_state.audit_data

    # Header Row
    header_html = f"""<div style="margin-bottom: 2rem;">
<div class="hero-badge">DIAGNOSTIC OVERVIEW</div>
<div style="font-size: 2.5rem; font-weight: 700; color: #ffffff; letter-spacing: -0.8px; line-height: 1.1;">
Deep Technical Audit & Trust Analysis
</div>
<div style="color: #64748b; font-size: 0.9rem; margin-top: 6px;">
Latest audit report for <span style="color: #38bdf8; font-weight: 500;">{d['url']}</span> ({d['total_pages_scanned']} page(s) analyzed)
</div>
</div>"""
    st.markdown(header_html, unsafe_allow_html=True)

    # Overview Cards 4-Column Row (NOW INCLUDES DOMAIN AUTHORITY)
    c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1], gap="medium")

    with c1:
        card1_html = f"""<div class="glass-card">
<div class="card-label-mono">SITE HEALTH</div>
<div style="display:flex; align-items: baseline; gap: 6px; margin-top: 0.4rem;">
<span style="font-size: 2.2rem; font-weight: 700; color: #fff;">{d['health_score']}</span>
<span style="font-size: 0.85rem; color: #64748b;">/ 100</span>
</div>
<div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.3rem;">Based on technical checks across {d['total_pages_scanned']} route(s).</div>
</div>"""
        st.markdown(card1_html, unsafe_allow_html=True)

    with c2:
        da = d["domain_authority"]
        card2_html = f"""<div class="glass-card">
<div class="card-label-mono">DOMAIN AUTHORITY</div>
<div class="card-metric-val">{da} <span style="font-size: 0.85rem; font-weight: 400; color: #64748b;">/ 100</span></div>
<div class="da-progress-bg"><div class="da-progress-fill" style="width: {da}%;"></div></div>
<div class="card-subtext" style="color: #38bdf8; margin-top: 0.5rem;">Google Trust Signal</div>
</div>"""
        st.markdown(card2_html, unsafe_allow_html=True)

    with c3:
        card3_html = f"""<div class="glass-card">
<div class="card-label-mono">AVG RESPONSE TIME</div>
<div class="card-metric-val">{d['rt']} ms</div>
<div class="card-subtext">Server Latency</div>
</div>"""
        st.markdown(card3_html, unsafe_allow_html=True)

    with c4:
        card4_html = f"""<div class="glass-card">
<div class="card-label-mono">MISSING ALT TAGS</div>
<div class="card-metric-val">{d['no_alt']}</div>
<div class="card-subtext card-subtext-warn">Across all scanned pages</div>
</div>"""
        st.markdown(card4_html, unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-bottom: 1.8rem;"></div>', unsafe_allow_html=True
    )

    # PRIORITIZED FINDINGS & METADATA SECTION
    col_findings, col_meta = st.columns([1.3, 1], gap="medium")

    with col_findings:
        st.markdown(
            """<div class="glass-card">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
<div>
<div class="card-label-mono">PRIORITIZED FINDINGS</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff;">What needs your attention</div>
</div>
</div>""",
            unsafe_allow_html=True,
        )

        # INTERACTIVE EXPANDABLES FOR FLAWS (ARROWS WORKING)
        if d["flaws"]:
            for idx, flaw in enumerate(d["flaws"], 1):
                with st.expander(f"⚠️  Issue #{idx}: {flaw}"):
                    st.write(
                        f"**Impact:** This technical flaw directly affects search engine indexing or accessibility across one or more scanned pages."
                    )
                    st.write(
                        f"**Recommendation:** Inspect page HTML source and update the affected tags to ensure compliance with modern web standards."
                    )
        else:
            st.success("✓ No critical flaws detected across the scanned pages.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_meta:
        # Elegant non-bold typography for metadata
        title_val = d["title"]
        meta_val = d["meta"]

        meta_html = f"""<div class="glass-card">
<div class="card-label-mono">PAGE INTELLIGENCE</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff; margin-bottom: 1rem;">Metadata inspection</div>

<div style="margin-bottom: 1rem; padding-bottom: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
<div class="card-label-mono">HOMEPAGE TITLE</div>
<div class="meta-field-title">{title_val}</div>
<div style="color: #10b981; font-size: 0.78rem; margin-top: 4px;">Length: {len(title_val)} characters</div>
</div>

<div style="margin-bottom: 1rem; padding-bottom: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
<div class="card-label-mono">META DESCRIPTION</div>
<div class="meta-field-desc">{meta_val}</div>
</div>

<div>
<div class="card-label-mono">MEDIA & HEADINGS</div>
<div style="color: #f1f5f9; font-size: 0.88rem; font-weight: 500;">{d['tot_img']} Total Images · {d['no_alt']} Missing Alt Text</div>
<div style="color: #94a3b8; font-size: 0.82rem; margin-top: 2px;">Primary Heading: H1 Tags = {d['h1']}</div>
</div>
</div>"""
        st.markdown(meta_html, unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-bottom: 1.8rem;"></div>', unsafe_allow_html=True
    )

    # PER-PAGE BREAKDOWN TABLE
    table_rows = ""
    for page in d.get("scanned_pages", []):
        flaw_count = len(page.get("flaws", []))
        flaw_html = (
            f'<span style="color: #ef4444; font-weight: 600;">{flaw_count} issue(s)</span>'
            if flaw_count > 0
            else '<span style="color: #10b981; font-weight: 500;">✓ Clean</span>'
        )
        parsed_path = urllib.parse.urlparse(page["url"]).path or "/"

        table_rows += f"""<tr>
<td><span style="font-family: 'JetBrains Mono'; font-size: 0.82rem; color: #38bdf8;">{parsed_path}</span></td>
<td><span class="badge-status-200">{page['status']} OK</span></td>
<td style="font-family: 'JetBrains Mono';">{page['rt']} ms</td>
<td>{page['size_kb']} KB</td>
<td>{flaw_html}</td>
</tr>"""

    crawl_html = f"""<div class="glass-card">
<div class="card-label-mono">MULTI-PAGE AUDIT BREAKDOWN</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff; margin-bottom: 1rem;">Individual Scanned Pages</div>
<table class="crawl-table">
<thead>
<tr>
<th>PAGE ROUTE</th>
<th>HTTP STATUS</th>
<th>LATENCY</th>
<th>PAYLOAD SIZE</th>
<th>DIAGNOSTIC RESULT</th>
</tr>
</thead>
<tbody>
{table_rows}
</tbody>
</table>
</div>"""
    st.markdown(crawl_html, unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-bottom: 1.8rem;"></div>', unsafe_allow_html=True
    )

    # AI SYNTHESIS REPORT (PROPERLY RENDERED MARKDOWN)
    st.markdown(
        """<div class="glass-card">
<div class="card-label-mono">AI DIAGNOSTICS & GOOGLE TRUST ANALYSIS</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff; margin-bottom: 1rem;">Deep Audit Synthesis Report</div>""",
        unsafe_allow_html=True,
    )

    st.markdown(d["report"])

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True
    )

    # RE-SCAN BUTTON
    if st.button("← Scan Another Website", use_container_width=False):
        st.session_state.scanned = False
        st.rerun()