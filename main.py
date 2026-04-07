#!/usr/bin/env python3
"""
Cricket Live Scoring Application
Main entry point for the cricket scoring application
"""

import sys
import os

# Add the internal directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'internal'))

from gui import SetupWindow
import tkinter as tk

def main():
    """Main entry point for the cricket scoring application"""
    root = tk.Tk()
    
    # Set app icon using logo.png
    try:
        icon_path = os.path.join(os.path.dirname(__file__), 'internal', 'logo.png')
        if os.path.exists(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon)
    except Exception as e:
        print(f"Could not load icon: {e}")
    
    setup = SetupWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
