
import sys
from PyQt6.QtWidgets import QApplication
from app.robo_assistant import RoboAssistant


def main():
    app = QApplication(sys.argv)
    assistant = RoboAssistant()
    assistant.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
