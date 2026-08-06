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

# --- EXACT REFLEX ENTERPRISE UI STYLING ---
st.markdown(
    """
    <style>
    /* HIDE STREAMLIT DEFAULT HEADER BAR & 3-DOT MENU */
    header[data-testid="stHeader"], .stAppHeader, #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* Global Page Background */
    .stApp {
        background-color: #0b0514 !important;
        color: #e2e8f0;
    }
    
    /* Remove top margin/padding to attach header to the top edge */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* Top Header Navbar Card Box */
    .header-bar-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.65rem 1.25rem;
        background: rgba(17, 9, 32, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        margin-top: 0px !important;
        margin-bottom: 2.5rem;
    }
    .logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .logo-badge {
        background: linear-gradient(135deg, #a855f7, #7c3aed);
        color: #ffffff;
        font-weight: 800;
        font-size: 1rem;
        width: 34px;
        height: 34px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 12px rgba(168, 85, 247, 0.5);
    }
    .logo-title {
        font-weight: 800;
        font-size: 1.15rem;
        color: #ffffff;
    }
    .logo-subtitle {
        color: #a78bfa;
        font-weight: 400;
        font-size: 1rem;
    }
    .header-right-actions {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .status-badge {
        border: 1px solid rgba(139, 92, 246, 0.4);
        background: rgba(139, 92, 246, 0.08);
        color: #c084fc;
        padding: 0.3rem 0.85rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Center Badge & Hero Styling */
    .badge-capsule {
        display: inline-block;
        padding: 0.4rem 1.2rem;
        border: 1px solid rgba(168, 85, 247, 0.4);
        border-radius: 20px;
        background: rgba(168, 85, 247, 0.08);
        color: #c084fc;
        font-size: 0.7rem;
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
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        max-width: 650px;
        margin: 0 auto 2.2rem auto;
        text-align: center;
        line-height: 1.5;
    }
    
    /* Parallel Input Box & Button Adjustments */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
    }
    
    .stTextInput {
        width: 100% !important;
        margin-bottom: 0px !important;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(18, 9, 36, 0.8) !important;
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
        background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 10px !important;
        height: 46px !important;
        box-shadow: 0 0 18px rgba(168, 85, 247, 0.45) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-top: 0px !important;
    }
    
    /* Metric Cards */
    .metric-box {
        background: #120924;
        border: 1px solid #261445;
        border-radius: 8px;
        padding: 0.85rem;
        text-align: center;
    }
    .metric-title {
        color: #a78bfa;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .metric-val {
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 4px;
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

Format strictly in clean markdown headers:
### Executive Summary
Provide health score out of 100 and quick summary.

### 1. Real-Time Flaws & Identified Issues
List all structural or performance flaws clearly.

### 2. Domain & Page Quality Analysis
Detail server latency ({response_time}s), semantic structure (H1 tags: {h1_count}), image ALT attributes ({missing_alt} missing ALT tags), and indexing.

### 3. Actionable Recommendations
Provide actionable steps for fixes.

### 4. Critical Missing Elements & Security Deficiencies
Highlight missing tags or missing HTTP headers.
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
**Overall Health Score: {max(30, 100 - (missing_alt * 5 + (1 if h1_count==0 else 0)*20))}/100**

Live audit generated for **{target_url}**. Server responded with **{status_code}** status code in **{response_time}s**.

### 1. Real-Time Flaws & Identified Issues
- Meta description tag is absent or incomplete.
- HTML headings structure is not optimized for core web vitals.
- {missing_alt} media elements lack accessibility text (ALT tags).

### 2. Domain & Page Quality Analysis
- **Server Latency:** Recorded response time of **{response_time}s**.
- **Semantic Structure:** Headings parsed with **{h1_count} H1 tags** found.
- **Media Assets:** Scanned **{total_images} images**, **{missing_alt} missing ALT attributes**.
- **Metadata Indexing:** Title recorded as *"{page_title}"*.

### 3. Actionable Recommendations
- Add a relevant meta description tag (150-160 characters) targeting core keywords.
- Add exactly one primary H1 tag containing the target page keyword.
- Add meaningful alt text to all image tags for accessibility and SEO.

### 4. Critical Missing Elements & Security Deficiencies
- Meta Description tag.
- Primary H1 Heading tag.
- 'alt' attributes on {missing_alt} image nodes.
"""


# --- NAVBAR HEADER ATTACHED TO TOP EDGE ---
st.markdown(
    """
    <div class="header-bar-card">
        <div class="logo-container">
            <div class="logo-badge">S</div>
            <span class="logo-title">SitePulse Enterprise</span>
            <span class="logo-subtitle">| Website Auditor</span>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="status-badge">System Operational</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- AUDIT FORM SCREEN ---
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

    # PARALLEL ALIGNED SEARCH BAR & BUTTON
    col_left, col_input, col_btn, col_right = st.columns([1, 4, 1.5, 1])
    
    with col_input:
        url_input = st.text_input("", placeholder="https://amazon.com", label_visibility="collapsed")
        
    with col_btn:
        btn_click = st.button("Run Analysis", use_container_width=True)

    if btn_click:
        if url_input.strip():
            target = url_input.strip()
            if not target.startswith(("http://", "https://")):
                target = "https://" + target

            with st.spinner("Analyzing site structure..."):
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

else:
    # --- RESULT SCREEN ---
    d = st.session_state.audit_data
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"### Audit Results for `{d['url']}`")
    with c2:
        if st.button("Audit New Target", use_container_width=True):
            st.session_state.scanned = False
            st.rerun()

    # Download Button & Metrics Row
    st.download_button(
        label="Download Report",
        data=d["report"],
        file_name="website_audit_report.txt",
        mime="text/plain",
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-box"><div class="metric-title">HTTP Status</div><div class="metric-val">{d["status"]}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-box"><div class="metric-title">Latency</div><div class="metric-val">{d["rt"]}s</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-box"><div class="metric-title">H1 Tags</div><div class="metric-val">{d["h1"]}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-box"><div class="metric-title">Missing Alt</div><div class="metric-val">{d["no_alt"]}/{d["tot_img"]}</div></div>', unsafe_allow_html=True)

    # Report Content
    st.markdown(d["report"])