import base64
import io
from PIL import ImageGrab
from PyQt6.QtWidgets import QWidget, QRubberBand
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal, QPoint

class ScreenSelector(QWidget):
    """ Capa para seleccionar área de pantalla. """
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

def capture_and_base64(rect: QRect):
    """ Captura el área y la devuelve en Base64 para Groq Vision. """
    try:
        bbox = (rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height())
        screenshot = ImageGrab.grab(bbox=bbox)
        
        # Optimizar tamaño de imagen para la API
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_base64
    except Exception as e:
        return None
