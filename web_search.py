from duckduckgo_search import DDGS
from PyQt6.QtCore import QThread, pyqtSignal

class WebSearchWorker(QThread):
    """
    Busca en DuckDuckGo con mayor profundidad y mejores filtros.
    """
    results_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            with DDGS() as ddgs:
                # Aumentamos a 8 resultados para dar más contexto a la IA
                results = list(ddgs.text(self.query, max_results=8, region='wt-wt', safesearch='moderate'))
                
                if not results:
                    self.results_ready.emit("ERROR: No se encontraron fuentes relevantes en la web.")
                    return

                context = "--- CONTEXTO DE FUENTES WEB EXTERNAS ---\n\n"
                for i, r in enumerate(results, 1):
                    title = r.get('title', 'Sin título')
                    body = r.get('body', 'Sin descripción')
                    url = r.get('href', '#')
                    context += f"FUENTE [{i}]: {title}\nSINTESIS: {body}\nREFERENCIA: {url}\n\n"
                
                context += "--- FIN DEL CONTEXTO WEB ---"
                self.results_ready.emit(context)
        except Exception as e:
            self.error_occurred.emit(f"Error en motor de búsqueda: {str(e)}")
