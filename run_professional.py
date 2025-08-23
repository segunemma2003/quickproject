#!/usr/bin/env python3
"""
Professional EVA Interface Launcher
"""

import sys
import os

def main():
    print("🚗 Starting Professional EVA Interface...")
    print("=" * 50)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected. Please activate eva_env first:")
        print("   source eva_env/bin/activate")
        return
    
    try:
        from eva_professional import ProfessionalEVAInterface
        import tkinter as tk
        
        print("✅ Professional interface loaded")
        print("🎯 Launching interface...")
        
        root = tk.Tk()
        app = ProfessionalEVAInterface(root)
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Please ensure all required packages are installed")
    except Exception as e:
        print(f"❌ Error launching interface: {e}")

if __name__ == "__main__":
    main() 