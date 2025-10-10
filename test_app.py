#!/usr/bin/env python3
"""
Test the complete application
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_app_imports():
    """Test if all app components can be imported"""
    print("Testing application imports...")
    
    modules_to_test = [
        'app.main',
        'app.emotion.facial_analyzer',
        'app.emotion.text_analyzer', 
        'app.spotify.client',
        'config.settings'
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
    
    print("\nApplication import test completed!")

if __name__ == '__main__':
    test_app_imports()