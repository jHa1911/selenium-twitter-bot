#!/usr/bin/env python3
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from web.app import app

if __name__ == '__main__':
    print("Starting Twitter Bot Web UI...")
    print("Access the control panel at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
