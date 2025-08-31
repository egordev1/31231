from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QColor, QTextCharFormat, QFont
from datetime import datetime

class Console(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(200)
        self.setFont(QFont("Consolas", 10))
        self.append_info("Console initialized")
        
    def append_info(self, message):
        self.append_formatted(f"[INFO] {message}", QColor(200, 200, 200))
        
    def append_warning(self, message):
        self.append_formatted(f"[WARN] {message}", QColor(255, 165, 0))
        
    def append_error(self, message):
        self.append_formatted(f"[ERROR] {message}", QColor(255, 0, 0))
        
    def append_success(self, message):
        self.append_formatted(f"[SUCCESS] {message}", QColor(0, 255, 0))
        
    def append_formatted(self, message, color):
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_message = f"{timestamp} {message}"
        
        format = QTextCharFormat()
        format.setForeground(color)
        
        self.setCurrentCharFormat(format)
        self.append(full_message)
        
        # Автопрокрутка вниз
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def clear_console(self):
        self.clear()
        self.append_info("Console cleared")