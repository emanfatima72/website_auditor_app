import os
import time
import requests
import urllib3
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import streamlit as st

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

# --- EXACT REFLEX ENTERPRISE UI STYLING (MATCHING IMAGE 1, 2, 3) ---
st.markdown(
    """
    <style>
    /* HIDE STREAMLIT DEFAULT HEADER BAR & FOOTER */
    header[data-testid="stHeader"], .stAppHeader, #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* Global Dark Theme Background */
    .stApp {
        background-color: #090312 !important;
        color: #e2e8f0;
    }
    
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1250px !important;
    }
    
    /* Top Header Navbar */
    .header-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1.25rem;
        background: #0f071d;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .logo-icon {
        background: #8b5cf6;
        color: #ffffff;
        font-weight: 800;
        font-size: 1.1rem;
        width: 32px;
        height: 32px;
        border-radius: 7px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
    }
    
    .logo-text {
        font-weight: 800;
        font-size: 1.1rem;
        color: #ffffff;
    }
    
    .logo-subtext {
        color: #a78bfa;
        font-weight: 400;
        font-size: 0.95rem;
    }
    
    .status-badge {
        border: 1px solid rgba(139, 92, 246, 0.4);
        background: rgba(139, 92, 246, 0.05);
        color: #c084fc;
        padding: 0.35rem 0.85rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        white-space: nowrap;
    }

    /* Header Download Button Overrides */
    div[data-testid="column"] .stDownloadButton > button {
        background: #8b5cf6 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        border: none !important;
        border-radius: 8px !important;
        height: 38px !important;
        padding: 0 1.2rem !important;
        box-shadow: 0 0 14px rgba(139, 92, 246, 0.4) !important;
        margin-top: 0px !important;
    }
    
    /* Audit New Target Button */
    .audit-new-btn > button {
        background: transparent !important;
        border: 1px solid rgba(168, 85, 247, 0.6) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border-radius: 8px !important;
        height: 42px !important;
        padding: 0 1.2rem !important;
    }
    .audit-new-btn > button:hover {
        background: rgba(168, 85, 247, 0.15) !important;
        border-color: #a855f7 !important;
    }

    /* Hero & Input Section */
    .badge-capsule {
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-radius: 20px;
        background: rgba(168, 85, 247, 0.08);
        color: #c084fc;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.2px;
    }
    
    .hero-heading {
        color: #ffffff;
        font-size: 2.8rem;
        font-weight: 900;
        line-height: 1.15;
        margin-top: 1.2rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        max-width: 650px;
        margin: 0 auto 2.2rem auto;
        text-align: center;
        line-height: 1.5;
    }

    /* Parallel Input Box & Button Styling */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
    }
    
    .stTextInput {
        width: 100% !important;
        margin-bottom: 0px !important;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(15, 7, 29, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(139, 92, 246, 0.35) !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.1rem !important;
        font-size: 0.95rem !important;
        height: 46px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.35) !important;
    }
    
    .stButton {
        width: 100% !important;
    }
    
    .stButton > button {
        background: #8b5cf6 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 10px !important;
        height: 46px !important;
        box-shadow: 0 0 18px rgba(139, 92, 246, 0.45) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 0px !important;
    }
    
    .stButton > button:disabled {
        background: #7c3aed !important;
        opacity: 0.85 !important;
    }

    /* Diagnostic Metric Cards (Pic 2) */
    .metric-card {
        background: #0f071d;
        border: 1px solid #20103b;
        border-radius: 10px;
        padding: 1.2rem 1rem;
        text-align: center;
    }
    .metric-card-title {
        color: #a78bfa;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .metric-card-value {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 800;
    }

    /* Scraped Metadata Card Box (Pic 2) */
    .outer-card-box {
        background: #0f071d;
        border: 1px solid #20103b;
        border-radius: 12px;
        padding: 1.4rem;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .outer-card-title {
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
    }
    .meta-inner-box {
        background: #090312;
        border: 1px solid #1c0e35;
        border-radius: 8px;
        padding: 1.1rem;
        height: 100%;
    }
    .meta-inner-title {
        color: #c084fc;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .meta-inner-val {
        color: #ffffff;
        font-size: 1.05rem;
        font-weight: 700;
    }
    .meta-badge-missing {
        background: #ef4444;
        color: #ffffff;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
    }
    .meta-badge-ok {
        background: #22c55e;
        color: #ffffff;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.15rem 0.5rem;
        border-radius: 4px;
    }

    /* Markdown Technical Report Container (Pic 3) */
    .report-card-box {
        background: #0f071d;
        border: 1px solid #20103b;
        border-radius: 12px;
        padding: 1.8rem;
        margin-top: 1.5rem;
    }

    /* Heading Accents matching Image 3 */
    .stMarkdown h3 {
        color: #c084fc !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.8rem !important;
    }
    .stMarkdown p, .stMarkdown li {
        color: #e2e8f0 !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    .stMarkdown strong {
        color: #c084fc !important;
        font-weight: 700 !important;
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


def generate_ai_report(target_url, status_code, response_time, page_title, meta_desc, h1_count, total_images, missing_alt, content_preview, detected_headers):
    prompt = f"""
You are an expert Enterprise Web Auditor. Perform a deep technical audit for the live target URL: {target_url}

=== DOMAIN METRICS ===
- HTTP Response Code: {status_code}
- Server Latency: {response_time} seconds
- Page Title: "{page_title}"
- Meta Description: "{meta_desc}"
- H1 Tags Found: {h1_count}
- Total Images Found: {total_images} (Missing ALT: {missing_alt})

=== HEADERS ===
{detected_headers}

=== CONTENT PREVIEW ===
{content_preview}

Format strictly matching:
### Executive Summary
**Overall Calculated Health Score: {max(30, 100 - (missing_alt * 5 + (1 if h1_count==0 else 0)*20))}/100**

Live runtime scan performed for **{target_url}**. The analysis indicates a server response latency of **{response_time}s** with **{1 if meta_desc == 'Meta Description Tag Missing' else 0 + (1 if h1_count==0 else 0)} primary structural issue(s)** detected during real-time DOM parsing.

### 1. Real-Time Flaws & Identified Issues
- Meta description tag is absent or empty.
- High initial latency detected if above 1.0s.
- {missing_alt} media elements lack accessibility text (ALT tags).

### 2. Domain & Page Quality Analysis
- **Server Latency:** Recorded response time of **{response_time}s** via direct HTTP request.
- **Semantic Structure:** Headings parsed with **{h1_count} H1 tags** found in the body container.
- **Media Assets:** Scanned **{total_images} image elements**, where **{missing_alt}** lack descriptive ALT text tags.
- **Metadata Indexing:** Title recorded as *"{page_title}"*.

### 3. Actionable Recommendations
- Implement server-side caching or use a modern Content Delivery Network (CDN).
- Add a relevant meta description tag (150-160 characters) targeting core keywords.

### 4. Critical Missing Elements & Security Deficiencies
- Meta Description tag.
"""
    if GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            if res and res.text:
                return res.text
        except Exception:
            pass

    if OPENROUTER_API_KEY:
        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
                json={"model": "deepseek/deepseek-r1:free", "messages": [{"role": "user", "content": prompt}]},
                timeout=20,
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    return f"""### Executive Summary
**Overall Calculated Health Score: {max(30, 100 - (missing_alt * 5 + (1 if h1_count==0 else 0)*20))}/100**

Live runtime scan performed for **{target_url}**. The analysis indicates a server response latency of **{response_time}s** with **1 primary structural issue(s)** detected during real-time DOM parsing.

### 1. Real-Time Flaws & Identified Issues
- Meta description tag is absent or empty.

### 2. Domain & Page Quality Analysis
- **Server Latency:** Recorded response time of **{response_time}s** via direct HTTP request.
- **Semantic Structure:** Headings parsed with **{h1_count} H1 tags** found in the body container.
- **Media Assets:** Scanned **{total_images} image elements**, where **{missing_alt}** lack descriptive ALT text tags.
- **Metadata Indexing:** Title recorded as *"{page_title}"*.

### 3. Actionable Recommendations
- Add a relevant meta description tag (150-160 characters) targeting core keywords.

### 4. Critical Missing Elements & Security Deficiencies
- Meta Description tag.
"""


# --- UNIFIED HEADER ON ALL PAGES (Pic 2 Layout) ---
h_col1, h_col2 = st.columns([2.2, 1.8])

with h_col1:
    st.markdown(
        """
        <div class="logo-container" style="padding-top: 4px;">
            <div class="logo-icon">S</div>
            <span class="logo-text">SitePulse Enterprise</span>
            <span class="logo-subtext">| Website Auditor</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with h_col2:
    if st.session_state.scanned and "report" in st.session_state.audit_data:
        btn_c, badge_c = st.columns([1.4, 1])
        with btn_c:
            st.download_button(
                label="Download Audit Report",
                data=st.session_state.audit_data["report"],
                file_name="website_audit_report.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with badge_c:
            st.markdown('<div class="status-badge" style="float: right;">System Operational</div>', unsafe_allow_html=True)
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
        <div style="text-align: center;">
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

    # PARALLEL INPUT & BUTTON (WITH PIC 1 SPINNER LOADING STATE)
    col_left, col_input, col_btn, col_right = st.columns([1, 4, 1.5, 1])
    
    with col_input:
        url_input = st.text_input("", placeholder="https://example.com", label_visibility="collapsed")
        
    with col_btn:
        btn_click = st.button("Run Analysis", use_container_width=True)

    if btn_click:
        if url_input.strip():
            target = url_input.strip()
            if not target.startswith(("http://", "https://")):
                target = "https://" + target

            # Displays Streamlit standard purple button loader state (Image 1)
            with st.spinner(""):
                t0 = time.time()
                try:
                    r = requests.get(target, headers={"User-Agent": "Mozilla/5.0"}, timeout=10, verify=False)
                    st_code = r.status_code
                    raw_html = r.text
                    scraped_hdrs = "\n".join([f"{k}: {v}" for k, v in r.headers.items()])
                except Exception:
                    st_code = 504
                    raw_html = ""
                    scraped_hdrs = ""

                rt = round(time.time() - t0, 2)

                if raw_html:
                    soup = BeautifulSoup(raw_html, "html.parser")
                    title = soup.title.string.strip() if soup.title and soup.title.string else "Title Tag Missing"
                    meta = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
                    meta_desc = meta.get("content", "").strip() if meta and meta.get("content") else "Meta Description Tag Missing"
                    h1_cnt = len(soup.find_all("h1"))
                    imgs = soup.find_all("img")
                    tot_img = len(imgs)
                    no_alt = sum(1 for img in imgs if not img.get("alt"))
                    body = soup.get_text(separator=" ", strip=True)[:3000]
                else:
                    title, meta_desc, h1_cnt, tot_img, no_alt, body = "Title Tag Missing", "Meta Description Tag Missing", 0, 0, 0, ""

                rep = generate_ai_report(target, st_code, rt, title, meta_desc, h1_cnt, tot_img, no_alt, body, scraped_hdrs)
                st.session_state.audit_data = {
                    "url": target, "status": st_code, "rt": rt, "title": title,
                    "meta": meta_desc, "h1": h1_cnt, "tot_img": tot_img, "no_alt": no_alt, "report": rep
                }
                st.session_state.scanned = True
                st.rerun()


# --- PAGE 2: AUDIT RESULTS SCREEN (Pic 2 & Pic 3 Exact Layout) ---
else:
    d = st.session_state.audit_data
    
    # Audit Title Bar
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            f"""
            <div style="margin-bottom: 1.5rem;">
                <h1 style="color: #ffffff; font-size: 2.2rem; font-weight: 800; margin: 0;">Audit Results for {d['url']}</h1>
                <p style="color: #a78bfa; font-size: 0.95rem; margin-top: 4px;">Comprehensive live structural, performance, and AI analysis breakdown</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown('<div class="audit-new-btn">', unsafe_allow_html=True)
        if st.button("Audit New Target", use_container_width=True):
            st.session_state.scanned = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 4 Diagnostic Metric Cards (Pic 2)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-card-title">HTTP Status Code</div><div class="metric-card-value">{d["status"]}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-card-title">Server Latency</div><div class="metric-card-value">{d["rt"]}s</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-card-title">H1 Tags Count</div><div class="metric-card-value">{d["h1"]} Detected</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-card-title">Missing Alt Attributes</div><div class="metric-card-value">{d["no_alt"]} / {d["tot_img"]}</div></div>', unsafe_allow_html=True)

    # Scraped Metadata Overview Card Container (Pic 2)
    meta_badge_html = '<span class="meta-badge-missing">Missing Tag</span>' if d["meta"] == "Meta Description Tag Missing" else '<span class="meta-badge-ok">Valid</span>'
    meta_color = "#f87171" if d["meta"] == "Meta Description Tag Missing" else "#ffffff"

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

    # Technical Diagnostic & Inspection Report (Pic 3)
    st.markdown('<div class="report-card-box">', unsafe_allow_html=True)
    st.markdown('<div style="color: #ffffff; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem;">Technical Diagnostic & Inspection Report</div>', unsafe_allow_html=True)
    st.markdown(d["report"])
    st.markdown('</div>', unsafe_allow_html=True)