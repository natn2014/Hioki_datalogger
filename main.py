# coding: UTF-8

import sys
import os
from PySide2.QtWidgets import QApplication

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_controller import HiokiResistanceApp


def main():
    """Main entry point for the HIOKI Resistance Meter application."""
    app = QApplication(sys.argv)
    
    # Create and show main window
    window = HiokiResistanceApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
