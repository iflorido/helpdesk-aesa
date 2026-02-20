"""
Vector Store usando ChromaDB para almacenar embeddings de documentos.
"""
import chromadb
from typing import List, Dict, Optional
import logging

from core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """Gestiona el almacenamiento y búsqueda de vectores en ChromaDB."""
    
    def __init__(self):
        """Inicializa la conexión con ChromaDB."""
        try:
            # Usar PersistentClient para persistir en disco
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY
            )
            
            # Crear o obtener colección
            self.collection = self.client.get_or_create_collection(
                name="aesa_documents",
                metadata={"description": "Documentos AESA A1/A2/A3"}
            )
            
            logger.info(f"✅ ChromaDB conectado. Documentos: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"❌ Error conectando a ChromaDB: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict],
        ids: List[str]
    ) -> None:
        """
        Añade documentos a la colección.
        
        Args:
            documents: Lista de textos a indexar
            metadatas: Lista de metadatos asociados
            ids: Lista de IDs únicos para cada documento
        """
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"✅ Añadidos {len(documents)} documentos a ChromaDB")
        except Exception as e:
            logger.error(f"❌ Error añadiendo documentos: {e}")
            raise
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Busca documentos similares a la query.
        
        Args:
            query: Texto de búsqueda
            n_results: Número de resultados a retornar
            where: Filtros opcionales (ej: {"document_type": "pdf_aesa_a2"})
        
        Returns:
            Diccionario con resultados: {
                "documents": [[doc1, doc2, ...]],
                "metadatas": [[meta1, meta2, ...]],
                "distances": [[dist1, dist2, ...]]
            }
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            
            logger.info(f"🔍 Búsqueda realizada. Resultados: {len(results['documents'][0])}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda: {e}")
            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }
    
    def delete_collection(self) -> None:
        """Elimina la colección completa (útil para reset)."""
        try:
            self.client.delete_collection("aesa_documents")
            logger.info("🗑️ Colección eliminada")
        except Exception as e:
            logger.error(f"❌ Error eliminando colección: {e}")
    
    def count(self) -> int:
        """Retorna el número de documentos en la colección."""
        return self.collection.count()
    
    def get_stats(self) -> Dict:
        """Retorna estadísticas de la colección."""
        return {
            "total_documents": self.count(),
            "collection_name": self.collection.name,
            "metadata": self.collection.metadata
        }


# Instancia global del vector store
_vector_store = None

def get_vector_store() -> VectorStore:
    """
    Dependency para obtener el vector store.
    Usa singleton pattern.
    """
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStore()
    
    return _vector_store