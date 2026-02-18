"""
Modelo de Documento (PDFs de AESA, manuales, etc.).
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import enum

from db.base import Base


class DocumentType(str, enum.Enum):
    """Tipos de documentos."""
    PDF_AESA_A1 = "pdf_aesa_a1"
    PDF_AESA_A2 = "pdf_aesa_a2"
    PDF_AESA_A3 = "pdf_aesa_a3"
    MANUAL = "manual"
    FAQ = "faq"
    OTHER = "other"


class Document(Base):
    """Modelo de documento procesado."""
    
    __tablename__ = "documents"
    
    # Campos principales
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False, index=True)
    
    # Estado de procesamiento
    processed = Column(Boolean, default=False, nullable=False, index=True)
    vector_count = Column(Integer, default=0, nullable=False)  # Número de chunks/vectores generados
    
    # Metadata del procesamiento
    file_size = Column(Integer, nullable=True)  # Tamaño en bytes
    page_count = Column(Integer, nullable=True)  # Número de páginas
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename={self.filename}, processed={self.processed})>"
    
    @property
    def is_ready(self) -> bool:
        """Verifica si el documento está listo para consultas."""
        return self.processed and self.vector_count > 0