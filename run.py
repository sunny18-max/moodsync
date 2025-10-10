#!/usr/bin/env python3
"""
Main entry point for Mood-Based Music Recommender
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

if __name__ == '__main__':
    print("🎵 Starting Mood-Based Music Recommender...")
    print("=" * 50)
    print("Server running on http://localhost:5000")
    print("=" * 50)
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, port=5000, host='0.0.0.0')