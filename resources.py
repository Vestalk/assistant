import os
import sys


def get_resource_path(relative_path: str) -> str:
    """Повертає шлях до ресурсу для звичайного запуску та PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)

    return os.path.join(os.path.abspath("."), relative_path)
