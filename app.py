import os
import time
import requests
import urllib3
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import streamlit as st

# Disable SSL warnings for external domain scraping
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

# --- CUSTOM CSS FOR REFLEX-LIKE DARK THEME & METRICS ---
st.markdown(
    """
    <style>
    /* Global Page Styling */
    .stApp {
        background: radial-gradient(circle at top center, #1b0933 0%, #0a0612 80%);
        color: #e2e8f0;
    }
    
    /* Header Container */
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.85rem 1.5rem;
        background: rgba(11, 7, 20, 0.75);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .logo-box {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);
        border-radius: 8px;
        color: #ffffff;
        font-weight: 900;
        font-size: 1.2rem;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.4);
    }
    
    /* Metric Cards Styling */
    .metric-card {
        background: rgba(20, 12, 36, 0.8);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 8px;
        padding: 1.2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #a78bfa;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .metric-value {
        font-size: 1.45rem;
        color: #ffffff;
        font-weight: 700;
    }
    
    /* Report Container */
    .report-card {
        background: rgba(20, 12, 36, 0.75);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    /* Input Styling */
    .stTextInput > div > div > input {
        background-color: rgba(15, 10, 26, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid rgba(168, 85, 247, 0.35) !important;
        border-radius: 8px !important;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 0 14px rgba(168, 85, 247, 0.45) !important;
    }
    
    /* Markdown Fixes to prevent enlarged raw HTML text */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #c084fc !important;
        font-size: 1.25rem !important;
        margin-top: 1rem !important;
        font-weight: 700 !important;
    }
    .stMarkdown p, .stMarkdown li {
        color: #cbd5e1 !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    .stMarkdown code {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #e2e8f0 !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session States
if "scanned" not in st.session_state:
    st.session_state.scanned = False
if "audit_data" not in st.session_state:
    st.session_state.audit_data = {}


def generate_ai_report(target_url, status_code, response_time, page_title, meta_desc, h1_count, total_images, missing_alt, content_preview, detected_headers):
    """Generates dynamic Markdown AI Diagnostic report"""
    prompt = f"""
You are an expert Enterprise Web Auditor. Perform an authentic, real-time deep technical audit for the live target URL: {target_url}

=== SCRAPED DOMAIN METRICS & AUDIT DATA ===
- HTTP Response Code: {status_code}
- Server Response Time / Latency: {response_time} seconds
- HTML Page Title: "{page_title}"
- Meta Description: "{meta_desc}"
- Total H1 Heading Elements Found: {h1_count}
- Total Image Elements Found: {total_images} (Images missing 'alt' attribute: {missing_alt})
- Scraped HTTP Response Headers:
{detected_headers}

=== PAGE TEXT BODY PREVIEW ===
{content_preview}

=== INSTRUCTIONS FOR REPORT GENERATION ===
Analyze ONLY the provided target site data and live content preview. DO NOT output raw HTML tags like <h1> or <title> directly in plain markdown bullets as they corrupt Markdown parsing. Use backticks like `h1 tag` or `title tag` instead.

Format the response strictly in Clean Markdown with the following headers:

### Executive Summary
Provide a realistic overall health evaluation score (out of 100) based on actual scraped data, along with a concise technical summary of the site's overall posture.

### 1. Real-Time Flaws & Identified Issues
List EVERY single issue, missing tag, broken pattern, header vulnerability, or performance bottleneck detected on this specific domain.

### 2. Domain & Page Quality Analysis
Detail the technical analysis of latency ({response_time}s), semantic structure (H1 tags: {h1_count}), image optimization ({missing_alt} missing alt tags), SSL configuration, and server setup.

### 3. Actionable Recommendations
Provide specific, technical steps to fix every issue identified above.

### 4. Critical Missing Elements & Security Deficiencies
Highlight missing HTTP security headers (e.g., CSP, HSTS, X-Frame-Options), schema markups, missing metadata, or missing key structural elements.
"""

    # 1. Google Gemini Call
    if GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            if response and response.text:
                return response.text
        except Exception as e:
            pass

    # 2. OpenRouter Fallback
    if OPENROUTER_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "deepseek/deepseek-r1:free",
                "messages": [{"role": "user", "content": prompt}],
            }
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=20,
            )
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception:
            pass

    # 3. Dynamic Rule-Based Fallback
    issues = []
    recommendations = []
    missing_elements = []

    if status_code != 200:
        issues.append(f"HTTP Server response status is non-optimal: {status_code}")
        recommendations.append("Investigate web server routing or CDN settings to return a clean HTTP 200 status.")

    if response_time > 1.5:
        issues.append(f"High initial page latency detected ({response_time}s).")
        recommendations.append("Implement server-side caching or use a modern Content Delivery Network (CDN).")

    if page_title in ["Title Tag Missing", ""]:
        issues.append("HTML Title tag is completely missing from the DOM head node.")
        missing_elements.append("Title tag in HTML head section.")
        recommendations.append("Add a concise, unique page title between 50 and 60 characters.")

    if "Missing" in meta_desc or not meta_desc:
        issues.append("Meta description tag is absent or empty.")
        missing_elements.append("Meta Description tag.")
        recommendations.append("Add a relevant meta description tag (150-160 characters) targeting core keywords.")

    if h1_count == 0:
        issues.append("Zero H1 heading elements detected on the page structure.")
        missing_elements.append("Primary H1 Heading tag.")
        recommendations.append("Add exactly one primary H1 tag containing the target page keyword.")
    elif h1_count > 1:
        issues.append(f"Multiple H1 heading elements detected ({h1_count} found).")
        recommendations.append("Refactor heading hierarchy so only one H1 tag is present on the page.")

    if missing_alt > 0:
        issues.append(f"{missing_alt} out of {total_images} images are missing descriptive 'alt' attributes.")
        missing_elements.append(f"'alt' attributes on {missing_alt} image nodes.")
        recommendations.append("Add meaningful alt text to all image tags for accessibility and SEO.")

    score = max(20, 100 - (len(issues) * 12 + int(response_time * 5)))

    issues_md = "\n".join([f"- {iss}" for iss in issues]) if issues else "- No severe critical issues detected."
    recs_md = "\n".join([f"- {rec}" for rec in recommendations]) if recommendations else "- Maintain current architectural standards."
    missing_md = "\n".join([f"- {mis}" for mis in missing_elements]) if missing_elements else "- All primary standard metadata tags are present."

    return f"""### Executive Summary
**Overall Calculated Health Score: {score}/100**

Live runtime scan performed for **{target_url}**. Server latency recorded at **{response_time}s** with **{len(issues)} primary structural issue(s)** detected.

### 1. Real-Time Flaws & Identified Issues
{issues_md}

### 2. Domain & Page Quality Analysis
- **Server Latency:** Recorded response time of **{response_time}s**.
- **Semantic Structure:** Headings parsed with **{h1_count} H1 tags** found.
- **Media Assets:** Scanned **{total_images} images**, **{missing_alt}** missing ALT attributes.
- **Metadata Indexing:** Title recorded as *"{page_title}"*.

### 3. Actionable Recommendations
{recs_md}

### 4. Critical Missing Elements & Security Deficiencies
{missing_md}
"""


# --- NAVBAR WITH LOGO ---
st.markdown(
    """
    <div class="header-container">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="logo-box">S</div>
            <span style="font-weight: 800; font-size: 1.15rem; color: #ffffff;">SitePulse Enterprise</span>
            <span style="font-weight: 400; font-size: 1.05rem; color: #a78bfa;">| Website Auditor</span>
        </div>
        <div style="background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.4); padding: 0.25rem 0.75rem; border-radius: 6px; font-size: 0.8rem; color: #d8b4fe;">
            System Operational
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --- MAIN UI ---
if not st.session_state.scanned:
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0;">
            <div style="display: inline-block; padding: 0.35rem 1rem; border: 1px solid rgba(192, 132, 252, 0.4); border-radius: 20px; background: rgba(192, 132, 252, 0.08); font-size: 0.75rem; font-weight: 700; color: #c084fc; letter-spacing: 1px;">
                ENTERPRISE DIAGNOSTICS PLATFORM
            </div>
            <h1 style="font-size: 2.8rem; font-weight: 800; color: #ffffff; margin-top: 1rem;">
                Enterprise Website Audit & Diagnostics
            </h1>
            <p style="color: #94a3b8; font-size: 1.1rem; max-width: 650px; margin: 0 auto 2rem auto;">
                Deep-tier structural inspection, technical flaw detection, and live AI quality analysis
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        url_input = st.text_input("", placeholder="https://example.com", label_visibility="collapsed")
        btn = st.button("Run Analysis", use_container_width=True)

        if btn:
            if not url_input.strip():
                st.error("Please enter a valid website URL.")
            else:
                target_url = url_input.strip()
                if not target_url.startswith(("http://", "https://")):
                    target_url = "https://" + target_url

                with st.spinner("Scraping DOM and analyzing site metrics with AI..."):
                    start_time = time.time()
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                    try:
                        resp = requests.get(target_url, headers=headers, timeout=10, verify=False)
                        status_code = resp.status_code
                        resp_text = resp.text
                        scraped_headers = "\n".join([f"{k}: {v}" for k, v in resp.headers.items()])
                    except Exception:
                        status_code = 504
                        resp_text = ""
                        scraped_headers = "No HTTP headers received."

                    response_time = round(time.time() - start_time, 2)

                    if resp_text:
                        soup = BeautifulSoup(resp_text, "html.parser")
                        page_title = soup.title.string.strip() if soup.title and soup.title.string else "Title Tag Missing"
                        meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
                        meta_desc = meta_tag.get("content", "").strip() if meta_tag and meta_tag.get("content") else "Meta Description Tag Missing"
                        h1_count = len(soup.find_all("h1"))
                        imgs = soup.find_all("img")
                        total_images = len(imgs)
                        missing_alt = sum(1 for img in imgs if not img.get("alt"))
                        
                        for element in soup(["script", "style", "nav", "footer", "svg", "noscript", "iframe"]):
                            element.extract()
                        body_text = soup.get_text(separator=" ", strip=True)[:3000]
                    else:
                        page_title = "Title Tag Missing"
                        meta_desc = "Meta Description Tag Missing"
                        h1_count = 0
                        total_images = 0
                        missing_alt = 0
                        body_text = "Connection timeout reached."

                    report = generate_ai_report(
                        target_url, status_code, response_time, page_title, meta_desc, h1_count, total_images, missing_alt, body_text, scraped_headers
                    )

                    st.session_state.audit_data = {
                        "url": target_url,
                        "status_code": status_code,
                        "response_time": response_time,
                        "page_title": page_title,
                        "meta_desc": meta_desc,
                        "h1_count": h1_count,
                        "total_images": total_images,
                        "missing_alt": missing_alt,
                        "report": report,
                    }
                    st.session_state.scanned = True
                    st.rerun()

else:
    # --- RESULTS SCREEN ---
    data = st.session_state.audit_data
    top_col1, top_col2 = st.columns([3, 1])

    with top_col1:
        st.markdown(f"### Audit Results for `{data['url']}`")
        st.caption("Comprehensive live structural, performance, and AI analysis breakdown")

    with top_col2:
        if st.button("Audit New Target", use_container_width=True):
            st.session_state.scanned = False
            st.rerun()

    st.write("")

    # 4 Metric Cards Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">HTTP Status Code</div><div class="metric-value">{data["status_code"]}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Server Latency</div><div class="metric-value">{data["response_time"]}s</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">H1 Tags Count</div><div class="metric-value">{data["h1_count"]} Detected</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Missing Alt Attributes</div><div class="metric-value">{data["missing_alt"]} / {data["total_images"]}</div></div>', unsafe_allow_html=True)

    # Scraped Metadata Overview
    st.markdown(
        f"""
        <div class="report-card">
            <h4 style="color: #ffffff; margin-bottom: 1rem;">Scraped Metadata Overview</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="background: rgba(15, 10, 26, 0.6); padding: 1rem; border-radius: 6px; border: 1px solid rgba(139, 92, 246, 0.2);">
                    <div style="font-size: 0.85rem; color: #c084fc; font-weight: 600;">Page Title</div>
                    <div style="font-weight: 700; color: #ffffff; margin-top: 4px;">{data['page_title']}</div>
                </div>
                <div style="background: rgba(15, 10, 26, 0.6); padding: 1rem; border-radius: 6px; border: 1px solid rgba(139, 92, 246, 0.2);">
                    <div style="font-size: 0.85rem; color: #c084fc; font-weight: 600;">Meta Description</div>
                    <div style="font-weight: 700; color: {'#f87171' if 'Missing' in data['meta_desc'] else '#ffffff'}; margin-top: 4px;">{data['meta_desc']}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # AI Markdown Report Container
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.markdown("### Technical Diagnostic & Inspection Report")
    st.markdown(data["report"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.download_button(
        label="Download Audit Report",
        data=data["report"],
        file_name="website_audit_report.txt",
        mime="text/plain",
    )