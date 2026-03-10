import easyocr
import numpy as np
from PIL import ImageGrab, Image
from PyQt6.QtWidgets import QWidget, QRubberBand
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal, QPoint

# Inicializar lector (se descarga la primera vez)
reader = None

class ScreenSelector(QWidget):
    """ Capa semi-transparente para seleccionar área de pantalla. """
    area_selected = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setWindowOpacity(0.3)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.showFullScreen()
        self.rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self.origin = QPoint()

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubber_band.setGeometry(QRect(self.origin, QSize()))
        self.rubber_band.show()

    def mouseMoveEvent(self, event):
        self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        self.rubber_band.hide()
        self.area_selected.emit(self.rubber_band.geometry())
        self.close()

def extract_text_from_area(rect: QRect):
    """ Captura el área y usa EasyOCR. """
    global reader
    try:
        if reader is None:
            # Inicialización perezosa para no ralentizar el inicio de la app
            reader = easyocr.Reader(['es', 'en'], gpu=False)

        bbox = (rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height())
        screenshot = ImageGrab.grab(bbox=bbox)
        
        # Convertir imagen PIL a formato compatible con EasyOCR (numpy array)
        img_np = np.array(screenshot)
        
        results = reader.readtext(img_np)
        # Unir todos los fragmentos de texto detectados
        text = " ".join([res[1] for res in results])
        
        return text.strip()
    except Exception as e:
        return f"Error en OCR (EasyOCR): {str(e)}"
