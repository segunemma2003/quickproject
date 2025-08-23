#!/usr/bin/env python3
"""
Fixed EVA Interface Launcher
"""

import sys
import os

def main():
    print("🚗 Starting Fixed EVA Interface...")
    print("=" * 50)
    
    try:
        from eva_professional_fixed import EVAInterface
        import tkinter as tk
        
        print("✅ Fixed interface loaded")
        print("🎯 Launching interface...")
        
        root = tk.Tk()
        app = EVAInterface(root)
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Please ensure all required packages are installed")
    except Exception as e:
        print(f"❌ Error launching interface: {e}")

if __name__ == "__main__":
    main() 