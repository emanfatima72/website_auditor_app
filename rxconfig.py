import reflex as rx
from reflex_base.plugins.sitemap import SitemapPlugin
from reflex.plugins import RadixThemesPlugin

config = rx.Config(
    app_name="website_auditor_app",
    backend_port=8000,
    frontend_port=3000,
    api_url="http://192.168.0.109:8000",
    disable_plugins=[SitemapPlugin],
    plugins=[RadixThemesPlugin()],
    metadata={
        "title": "SitePulse Enterprise | Website Auditor",
        "description": "Deep-tier structural inspection, technical flaw detection, and AI quality analysis",
        "author": "InternWeb Python Team",
        "icon": "/logo.png",
        "apple_touch_icon": "/logo.png",
        "manifest": "/manifest.json",
    },
)