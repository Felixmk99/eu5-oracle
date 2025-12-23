import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLineEdit, QTextEdit, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QFont
from pynput import keyboard

# Ensure we can import core_engine from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core_engine import oracle_core

class HotkeyListener(QThread):
    """Listens for global hotkeys in a background thread."""
    hotkey_pressed = pyqtSignal()

    def run(self):
        # Default hotkey: Ctrl + Alt + Space
        with keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+<space>': self.on_activate
        }) as h:
            h.join()

    def on_activate(self):
        self.hotkey_pressed.emit()

class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_engine()

    def init_ui(self):
        # Window Setup
        self.setWindowTitle("EU5 Oracle Overlay")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Position: Top Right (fixed size for now)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 420, 50, 400, 500)

        # Central Widget & Layout
        self.main_widget = QWidget()
        self.main_widget.setObjectName("OverlayContainer")
        self.layout = QVBoxLayout(self.main_widget)
        
        # Style sheet for premium dark glass look
        self.main_widget.setStyleSheet("""
            QWidget#OverlayContainer {
                background-color: rgba(30, 30, 35, 230);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 15px;
            }
            QLabel {
                color: #e0e0e0;
                font-weight: bold;
            }
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #d0d0d0;
                font-size: 14px;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 20);
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 8px;
                color: white;
                padding: 8px;
                font-size: 14px;
            }
        """)

        # Title
        self.title_label = QLabel("🌍 EU5 Oracle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Chat Area
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        self.chat_view.setPlaceholderText("The Oracle is listening...")
        self.layout.addWidget(self.chat_view)

        # Input Field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask a question...")
        self.input_field.returnPressed.connect(self.handle_query)
        self.layout.addWidget(self.input_field)

        self.setCentralWidget(self.main_widget)
        self.hide() # Hidden by default

    def setup_engine(self):
        """Initializes the Oracle engine with default settings (Local/Groq fallback)."""
        self.chat_view.append("<i>Waking up the Oracle...</i>")
        
        # Try to auto-initialize using environment defaults
        # For simplicity in overlay, we assume the user has set up .env or Ollama is running
        provider = "Local (Ollama)"
        model = "llama3.1:8b"
        
        success, msg = oracle_core.initialize_engine(provider, model)
        if not success:
            # Fallback to Groq if env key exists
            if os.getenv("GROQ_API_KEY"):
                self.chat_view.append("<i>Local fail. Trying Cloud Fallback...</i>")
                success, msg = oracle_core.initialize_engine("Groq", "llama3-70b-8192")
        
        if success:
            self.chat_view.append(f"<b>System:</b> {msg}")
        else:
            self.chat_view.append(f"<b>System:</b> Error initializing engine. Check your .env file.")

    def handle_query(self):
        prompt = self.input_field.text()
        if not prompt:
            return
        
        self.chat_view.append(f"\n<b>You:</b> {prompt}")
        self.input_field.clear()
        
        self.chat_view.append("<b>Oracle:</b> <i>Thinking...</i>")
        QApplication.processEvents() # Ensure UI updates
        
        response = oracle_core.query(prompt)
        
        # Remove the 'Thinking...' line
        cursor = self.chat_view.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.select(cursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar() # remove newline
        
        self.chat_view.append(f"<b>Oracle:</b> {response}")
        self.chat_view.ensureCursorVisible()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()
            self.input_field.setFocus()

def main():
    app = QApplication(sys.argv)
    
    window = OverlayWindow()
    
    # Setup Hotkey
    listener = HotkeyListener()
    listener.hotkey_pressed.connect(window.toggle_visibility)
    listener.start()
    
    print("Oracle Overlay is running in the background.")
    print("Press Ctrl + Alt + Space to show/hide.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
