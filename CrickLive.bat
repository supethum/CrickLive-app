@echo off
title CrickLive Launcher
echo Starting CrickLive - Cricket Live Scoring Application...
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo Error: Could not start CrickLive. Make sure Python is installed.
    pause
)
