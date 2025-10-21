@echo off
REM Check if DEV_MODE is set, default to false if not
if not defined DEV_MODE set DEV_MODE=false

REM Only auto-activate if DEV_MODE=true
if /i "%DEV_MODE%"=="true" (
    echo Auto-activating developer license...
    python scripts\auto_activate_dev_license.py
) else (
    echo Skipping dev license auto-activation (DEV_MODE=%DEV_MODE%)
)

REM Start the GUI
cd gui
bun run start:dev
