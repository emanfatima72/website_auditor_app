import reflex as rx

# App main configuration
config = rx.Config(
    app_name="website_auditor_app",
    api_url="http://192.168.0.109:8000",
    
    # Custom Application Metadata
    # --- Metadata Start ---
    metadata={
        "title": "SitePulse Enterprise",
        "author": "InternWeb Python Team",
        "icon": "/logo.png",  # <--- Web favicon
        "apple_touch_icon": "/logo.png",  # <--- iOS app icon
        "manifest": "/manifest.json",  # <--- PWA definition
    },
)