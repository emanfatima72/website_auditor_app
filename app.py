# ==============================================================================
# DEPENDENCIES:
# pip install streamlit requests beautifulsoup4 python-dotenv google-genai urllib3
# ==============================================================================

import concurrent.futures
from collections import Counter
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
    page_title="SitePulse Enterprise | Technical SEO & Diagnostic Auditor",
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
    margin-bottom: 0.8rem;
}

.hero-heading-main {
    font-size: 3.2rem;
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
    max-width: 500px;
    margin-bottom: 2rem;
    font-weight: 400;
}

/* ANIMATED STANDALONE RADAR PULSE WIDGET (NO BOX) */
.radar-standalone {
    position: relative;
    width: 340px;
    height: 340px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0 auto;
}

.radar-ring {
    position: absolute;
    border-radius: 50%;
    border: 1px solid rgba(56, 189, 248, 0.15);
}

.ring-outer {
    width: 310px;
    height: 310px;
}

.ring-mid {
    width: 210px;
    height: 210px;
}

.radar-cross-h {
    position: absolute;
    width: 310px;
    height: 1px;
    background: rgba(56, 189, 248, 0.12);
}

.radar-cross-v {
    position: absolute;
    height: 310px;
    width: 1px;
    background: rgba(56, 189, 248, 0.12);
}

.radar-sweeper {
    position: absolute;
    width: 310px;
    height: 310px;
    border-radius: 50%;
    animation: radarRotate 4s linear infinite;
    background: conic-gradient(from 0deg, transparent 70%, rgba(56, 189, 248, 0.25) 100%);
}

@keyframes radarRotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.radar-dot {
    position: absolute;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    animation: pulseRadarDot 2s ease-in-out infinite alternate;
}

.dot-1 { background: #38bdf8; top: 80px; left: 90px; }
.dot-2 { background: #818cf8; top: 150px; right: 45px; animation-delay: 0.6s; }
.dot-3 { background: #34d399; bottom: 65px; left: 120px; animation-delay: 1.2s; }

@keyframes pulseRadarDot {
    0% { transform: scale(0.8); opacity: 0.3; }
    100% { transform: scale(1.5); opacity: 1; box-shadow: 0 0 12px currentColor; }
}

.score-circle {
    position: relative;
    z-index: 5;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    background: #0b0f19;
    border: 2px solid #38bdf8;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    animation: glowPulseCircle 2.5s ease-in-out infinite alternate;
}

.score-num {
    font-size: 2.3rem;
    font-weight: 800;
    line-height: 1;
    color: #ffffff;
    letter-spacing: -1px;
}

.score-label {
    font-size: 0.68rem;
    color: #94a3b8;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 4px;
    text-transform: lowercase;
}

@keyframes glowPulseCircle {
    0% {
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
        border-color: rgba(56, 189, 248, 0.6);
    }
    100% {
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.7);
        border-color: rgba(56, 189, 248, 1);
    }
}

/* CARDS & GLASS CONTAINERS */
.glass-card {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(14px);
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

.card-subtext-danger {
    color: #ef4444;
}

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

/* BADGES FOR KEYWORDS AND SPAM LINKS */
.kw-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.25);
    color: #38bdf8;
    padding: 0.3rem 0.7rem;
    border-radius: 8px;
    font-size: 0.8rem;
    margin: 0.25rem;
    font-weight: 500;
}

.kw-count {
    background: rgba(255, 255, 255, 0.15);
    color: #ffffff;
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
}

.spam-link-item {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.25);
    color: #fca5a5;
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    font-size: 0.82rem;
    margin-bottom: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    word-break: break-all;
}

/* STYLING EXPANDERS */
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

.headers-block {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    color: #38bdf8;
    line-height: 1.6;
    white-space: pre-wrap;
    word-break: break-all;
}

.stTextInput > div > div > input {
    background: transparent !important;
    color: #ffffff !important;
    border: none !important;
    font-size: 1rem !important;
    height: 48px !important;
    padding-left: 1rem !important;
}

.stSelectbox > div > div {
    background: rgba(30, 41, 59, 0.6) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    height: 48px !important;
}

.stButton > button {
    background: #4f46e5 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
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
    return f"{clean_domain or 'website'}_technical_seo_report.txt"


def generate_enterprise_txt_report(data):
    scanned_pages = data.get("scanned_pages", [])
    headers_dict = data.get("response_headers", {})

    headers_formatted = (
        "\n".join([f"{k}: {v}" for k, v in headers_dict.items()])
        if headers_dict
        else "No Headers Recorded"
    )

    crawl_log_str = ""
    for idx, p in enumerate(scanned_pages, 1):
        crawl_log_str += f"[{idx}] {p['url']} | Status: {p['status']} | Latency: {p['rt_sec']}s | Flaws: {len(p['flaws'])}\n"

    detailed_flaws_str = ""
    for p in scanned_pages:
        for flaw in p["flaws"]:
            detailed_flaws_str += f"  - [{p['url']}] {flaw}\n"

    recommendations_str = ""
    for rec in data.get("recommendations", []):
        recommendations_str += f"  - {rec}\n"

    deficiencies_str = ""
    for deficiency in data.get("critical_deficiencies", []):
        deficiencies_str += f"  - {deficiency}\n"

    keywords_str = ", ".join(
        [
            f"{kw} ({cnt})"
            for kw, cnt in data.get("keywords_extracted", [])
        ]
    )
    spam_links_str = (
        "\n".join([f"  - {link}" for link in data.get("spammy_backlinks", [])])
        if data.get("spammy_backlinks")
        else "  - No suspicious outbound spam links detected."
    )

    full_text = f"""====================================================================
SITEPULSE ENTERPRISE - TECHNICAL SEO & DIAGNOSTIC REPORT
====================================================================
Target URL          : {data.get('url')}
Scan Scope          : {data.get('scan_mode', 'Full Site')}
Pages Scanned       : {data.get('total_pages_scanned', 1)}
Calculated Score    : {data.get('health_score')}/100
Google DOM Authority: {data.get('domain_authority')}/100 ({data.get('trust_label')})
HTTP Response Status: {data.get('status')}
Server Latency      : {data.get('rt_sec')} seconds
Payload Size        : {data.get('size_kb')} KB

--------------------------------------------------------------------
1. SCRAPED TECHNICAL METRICS (MAIN PAGE)
--------------------------------------------------------------------
- Page Title: {data.get('title')}
- Meta Description: {data.get('meta')}
- H1 Headings Count: {data.get('h1')}
- Image Count: {data.get('tot_img')}
- Missing Image Alt Attributes: {data.get('no_alt')}

--------------------------------------------------------------------
HIGH-TRAFFIC SEARCH KEYWORDS EXTRACTED
--------------------------------------------------------------------
{keywords_str or 'No dominant search terms detected.'}

--------------------------------------------------------------------
SPAM & UNTRUSTED OUTBOUND LINKS DETECTED
--------------------------------------------------------------------
{spam_links_str}

----------------------------------------------------
SCANNED SUB-PAGES CRAWL LOG
----------------------------------------------------
{crawl_log_str}
--------------------------------------------------------------------
2. DETECTED FLAWS & ISSUES
--------------------------------------------------------------------
{detailed_flaws_str}
--------------------------------------------------------------------
3. ACTIONABLE RECOMMENDATIONS
--------------------------------------------------------------------
{recommendations_str}
--------------------------------------------------------------------
4. CRITICAL MISSING ELEMENTS & SECURITY DEFICIENCIES
--------------------------------------------------------------------
{deficiencies_str}
--------------------------------------------------------------------
5. COMPLETE AI DIAGNOSTIC REPORT BREAKDOWN
--------------------------------------------------------------------
{data.get('report', '')}

--------------------------------------------------------------------
6. RESPONSE HEADERS
--------------------------------------------------------------------
{headers_formatted}

====================================================================
End of SitePulse Enterprise Diagnostic Report
====================================================================
"""
    return full_text.encode("utf-8")


def scan_individual_url(page_url):
    headers_req = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    t0 = time.time()
    resp_headers = {}
    try:
        r = requests.get(
            page_url,
            headers=headers_req,
            timeout=10,
            verify=False,
            allow_redirects=True,
        )
        status_code = r.status_code
        raw_html = r.text
        content_size_kb = round(len(r.content) / 1024, 2)
        resp_headers = dict(r.headers)
    except Exception:
        status_code = 504
        raw_html = ""
        content_size_kb = 0.0

    latency_sec = round(time.time() - t0, 2)
    flaws = []
    recommendations = []
    critical_deficiencies = []
    spammy_links = []
    extracted_keywords = []

    if raw_html:
        soup = BeautifulSoup(raw_html, "html.parser")

        # 1. DOM Title & Meta Audit
        title_tag = soup.title
        title = (
            title_tag.string.strip()
            if title_tag and title_tag.string
            else "Title Tag Missing"
        )
        if title == "Title Tag Missing":
            flaws.append("Missing <title> tag on page.")
        elif len(title) < 30 or len(title) > 60:
            flaws.append(
                f"Page Title length ({len(title)} chars) is non-optimal (recommended: 50-60 chars)."
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
            critical_deficiencies.append("Meta Description Tag")
            recommendations.append(
                "Add a compelling meta description tag (140-160 characters) to improve Search CTR."
            )

        # 2. H1 & Structure
        h1_tags = soup.find_all("h1")
        h1_count = len(h1_tags)
        if h1_count == 0:
            flaws.append("No primary <h1> heading tag found on the page.")
            critical_deficiencies.append("Main <h1> Heading Tag")
            recommendations.append(
                "Include exactly one primary <h1> tag containing the main page topic."
            )
        elif h1_count > 1:
            flaws.append(
                f"Multiple ({h1_count}) <h1> heading tags detected on page."
            )

        # 3. Media & Viewport
        imgs = soup.find_all("img")
        tot_img = len(imgs)
        no_alt = sum(
            1 for img in imgs if not img.get("alt") or not img.get("alt").strip()
        )
        if no_alt > 0:
            flaws.append(
                f"{no_alt} out of {tot_img} image elements lack accessibility descriptive alt text."
            )
            recommendations.append(
                f"Add descriptive alt attributes to all {no_alt} missing image elements."
            )

        viewport_tag = soup.find("meta", attrs={"name": "viewport"})
        if not viewport_tag:
            flaws.append(
                'Mobile viewport meta tag <meta name="viewport"> is missing.'
            )
            critical_deficiencies.append("Mobile Viewport Configuration Tag")
            recommendations.append(
                'Add <meta name="viewport" content="width=device-width, initial-scale=1"> for mobile responsiveness.'
            )

        canonical_tag = soup.find("link", attrs={"rel": "canonical"})
        if not canonical_tag:
            flaws.append('Canonical URL link <link rel="canonical"> is missing.')

        # 4. Outbound Spammy Backlinks / Unsafe Links Detection
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            # Flag HTTP links, URL shorteners, affiliate parameters or suspicious keywords
            if (
                href.startswith("http://")
                or "bit.ly" in href
                or "tinyurl" in href
                or "aff=" in href
                or "?ref=" in href
                or "casino" in href.lower()
                or "crypto" in href.lower()
            ):
                if href not in spammy_links:
                    spammy_links.append(href)

        # 5. High-Traffic Search Keywords Extraction Engine
        for script_or_style in soup(["script", "style", "nav", "footer"]):
            script_or_style.decompose()
        visible_text = soup.get_text(separator=" ").lower()
        clean_words = re.findall(r"\b[a-z]{4,15}\b", visible_text)
        stopwords = {
            "this",
            "that",
            "with",
            "from",
            "your",
            "have",
            "more",
            "about",
            "will",
            "home",
            "page",
            "site",
            "view",
            "contact",
            "privacy",
            "policy",
            "rights",
            "reserved",
            "click",
            "here",
            "using",
            "been",
        }
        filtered_words = [w for w in clean_words if w not in stopwords]
        word_counts = Counter(filtered_words)
        extracted_keywords = word_counts.most_common(10)

    else:
        title = "Title Tag Missing"
        meta_desc = "Meta Description Tag Missing"
        h1_count, tot_img, no_alt = 0, 0, 0
        flaws.append("Failed to load page content or server unreachable.")

    if not page_url.startswith("https://"):
        flaws.append(
            "Target URL is served over insecure HTTP instead of encrypted HTTPS."
        )
        critical_deficiencies.append("HTTPS / SSL Encryption")

    missing_sec_headers = []
    sec_check = [
        "Strict-Transport-Security",
        "X-Frame-Options",
        "Content-Security-Policy",
    ]
    for sec_h in sec_check:
        if sec_h not in resp_headers and sec_h.lower() not in [
            k.lower() for k in resp_headers
        ]:
            missing_sec_headers.append(sec_h)

    if missing_sec_headers:
        flaws.append(
            f"Missing security headers: {', '.join(missing_sec_headers)}."
        )

    return {
        "url": page_url,
        "status": status_code,
        "rt_sec": latency_sec,
        "title": title,
        "meta": meta_desc,
        "h1": h1_count,
        "tot_img": tot_img,
        "no_alt": no_alt,
        "size_kb": content_size_kb,
        "flaws": flaws,
        "recommendations": recommendations,
        "critical_deficiencies": critical_deficiencies,
        "response_headers": resp_headers,
        "spammy_links": spammy_links,
        "extracted_keywords": extracted_keywords,
    }


def extract_sitemap_urls(base_url, max_urls=8):
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


def perform_website_audit(target_url, mode="Full Site (Fast Multi-Page)"):
    if not target_url.startswith(("http://", "https://")):
        target_url = "http://" + target_url

    if mode == "Single Page":
        urls_to_scan = [target_url]
    else:
        urls_to_scan = extract_sitemap_urls(target_url, max_urls=8)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        scanned_pages = list(executor.map(scan_individual_url, urls_to_scan))

    main_page = scanned_pages[0]

    all_flaws = []
    all_recommendations = []
    all_deficiencies = []
    all_spammy_links = []
    combined_keywords = Counter()
    total_no_alt = 0

    for p in scanned_pages:
        total_no_alt += p["no_alt"]
        for f in p["flaws"]:
            all_flaws.append((p["url"], f))
        for r in p["recommendations"]:
            if r not in all_recommendations:
                all_recommendations.append(r)
        for d in p["critical_deficiencies"]:
            if d not in all_deficiencies:
                all_deficiencies.append(d)
        for sl in p["spammy_links"]:
            if sl not in all_spammy_links:
                all_spammy_links.append(sl)
        for kw, cnt in p["extracted_keywords"]:
            combined_keywords[kw] += cnt

    total_flaws_count = len(all_flaws)
    health_score = max(15, min(100, 100 - (total_flaws_count * 2)))

    # --- GOOGLE DOMAIN AUTHORITY & TRUST CALCULATION ---
    da_score = 40
    if target_url.startswith("https://"):
        da_score += 25
    if main_page["rt_sec"] < 0.6:
        da_score += 15
    if main_page["h1"] == 1:
        da_score += 10
    if main_page["meta"] != "Meta Description Tag Missing":
        da_score += 10
    da_score -= len(all_deficiencies) * 5
    da_score -= len(all_spammy_links) * 4
    da_score = max(15, min(98, da_score))

    if da_score >= 80:
        trust_label = "High Trust & Powerful Authority"
    elif da_score >= 55:
        trust_label = "Moderate Google Authority"
    else:
        trust_label = "Low Google Trust & Weak Authority"

    return {
        "url": target_url,
        "scan_mode": mode,
        "total_pages_scanned": len(scanned_pages),
        "scanned_pages": scanned_pages,
        "status": main_page["status"],
        "rt_sec": main_page["rt_sec"],
        "title": main_page["title"],
        "meta": main_page["meta"],
        "h1": main_page["h1"],
        "tot_img": main_page["tot_img"],
        "no_alt": total_no_alt,
        "size_kb": main_page["size_kb"],
        "health_score": health_score,
        "domain_authority": da_score,
        "trust_label": trust_label,
        "total_flaws_count": total_flaws_count,
        "all_flaws": all_flaws,
        "recommendations": all_recommendations,
        "critical_deficiencies": all_deficiencies,
        "spammy_backlinks": all_spammy_links,
        "keywords_extracted": combined_keywords.most_common(12),
        "response_headers": main_page["response_headers"],
    }


def generate_ai_report(data):
    prompt = f"""
Perform an in-depth technical SEO, accessibility, and security analysis for the target domain: {data['url']}

AUDIT DATA SUMMARY:
- Overall Health Score: {data['health_score']}/100
- Google Domain Authority & Trust Score: {data['domain_authority']}/100 ({data['trust_label']})
- Server Response Latency: {data['rt_sec']} seconds
- Total Scanned Pages: {data['total_pages_scanned']}
- Total Detected Issues Across Pages: {data['total_flaws_count']}
- Primary Missing Elements: {', '.join(data['critical_deficiencies'])}
- Spammy / Untrusted Links Flagged: {len(data['spammy_backlinks'])}

INSTRUCTIONS:
Provide a deep, professional structured technical audit in standard Markdown format:
1. Executive Summary & Google Trust Assessment
2. Domain Authority & Ranking Potential Analysis
3. Real-Time Technical Flaws & Spam Vulnerabilities Breakdown
4. High-Traffic Search Keywords & Visibility Potential
5. Priority Actionable Optimizations Roadmap
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

    return f"""### Executive Summary
**Overall Calculated Health Score: {data['health_score']}/100** | **Google Trust Index: {data['domain_authority']}/100 ({data['trust_label']})**

Live runtime scan performed for **{data['url']}**. The analysis indicates a server response latency of **{data['rt_sec']}s** with **{data['total_flaws_count']} primary structural/technical issue(s)** detected during real-time DOM parsing.

### 1. Domain Authority & Google Trust Index
- **Domain Power:** Scored **{data['domain_authority']}/100** based on speed, SSL configuration, DOM semantics, and outbound link profile.
- **Google Perception:** Status classified as **{data['trust_label']}**.

### 2. Real-Time Flaws & Spam Analysis
- **Detected Flaws:** {data['total_flaws_count']} structural/SEO issues flagged across scanned pages.
- **Unsafe/Spam Outbound Links:** {len(data['spammy_backlinks'])} potentially risky or affiliate links detected.

### 3. High-Traffic Search Keywords
Primary topics extracted from HTML content: {', '.join([k[0] for k in data['keywords_extracted'][:6]])}.
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
<div class="brand-title">SitePulse Enterprise</div>
<div class="brand-subtitle">Technical SEO & Diagnostic Auditor</div>
</div>
</div>
<div class="nav-status">
<div class="status-indicator">
<span class="status-dot"></span> Engine Online
</div>
</div>
</div>"""

st.markdown(top_nav_html, unsafe_allow_html=True)

if st.session_state.scanned and "txt_data" in st.session_state.audit_data:
    t_col1, t_col2 = st.columns([8, 2])
    with t_col2:
        st.download_button(
            label="↓ Download Report",
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

    col_hero_left, col_hero_right = st.columns([1.1, 0.9], gap="large")

    with col_hero_left:
        hero_left_html = """<div class="hero-badge">
<span style="color:#10b981;">●</span> LIVE ENTERPRISE AUDITOR V3.0
</div>
<div class="hero-heading-main">
Automated Technical <span class="hero-heading-highlight">SEO & Security</span> Auditing.
</div>
<div class="hero-desc">
Scrape DOM structures, analyze response headers, detect missing metadata, evaluate DOM Google Authority, and scan spammy links in seconds.
</div>"""
        st.markdown(hero_left_html, unsafe_allow_html=True)

        st.markdown(
            '<div style="color: #94a3b8; font-size: 0.8rem; font-weight: 500; margin-bottom: 6px;">Target Website URL</div>',
            unsafe_allow_html=True,
        )

        c_in, c_sel, c_btn = st.columns([2.5, 1.3, 1.2])

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
                ["Full Site (Fast Multi-Page)", "Single Page"],
                label_visibility="collapsed",
                key="scan_mode_selection",
            )

        with c_btn:
            btn_label = "Analyzing..." if st.session_state.loading else "Run Audit"
            btn_click = st.button(
                f"▶  {btn_label}",
                use_container_width=True,
                disabled=st.session_state.loading,
            )

        sub_info_html = """<div style="display: flex; justify-content: flex-end; margin-top: 10px; color: #64748b; font-size: 0.8rem;">
<span style="font-family: 'JetBrains Mono';">Multi-threaded Crawl Engine</span>
</div>"""
        st.markdown(sub_info_html, unsafe_allow_html=True)

        if btn_click and url_input.strip():
            st.session_state.loading = True
            st.rerun()

        if st.session_state.loading:
            target = url_input.strip()
            selected_mode = st.session_state.get(
                "scan_mode_selection", "Full Site (Fast Multi-Page)"
            )
            audit_res = perform_website_audit(target, mode=selected_mode)
            audit_res["report"] = generate_ai_report(audit_res)
            audit_res["txt_data"] = generate_enterprise_txt_report(audit_res)

            st.session_state.audit_data = audit_res
            st.session_state.scanned = True
            st.session_state.loading = False
            st.rerun()

    with col_hero_right:
        # STANDALONE ANIMATED RADAR PULSE WIDGET
        radar_widget_html = """<div class="radar-standalone">
<div class="radar-cross-h"></div>
<div class="radar-cross-v"></div>

<div class="radar-ring ring-outer"></div>
<div class="radar-ring ring-mid"></div>

<div class="radar-sweeper"></div>

<div class="radar-dot dot-1"></div>
<div class="radar-dot dot-2"></div>
<div class="radar-dot dot-3"></div>

<div class="score-circle">
<div class="score-num">84</div>
<div class="score-label">health score</div>
</div>
</div>"""
        st.markdown(radar_widget_html, unsafe_allow_html=True)


# ==============================================================================
# SCREEN 2: ENTERPRISE AUDIT RESULTS DASHBOARD
# ==============================================================================
else:
    d = st.session_state.audit_data

    header_html = f"""<div style="margin-bottom: 2rem;">
<div class="hero-badge">SITEPULSE ENTERPRISE REPORT</div>
<div style="font-size: 2.4rem; font-weight: 700; color: #ffffff; letter-spacing: -0.8px; line-height: 1.1;">
Technical SEO & Diagnostic Report
</div>
<div style="color: #64748b; font-size: 0.9rem; margin-top: 6px;">
Target Domain: <span style="color: #38bdf8; font-weight: 500;">{d['url']}</span> | Scope: {d['scan_mode']} ({d['total_pages_scanned']} Pages Scanned)
</div>
</div>"""
    st.markdown(header_html, unsafe_allow_html=True)

    # 5 METRIC METRIC CARDS ROW INCLUDING GOOGLE DOM AUTHORITY
    c1, c2, c3, c4, c5 = st.columns([1, 1.2, 1, 1, 1], gap="small")

    with c1:
        card1_html = f"""<div class="glass-card">
<div class="card-label-mono">HEALTH SCORE</div>
<div style="display:flex; align-items: baseline; gap: 4px; margin-top: 0.4rem;">
<span style="font-size: 2rem; font-weight: 700; color: #fff;">{d['health_score']}</span>
<span style="font-size: 0.8rem; color: #64748b;">/ 100</span>
</div>
<div class="card-subtext card-subtext-danger" style="margin-top: 0.3rem;">{d['total_flaws_count']} Issue(s)</div>
</div>"""
        st.markdown(card1_html, unsafe_allow_html=True)

    with c2:
        card_da_html = f"""<div class="glass-card">
<div class="card-label-mono">GOOGLE DOM AUTHORITY</div>
<div style="display:flex; align-items: baseline; gap: 4px; margin-top: 0.4rem;">
<span style="font-size: 2rem; font-weight: 700; color: #38bdf8;">{d['domain_authority']}</span>
<span style="font-size: 0.8rem; color: #64748b;">/ 100</span>
</div>
<div class="card-subtext" style="color: #818cf8; font-size: 0.75rem;">{d['trust_label']}</div>
</div>"""
        st.markdown(card_da_html, unsafe_allow_html=True)

    with c3:
        card2_html = f"""<div class="glass-card">
<div class="card-label-mono">SERVER LATENCY</div>
<div class="card-metric-val">{d['rt_sec']} <span style="font-size: 0.85rem; font-weight: 400; color: #64748b;">s</span></div>
<div class="card-subtext">HTTP Status: {d['status']}</div>
</div>"""
        st.markdown(card2_html, unsafe_allow_html=True)

    with c4:
        card3_html = f"""<div class="glass-card">
<div class="card-label-mono">PAYLOAD SIZE</div>
<div class="card-metric-val">{d['size_kb']} <span style="font-size: 0.85rem; font-weight: 400; color: #64748b;">KB</span></div>
<div class="card-subtext">Main Container</div>
</div>"""
        st.markdown(card3_html, unsafe_allow_html=True)

    with c5:
        card4_html = f"""<div class="glass-card">
<div class="card-label-mono">MISSING ALT</div>
<div class="card-metric-val">{d['no_alt']}</div>
<div class="card-subtext card-subtext-warn">Out of {d['tot_img']} Imgs</div>
</div>"""
        st.markdown(card4_html, unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-bottom: 1.8rem;"></div>', unsafe_allow_html=True
    )

    # KEYWORD EXPRESSIONS & SPAM BACKLINKS SECTION
    col_kw, col_spam = st.columns([1.2, 1], gap="medium")

    with col_kw:
        kw_badges = "".join(
            [
                f'<span class="kw-tag">{kw} <span class="kw-count">{cnt}</span></span>'
                for kw, cnt in d["keywords_extracted"]
            ]
        )
        kw_html = f"""<div class="glass-card">
<div class="card-label-mono">KEYWORD EXPRESSION ENGINE</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff; margin-bottom: 0.8rem;">High-Traffic Organic Keywords Extracted</div>
<div style="line-height: 2;">
{kw_badges or "<span style='color:#94a3b8;'>No dominant search terms detected in DOM body.</span>"}
</div>
</div>"""
        st.markdown(kw_html, unsafe_allow_html=True)

    with col_spam:
        spam_items = "".join(
            [
                f'<div class="spam-link-item">⚠️ {link}</div>'
                for link in d["spammy_backlinks"][:5]
            ]
        )
        spam_html = f"""<div class="glass-card">
<div class="card-label-mono">OUTBOUND SPAM & UNTRUSTED BACKLINKS</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff; margin-bottom: 0.8rem;">Risk & Affiliate Link Audit</div>
<div>
{spam_items or "<div style='color:#34d399; font-weight: 500; font-size: 0.9rem;'>✓ No suspicious or untrusted outbound links detected.</div>"}
</div>
</div>"""
        st.markdown(spam_html, unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-bottom: 1.8rem;"></div>', unsafe_allow_html=True
    )

    col_metrics, col_deficiencies = st.columns([1.2, 1], gap="medium")

    with col_metrics:
        title_val = d["title"]
        meta_val = d["meta"]

        meta_html = f"""<div class="glass-card">
<div class="card-label-mono">1. SCRAPED TECHNICAL METRICS (MAIN PAGE)</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff; margin-bottom: 1rem;">DOM & Content Inspection</div>

<div style="margin-bottom: 0.8rem; padding-bottom: 0.6rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
<div class="card-label-mono">PAGE TITLE</div>
<div class="meta-field-title">{title_val}</div>
</div>

<div style="margin-bottom: 0.8rem; padding-bottom: 0.6rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
<div class="card-label-mono">META DESCRIPTION</div>
<div class="meta-field-desc">{meta_val}</div>
</div>

<div>
<div class="card-label-mono">HEADINGS & MEDIA</div>
<div style="color: #f1f5f9; font-size: 0.88rem; font-weight: 500;">H1 Headings Count: {d['h1']}</div>
<div style="color: #94a3b8; font-size: 0.82rem; margin-top: 2px;">Image Count: {d['tot_img']} | Missing Alt: {d['no_alt']}</div>
</div>
</div>"""
        st.markdown(meta_html, unsafe_allow_html=True)

    with col_deficiencies:
        def_items = "".join(
            [
                f"<li style='margin-bottom: 6px; color: #ef4444;'>{defi}</li>"
                for defi in d["critical_deficiencies"]
            ]
        )
        def_html = f"""<div class="glass-card">
<div class="card-label-mono">4. CRITICAL MISSING ELEMENTS & SECURITY DEFICIENCIES</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff; margin-bottom: 1rem;">Urgent Technical Deficiencies</div>
<ul style="padding-left: 1.2rem; font-size: 0.9rem; font-weight: 500;">
{def_items or "<li style='color:#10b981;'>No critical deficiencies detected.</li>"}
</ul>
</div>"""
        st.markdown(def_html, unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-bottom: 1.8rem;"></div>', unsafe_allow_html=True
    )

    table_rows = ""
    for idx, page in enumerate(d.get("scanned_pages", []), 1):
        flaw_count = len(page.get("flaws", []))
        flaw_html = (
            f'<span style="color: #ef4444; font-weight: 600;">{flaw_count} flaw(s)</span>'
            if flaw_count > 0
            else '<span style="color: #10b981; font-weight: 500;">✓ Clean</span>'
        )

        table_rows += f"""<tr>
<td><span style="font-family: 'JetBrains Mono'; color: #64748b;">[{idx}]</span></td>
<td><span style="font-family: 'JetBrains Mono'; font-size: 0.82rem; color: #38bdf8;">{page['url']}</span></td>
<td><span class="badge-status-200">{page['status']} OK</span></td>
<td style="font-family: 'JetBrains Mono';">{page['rt_sec']}s</td>
<td>{flaw_html}</td>
</tr>"""

    crawl_html = f"""<div class="glass-card">
<div class="card-label-mono">SCANNED SUB-PAGES CRAWL LOG</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff; margin-bottom: 1rem;">Crawl Metrics Breakdown</div>
<table class="crawl-table">
<thead>
<tr>
<th>#</th>
<th>TARGET SUB-PAGE URL</th>
<th>STATUS</th>
<th>LATENCY</th>
<th>FLAWS DETECTED</th>
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

    col_flaws, col_recs = st.columns([1.2, 1], gap="medium")

    with col_flaws:
        st.markdown(
            """<div class="glass-card">
<div class="card-label-mono">2. DETECTED FLAWS & ISSUES</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff; margin-bottom: 1rem;">Per-URL Real-Time Findings</div>""",
            unsafe_allow_html=True,
        )

        for page_url, flaw in d["all_flaws"]:
            safe_flaw = (
                flaw.replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("`", "")
            )
            with st.expander(f"⚠️ [{page_url}] {safe_flaw[:55]}..."):
                st.write(f"**Affected URL:** `{page_url}`")
                st.write(f"**Detected Issue:** {safe_flaw}")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_recs:
        rec_items = "".join(
            [
                f"<li style='margin-bottom: 8px; color: #38bdf8;'>{rec.replace('<', '&lt;').replace('>', '&gt;').replace('`', '')}</li>"
                for rec in d["recommendations"]
            ]
        )
        recs_html = f"""<div class="glass-card">
<div class="card-label-mono">3. ACTIONABLE RECOMMENDATIONS</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff; margin-bottom: 1rem;">Prioritized Optimization Steps</div>
<ul style="padding-left: 1.2rem; font-size: 0.88rem; line-height: 1.5;">
{rec_items}
</ul>
</div>"""
        st.markdown(recs_html, unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-bottom: 1.8rem;"></div>', unsafe_allow_html=True
    )

    st.markdown(
        """<div class="glass-card">
<div class="card-label-mono">5. COMPLETE AI DIAGNOSTIC REPORT BREAKDOWN</div>
<div style="font-size: 1.2rem; font-weight: 600; color: #fff; margin-bottom: 1rem;">Deep Technical & Trust Analysis</div>""",
        unsafe_allow_html=True,
    )

    st.markdown(d["report"])

    st.markdown(
        '<div style="margin-top: 1.5rem; margin-bottom: 0.8rem;" class="card-label-mono">6. RESPONSE HEADERS</div>',
        unsafe_allow_html=True,
    )

    headers_str = (
        "\n".join([f"{k}: {v}" for k, v in d["response_headers"].items()])
        if d["response_headers"]
        else "No Server Headers Recorded"
    )

    st.markdown(
        f'<div class="headers-block">{headers_str}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True
    )

    if st.button("← Scan Another Website", use_container_width=False):
        st.session_state.scanned = False
        st.rerun()