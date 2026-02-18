"""
Procesador de documentos PDF para RAG.
"""
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from pypdf import PdfReader
import re

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Procesa documentos PDF y los divide en chunks para RAG."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Inicializa el procesador.
        
        Args:
            chunk_size: Tamaño máximo de cada chunk en caracteres
            chunk_overlap: Solapamiento entre chunks consecutivos
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extrae todo el texto de un PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF
        
        Returns:
            Texto completo del PDF
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Página {page_num + 1} ---\n{page_text}"
            
            logger.info(f"📄 Extraído texto de {len(reader.pages)} páginas de {pdf_path.name}")
            
            return text
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo texto de {pdf_path}: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """
        Limpia el texto extraído del PDF.
        
        Args:
            text: Texto a limpiar
        
        Returns:
            Texto limpio
        """
        # Eliminar múltiples espacios en blanco
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar espacios al inicio y final
        text = text.strip()
        
        # Normalizar saltos de línea
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        Divide el texto en chunks con solapamiento.
        
        Args:
            text: Texto a dividir
        
        Returns:
            Lista de chunks de texto
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calcular el final del chunk
            end = start + self.chunk_size
            
            # Si no es el último chunk, intentar cortar en un punto natural (punto, salto de línea)
            if end < text_length:
                # Buscar el último punto o salto de línea en los últimos 100 caracteres
                chunk_end = text[end-100:end].rfind('.')
                if chunk_end != -1:
                    end = end - 100 + chunk_end + 1
                else:
                    chunk_end = text[end-100:end].rfind('\n')
                    if chunk_end != -1:
                        end = end - 100 + chunk_end + 1
            
            # Extraer el chunk
            chunk = text[start:end]
            chunks.append(chunk.strip())
            
            # Avanzar con solapamiento
            start = end - self.chunk_overlap
        
        logger.info(f"✂️ Texto dividido en {len(chunks)} chunks")
        
        return chunks
    
    def process_pdf(
        self,
        pdf_path: Path,
        document_type: str
    ) -> Tuple[List[str], List[Dict]]:
        """
        Procesa un PDF completo y retorna chunks con metadata.
        
        Args:
            pdf_path: Ruta al PDF
            document_type: Tipo de documento (pdf_aesa_a1, pdf_aesa_a2, etc.)
        
        Returns:
            Tupla de (chunks, metadatas)
        """
        # Extraer texto
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        if not raw_text:
            return [], []
        
        # Limpiar texto
        clean_text = self.clean_text(raw_text)
        
        # Dividir en chunks
        chunks = self.split_into_chunks(clean_text)
        
        # Crear metadata para cada chunk
        metadatas = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "source": pdf_path.name,
                "document_type": document_type,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            metadatas.append(metadata)
        
        logger.info(f"✅ Procesado {pdf_path.name}: {len(chunks)} chunks generados")
        
        return chunks, metadatas
    
    def get_pdf_info(self, pdf_path: Path) -> Dict:
        """
        Obtiene información básica de un PDF.
        
        Args:
            pdf_path: Ruta al PDF
        
        Returns:
            Diccionario con información del PDF
        """
        try:
            reader = PdfReader(pdf_path)
            
            return {
                "filename": pdf_path.name,
                "page_count": len(reader.pages),
                "file_size": pdf_path.stat().st_size,
                "metadata": reader.metadata if hasattr(reader, 'metadata') else {}
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo info de {pdf_path}: {e}")
            return {
                "filename": pdf_path.name,
                "error": str(e)
            }