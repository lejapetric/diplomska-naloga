#!/usr/bin/env python3
"""
Meeting Assistant - Startup Script
Run this file to start the application.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8501))  # <-- SPREMENJENO NA 8501
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     🚀 Meeting Assistant v2.0.0                         ║
    ║     📅 AI-powered meeting management                    ║
    ║                                                          ║
    ║     🌐 Running on: http://localhost:{port}              ║
    ║     🔧 Debug mode: {debug}                              ║
    ║                                                          ║
    ║     Press Ctrl+C to stop                                ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    app.run(debug=debug, host='0.0.0.0', port=port)