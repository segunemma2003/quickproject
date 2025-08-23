#!/usr/bin/env python3
"""
EVA Launcher Script
Launches the modern EVA interface
"""

import sys
import os
from pathlib import Path

def main():
    """Main launcher function"""
    print("🚗 Starting EVA Vehicle Data Analyzer...")
    print("=" * 50)
    
    # Check if required modules are available
    try:
        import tkinter as tk
        from PIL import Image, ImageTk
        print("✅ Required modules found")
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        print("Please install required packages:")
        print("pip install pillow")
        return
    
    # Try to import the EVA interface
    try:
        from eva_interface import EVAModernApp
        print("✅ EVA interface module loaded")
    except ImportError as e:
        print(f"❌ Error loading EVA interface: {e}")
        print("Make sure eva_interface.py is in the current directory")
        return
    
    # Check for MDF files in the current directory
    mdf_files = list(Path(".").glob("*.mdf")) + list(Path(".").glob("*.mf4")) + list(Path(".").glob("*.dat"))
    if mdf_files:
        print(f"📁 Found {len(mdf_files)} MDF files in current directory:")
        for f in mdf_files:
            print(f"   - {f.name}")
    else:
        print("📁 No MDF files found in current directory")
        print("   You can import files through the interface")
    
    print("=" * 50)
    print("🎯 Launching EVA Interface...")
    
    # Launch the interface
    try:
        root = tk.Tk()
        app = EVAModernApp(root)
        root.mainloop()
    except Exception as e:
        print(f"❌ Error launching interface: {e}")
        return
    
    print("👋 EVA Interface closed")

if __name__ == "__main__":
    main() 