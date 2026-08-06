@echo off
title SitePulse Enterprise Auditor
cd /d "D:\InternWeb\Python\website_auditor_app"
call venv\Scripts\activate
start /min cmd /c "reflex run --backend-host 0.0.0.0"
timeout /t 6
start http://localhost:3000
exit