# document_processor.py
import os
import openpyxl
from docx import Document
from PyPDF2 import PdfReader
from PyQt6.QtCore import QThread, pyqtSignal

MAX_FILE_SIZE_MB = 10

class DocumentWorker(QThread):
    """
    Motor de Procesamiento de Documentos asíncrono.
    Extrae texto de DOCX, PDF y Excel sin bloquear la UI.
    Optimizado sin pandas/numpy para reducir peso.
    """
    extraction_ready = pyqtSignal(str, str) # filename, content
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            if os.path.getsize(self.file_path) > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise ValueError(f"Archivo demasiado grande (máximo {MAX_FILE_SIZE_MB}MB).")

            filename = os.path.basename(self.file_path)
            content = self._extract_text()
            self.extraction_ready.emit(filename, content)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def _extract_text(self):
        ext = os.path.splitext(self.file_path)[1].lower()
        
        if ext == ".docx":
            doc = Document(self.file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        
        elif ext == ".pdf":
            reader = PdfReader(self.file_path)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            return text
        
        elif ext in [".xlsx", ".xls"]:
            # Carga ligera usando openpyxl directamente
            wb = openpyxl.load_workbook(self.file_path, data_only=True)
            text_content = []
            for sheet in wb.worksheets:
                for row in sheet.iter_rows(values_only=True):
                    row_text = "\t".join([str(cell) for cell in row if cell is not None])
                    if row_text:
                        text_content.append(row_text)
            return "\n".join(text_content)
        
        else:
            raise ValueError("Formato no soportado (DOCX, PDF, Excel).")
