import sys
import os
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtCore import QCoreApplication, Qt  # Правильный импорт Qt

# Add project directories to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ui'))

# Set application attributes before creating QApplication
QCoreApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

from ui.main_window import MainWindow

if __name__ == "__main__":
    # Create application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # Set application name and version
    app.setApplicationName("3D Unity Editor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("GameDevStudio")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)