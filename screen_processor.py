import base64
import io
from PIL import ImageGrab
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QCursor

class ScreenSelector(QWidget):
    """ Selector de pantalla optimizado para evitar congelamientos. """
    area_selected = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        # Configuración para que sea una capa transparente sobre todo el sistema
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        # Cubrir toda la pantalla (incluyendo configuraciones multi-monitor)
        self.setGeometry(0, 0, 10000, 10000) # Tamaño excesivo para cubrir todo
        self.showFullScreen()
        
        self.start_pos = QPoint()
        self.end_pos = QPoint()
        self.is_selecting = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = self.start_pos
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.is_selecting = False
            rect = QRect(self.start_pos, self.end_pos).normalized()
            
            # Validar que el área sea significativa
            if rect.width() > 5 and rect.height() > 5:
                # IMPORTANTE: Escondemos la ventana ANTES de emitir la señal para evitar capturarnos a nosotros mismos
                self.hide()
                self.area_selected.emit(rect)
                self.close()
            else:
                self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def paintEvent(self, event):
        if not self.is_selecting and self.start_pos.isNull():
            return

        painter = QPainter(self)
        # Fondo oscuro semi-transparente
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        if self.is_selecting:
            rect = QRect(self.start_pos, self.end_pos).normalized()
            # "Recortar" el área seleccionada (hacerla clara)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(rect, Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            
            # Dibujar borde neón estilo OMNI
            painter.setPen(QPen(QColor(0, 255, 65), 2))
            painter.drawRect(rect)

def capture_and_base64(rect: QRect):
    """ Captura el área seleccionada y la convierte a Base64 de forma segura. """
    try:
        # Asegurarnos de capturar las coordenadas correctas de la pantalla
        bbox = (rect.x(), rect.y(), rect.x() + rect.width(), rect.y() + rect.height())
        screenshot = ImageGrab.grab(bbox=bbox, all_screens=True)
        
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG", quality=85)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_base64
    except Exception as e:
        print(f"Capture Error: {e}")
        return None
