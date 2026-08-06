import os
import time
import requests
import urllib3
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import reflex as rx

# Disable SSL warnings for external domain scraping
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


class State(rx.State):
    """Application State & Web Scraping Engine"""
    url: str = ""
    active_view: str = "home"  # 'home' or 'results'
    is_scanning: bool = False
    error_msg: str = ""

    # Scraped Audit Attributes
    status_code: int = 200
    response_time: float = 0.0
    page_title: str = ""
    meta_desc: str = ""
    h1_count: int = 0
    total_images: int = 0
    images_missing_alt: int = 0
    text_content_preview: str = ""

    # Dynamic AI Diagnostic Structure
    ai_report: str = ""

    def set_url(self, new_url: str):
        self.url = new_url

    def reset_to_home(self):
        """Switches view back to Home search screen"""
        self.active_view = "home"
        self.error_msg = ""

    def analyze_with_ai(self, target_url: str, content_preview: str, detected_headers: str):
        """Generates dynamic real-time AI diagnostic report based on exact scraped metrics"""
        prompt = f"""
You are an expert Enterprise Web Auditor. Perform an authentic, real-time deep technical audit for the live target URL: {target_url}

=== SCRAPED DOMAIN METRICS & AUDIT DATA ===
- HTTP Response Code: {self.status_code}
- Server Response Time / Latency: {self.response_time} seconds
- HTML Page Title: "{self.page_title}"
- Meta Description: "{self.meta_desc}"
- Total H1 Heading Elements Found: {self.h1_count}
- Total Image Elements Found: {self.total_images} (Images missing 'alt' attribute: {self.images_missing_alt})
- Scraped HTTP Response Headers:
{detected_headers}

=== PAGE TEXT BODY PREVIEW ===
{content_preview}

=== INSTRUCTIONS FOR REPORT GENERATION ===
Analyze ONLY the provided target site data and live content preview. DO NOT output raw HTML tags like <h1> or <title> directly in plain markdown bullets as they corrupt Markdown parsing. Use backticks like `h1 tag` or `title tag` instead.

List ALL identified technical flaws, structural weaknesses, missing security headers, missing metadata, content issues, or accessibility concerns dynamically.

Format the response strictly in Clean Markdown with the following headers:

### Executive Summary
Provide a realistic overall health evaluation score (out of 100) based on actual scraped data, along with a concise technical summary of the site's overall posture.

### 1. Real-Time Flaws & Identified Issues
List EVERY single issue, missing tag, broken pattern, header vulnerability, or performance bottleneck detected on this specific domain. Use detailed bullet points.

### 2. Domain & Page Quality Analysis
Detail the technical analysis of latency ({self.response_time}s), semantic structure (H1 tags: {self.h1_count}), image optimization ({self.images_missing_alt} missing alt tags), SSL configuration, and server setup.

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
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                if response and response.text:
                    self.ai_report = response.text
                    return
            except Exception as e:
                print(f"Gemini AI Engine Exception: {e}")

        # 2. OpenRouter Fallback
        if OPENROUTER_API_KEY:
            try:
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "deepseek/deepseek-r1:free",
                    "messages": [{"role": "user", "content": prompt}]
                }
                res = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=20
                )
                if res.status_code == 200:
                    data = res.json()
                    self.ai_report = data["choices"][0]["message"]["content"]
                    return
            except Exception as e:
                print(f"OpenRouter Fallback Exception: {e}")

        # 3. Dynamic Rule-Based Fallback (No Raw HTML Angle Brackets to prevent enlarged text)
        issues = []
        recommendations = []
        missing_elements = []

        if self.status_code != 200:
            issues.append(f"HTTP Server response status is non-optimal: {self.status_code}")
            recommendations.append("Investigate web server routing or CDN settings to return a clean HTTP 200 status.")

        if self.response_time > 1.5:
            issues.append(f"High initial page latency detected ({self.response_time}s).")
            recommendations.append("Implement server-side caching or use a modern Content Delivery Network (CDN).")

        if self.page_title in ["Title Tag Missing", ""]:
            issues.append("HTML Title tag is completely missing from the DOM head node.")
            missing_elements.append("Title tag in HTML head section.")
            recommendations.append("Add a concise, unique page title between 50 and 60 characters.")

        if "Missing" in self.meta_desc or not self.meta_desc:
            issues.append("Meta description tag is absent or empty.")
            missing_elements.append("Meta Description tag.")
            recommendations.append("Add a relevant meta description tag (150-160 characters) targeting core keywords.")

        if self.h1_count == 0:
            issues.append("Zero H1 heading elements detected on the page structure.")
            missing_elements.append("Primary H1 Heading tag.")
            recommendations.append("Add exactly one primary H1 tag containing the target page keyword.")
        elif self.h1_count > 1:
            issues.append(f"Multiple H1 heading elements detected ({self.h1_count} found). This dilutes semantic heading hierarchy.")
            recommendations.append("Refactor heading hierarchy so only one H1 tag is present on the page.")

        if self.images_missing_alt > 0:
            issues.append(f"{self.images_missing_alt} out of {self.total_images} images are missing descriptive 'alt' attributes.")
            missing_elements.append(f"'alt' attributes on {self.images_missing_alt} image nodes.")
            recommendations.append("Add meaningful alt text to all image tags for accessibility and search engine compliance.")

        score = max(20, 100 - (len(issues) * 12 + int(self.response_time * 5)))

        issues_md = "\n".join([f"- {iss}" for iss in issues]) if issues else "- No severe critical issues detected in base HTML DOM scan."
        recs_md = "\n".join([f"- {rec}" for rec in recommendations]) if recommendations else "- Maintain current architectural and structural standards."
        missing_md = "\n".join([f"- {mis}" for mis in missing_elements]) if missing_elements else "- All primary standard metadata tags are present."

        self.ai_report = f"""### Executive Summary
**Overall Calculated Health Score: {score}/100**

Live runtime scan performed for **{target_url}**. The analysis indicates a server response latency of **{self.response_time}s** with **{len(issues)} primary structural issue(s)** detected during real-time DOM parsing.

### 1. Real-Time Flaws & Identified Issues
{issues_md}

### 2. Domain & Page Quality Analysis
- **Server Latency:** Recorded response time of **{self.response_time}s** via direct HTTP request.
- **Semantic Structure:** Headings parsed with **{self.h1_count} H1 tags** found in the body container.
- **Media Assets:** Scanned **{self.total_images} image elements**, where **{self.images_missing_alt}** lack descriptive ALT text tags.
- **Metadata Indexing:** Title recorded as *"{self.page_title}"*.

### 3. Actionable Recommendations
{recs_md}

### 4. Critical Missing Elements & Security Deficiencies
{missing_md}
"""

    def run_audit(self):
        """Scrapes URL dynamically, parses full real-time metrics, and generates live report"""
        if not self.url.strip():
            self.error_msg = "Please enter a valid website URL."
            return

        self.is_scanning = True
        self.error_msg = ""
        yield

        target_url = self.url.strip()
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        start_time = time.time()
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        resp_text = ""
        fetch_success = False
        scraped_headers = ""

        try:
            resp = requests.get(target_url, headers=headers, timeout=10, verify=False)
            self.status_code = resp.status_code
            resp_text = resp.text
            scraped_headers = "\n".join([f"{k}: {v}" for k, v in resp.headers.items()])
            fetch_success = True
        except Exception:
            try:
                alt_url = (
                    target_url.replace("http://", "https://")
                    if target_url.startswith("http://")
                    else target_url.replace("https://", "http://")
                )
                resp = requests.get(alt_url, headers=headers, timeout=10, verify=False)
                self.status_code = resp.status_code
                resp_text = resp.text
                scraped_headers = "\n".join([f"{k}: {v}" for k, v in resp.headers.items()])
                fetch_success = True
            except Exception:
                fetch_success = False

        self.response_time = round(time.time() - start_time, 2)

        if fetch_success and resp_text:
            soup = BeautifulSoup(resp_text, "html.parser")

            # Extract Page Title
            self.page_title = (
                soup.title.string.strip()
                if soup.title and soup.title.string
                else "Title Tag Missing"
            )

            # Extract Meta Description
            meta_tag = soup.find(
                "meta", attrs={"name": "description"}
            ) or soup.find("meta", attrs={"property": "og:description"})

            self.meta_desc = (
                meta_tag.get("content", "").strip()
                if meta_tag and meta_tag.get("content")
                else "Meta Description Tag Missing"
            )

            # Count H1 Tags
            h1_tags = soup.find_all("h1")
            self.h1_count = len(h1_tags)

            # Count Images & missing ALTs
            imgs = soup.find_all("img")
            self.total_images = len(imgs)
            self.images_missing_alt = sum(1 for img in imgs if not img.get("alt"))

            # Remove unneeded scripts/styles before feeding body text to AI
            for element in soup(["script", "style", "nav", "footer", "svg", "noscript", "iframe"]):
                element.extract()

            body_text = soup.get_text(separator=" ", strip=True)[:3000]
            self.text_content_preview = body_text
        else:
            self.status_code = 504
            self.page_title = "Title Tag Missing"
            self.meta_desc = "Meta Description Tag Missing"
            self.h1_count = 0
            self.total_images = 0
            self.images_missing_alt = 0
            body_text = "Connection timeout reached while reaching domain."
            scraped_headers = "No HTTP headers received."

        # Pass live parameters to dynamic AI generator
        self.analyze_with_ai(target_url, body_text, scraped_headers)
        self.is_scanning = False
        self.active_view = "results"
        yield


# --- UI Components & Navigation ---

def navbar() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.center(
                rx.text(
                    "S", 
                    font_weight="900", 
                    font_size="1.1rem", 
                    color="#ffffff",
                    line_height="1",
                ),
                width="34px",
                height="34px",
                background="linear-gradient(135deg, #a855f7 0%, #7c3aed 100%)",
                border_radius="8px",
                box_shadow="0 0 10px rgba(168, 85, 247, 0.4)",
            ),
            rx.text(
                "SitePulse Enterprise",
                font_weight="800",
                font_size="1.15rem",
                color="#ffffff",
            ),
            rx.text(
                "| Website Auditor",
                font_weight="400",
                font_size="1.05rem",
                color="#a78bfa",
            ),
            align="center",
            spacing="2",
        ),
        rx.hstack(
            rx.cond(
                State.active_view == "results",
                rx.button(
                    "Download Audit Report",
                    on_click=rx.download(
                        data=State.ai_report,
                        filename="website_audit_report.txt",
                    ),
                    variant="solid",
                    color_scheme="purple",
                    size="2",
                    cursor="pointer",
                    background="linear-gradient(135deg, #a855f7 0%, #7c3aed 100%)",
                    color="#ffffff",
                    font_weight="600",
                ),
            ),
            rx.box(
                rx.text("System Operational", font_size="0.8rem", color="#d8b4fe"),
                padding="0.25rem 0.75rem",
                border="1px solid rgba(168, 85, 247, 0.4)",
                border_radius="6px",
                background="rgba(168, 85, 247, 0.1)",
            ),
            spacing="3",
            align="center",
        ),
        justify="between",
        align="center",
        width="100%",
        padding="0.85rem 2rem",
        border_bottom="1px solid rgba(255, 255, 255, 0.08)",
        background="rgba(11, 7, 20, 0.75)",
        backdrop_filter="blur(10px)",
        position="sticky",
        top="0",
        z_index="100",
    )


def metric_card(label: str, value: str | rx.Var):
    return rx.box(
        rx.vstack(
            rx.text(label, font_size="0.8rem", color="#a78bfa", font_weight="600"),
            rx.text(value, font_size="1.45rem", color="#ffffff", font_weight="700"),
            align="center",
            justify="center",
            spacing="1",
        ),
        padding="1.2rem",
        background="rgba(20, 12, 36, 0.8)",
        border="1px solid rgba(139, 92, 246, 0.25)",
        border_radius="8px",
        width="100%",
        text_align="center",
    )


# --- View 1: Home Screen ---

def home_view() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.box(
                rx.text(
                    "ENTERPRISE DIAGNOSTICS PLATFORM",
                    font_size="0.72rem",
                    font_weight="700",
                    letter_spacing="1.2px",
                    color="#c084fc",
                ),
                padding="0.35rem 1rem",
                border="1px solid rgba(192, 132, 252, 0.4)",
                border_radius="20px",
                background="rgba(192, 132, 252, 0.08)",
                margin_bottom="1rem",
            ),
            rx.heading(
                "Enterprise Website Audit & Diagnostics",
                font_size=["2.2rem", "3.6rem"],
                font_weight="800",
                color="#ffffff",
                text_align="center",
                line_height="1.15",
                max_width="850px",
            ),
            rx.text(
                "Deep-tier structural inspection, technical flaw detection, and live AI quality analysis",
                font_size=["1rem", "1.2rem"],
                color="#94a3b8",
                text_align="center",
                max_width="650px",
                margin_bottom="1.5rem",
            ),
            rx.hstack(
                rx.input(
                    placeholder="https://amazon.com",
                    value=State.url,
                    on_change=State.set_url,
                    size="3",
                    width=["100%", "480px"],
                    background="rgba(15, 10, 26, 0.8)",
                    border="1px solid rgba(168, 85, 247, 0.35)",
                    color="#ffffff",
                ),
                rx.button(
                    rx.cond(
                        State.is_scanning,
                        rx.spinner(size="2", color="white"),
                        "Run Analysis"
                    ),
                    on_click=State.run_audit,
                    is_disabled=State.is_scanning,
                    size="3",
                    background="linear-gradient(135deg, #a855f7 0%, #7c3aed 100%)",
                    color="#ffffff",
                    font_weight="600",
                    cursor="pointer",
                    box_shadow="0 0 18px rgba(168, 85, 247, 0.45)",
                    padding="0 1.5rem",
                ),
                width="100%",
                justify="center",
                wrap="wrap",
                spacing="3",
            ),
            rx.cond(
                State.error_msg != "",
                rx.callout(
                    State.error_msg,
                    icon="circle_alert",
                    color_scheme="red",
                    width="100%",
                    margin_top="1.5rem",
                )
            ),
            align="center",
            spacing="4",
            max_width="1000px",
            width="100%",
            padding="4rem 1rem",
        ),
        width="100%",
    )


# --- View 2: Results Screen ---

def results_view() -> rx.Component:
    is_missing = State.meta_desc.to_string().contains("Missing")

    return rx.vstack(
        # Page Title Row
        rx.hstack(
            rx.vstack(
                rx.heading(
                    f"Audit Results for {State.url}",
                    font_size="2.2rem",
                    font_weight="800",
                    color="#ffffff",
                ),
                rx.text(
                    "Comprehensive live structural, performance, and AI analysis breakdown",
                    color="#a78bfa",
                    font_size="1rem",
                ),
                align_items="start",
                spacing="1",
            ),
            rx.button(
                "Audit New Target",
                on_click=State.reset_to_home,
                variant="outline",
                color_scheme="purple",
                size="3",
                cursor="pointer",
                border="1px solid rgba(168, 85, 247, 0.6)",
                color="#ffffff",
            ),
            justify="between",
            align="center",
            width="100%",
            margin_bottom="1rem",
        ),

        # 4 Metric Cards Row
        rx.grid(
            metric_card("HTTP Status Code", State.status_code),
            metric_card("Server Latency", f"{State.response_time}s"),
            metric_card("H1 Tags Count", f"{State.h1_count} Detected"),
            metric_card("Missing Alt Attributes", f"{State.images_missing_alt} / {State.total_images}"),
            columns=rx.breakpoints(initial="1", sm="2", md="4"),
            spacing="4",
            width="100%",
            margin_bottom="1.5rem",
        ),

        # Scraped Metadata Overview
        rx.box(
            rx.vstack(
                rx.heading(
                    "Scraped Metadata Overview",
                    font_size="1.25rem",
                    color="#ffffff",
                    font_weight="700",
                    margin_bottom="0.5rem",
                ),
                rx.grid(
                    # Title Box
                    rx.box(
                        rx.vstack(
                            rx.text("Page Title", font_size="0.85rem", color="#c084fc", font_weight="600"),
                            rx.text(State.page_title, font_weight="700", color="#ffffff", font_size="1.05rem"),
                            align_items="start",
                            spacing="1",
                        ),
                        padding="1rem",
                        background="rgba(15, 10, 26, 0.6)",
                        border="1px solid rgba(139, 92, 246, 0.2)",
                        border_radius="6px",
                    ),
                    # Meta Description Box
                    rx.box(
                        rx.hstack(
                            rx.vstack(
                                rx.text("Meta Description", font_size="0.85rem", color="#c084fc", font_weight="600"),
                                rx.text(
                                    State.meta_desc,
                                    font_weight="700",
                                    color=rx.cond(is_missing, "#f87171", "#ffffff"),
                                    font_size="1.05rem"
                                ),
                                align_items="start",
                                spacing="1",
                            ),
                            rx.cond(
                                is_missing,
                                rx.badge("Missing Tag", color_scheme="red", variant="solid", font_size="0.75rem")
                            ),
                            justify="between",
                            align="start",
                            width="100%",
                        ),
                        padding="1rem",
                        background="rgba(15, 10, 26, 0.6)",
                        border="1px solid rgba(139, 92, 246, 0.2)",
                        border_radius="6px",
                    ),
                    columns=rx.breakpoints(initial="1", md="2"),
                    spacing="4",
                    width="100%",
                ),
                align_items="start",
                width="100%",
            ),
            padding="1.5rem",
            background="rgba(20, 12, 36, 0.75)",
            border="1px solid rgba(139, 92, 246, 0.3)",
            border_radius="10px",
            width="100%",
            margin_bottom="1.5rem",
        ),

        # Technical Diagnostic Report Section
        rx.box(
            rx.vstack(
                rx.heading(
                    "Technical Diagnostic & Inspection Report",
                    font_size="1.25rem",
                    color="#ffffff",
                    font_weight="700",
                    margin_bottom="0.8rem",
                ),
                rx.markdown(
                    State.ai_report,
                    color="#e2e8f0",
                    style={
                        "h1": {"color": "#c084fc", "font_size": "1.2rem", "margin_top": "1rem", "font_weight": "700"},
                        "h2": {"color": "#c084fc", "font_size": "1.15rem", "margin_top": "1rem", "font_weight": "700"},
                        "h3": {"color": "#c084fc", "font_size": "1.1rem", "margin_top": "1rem", "font_weight": "700"},
                        "strong": {"color": "#c084fc"},
                        "p": {"font_size": "0.95rem", "line_height": "1.6", "color": "#cbd5e1"},
                        "ul": {"padding_left": "1.2rem", "margin_bottom": "1rem"},
                        "li": {"margin_bottom": "0.4rem", "font_size": "0.95rem", "color": "#cbd5e1", "line_height": "1.5"},
                        "code": {"font_size": "0.9rem", "background": "rgba(255, 255, 255, 0.1)", "padding": "2px 6px", "border_radius": "4px"}
                    }
                ),
                align_items="start",
                width="100%",
            ),
            padding="1.5rem",
            background="rgba(20, 12, 36, 0.75)",
            border="1px solid rgba(139, 92, 246, 0.3)",
            border_radius="10px",
            width="100%",
        ),

        spacing="4",
        max_width="1200px",
        width="100%",
        padding="2rem 1.5rem",
    )


# --- Main App Container ---

def index() -> rx.Component:
    return rx.box(
        navbar(),
        rx.center(
            rx.cond(
                State.active_view == "home",
                home_view(),
                results_view(),
            ),
            width="100%",
        ),
        min_height="100vh",
        background="radial-gradient(circle at top center, #1b0933 0%, #0a0612 80%)",
        width="100%",
    )


# --- Reflex Entry Point ---
app = rx.App()
app.add_page(index, title="SitePulse Enterprise | Website Auditor")