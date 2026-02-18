"""
Script para ingestar documentos PDF en ChromaDB.
Procesa los PDFs de la carpeta docs/ y los indexa en el vector store.
"""
import sys
from pathlib import Path
import logging

# Añadir backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from rag.document_processor import DocumentProcessor
from rag.vector_store import get_vector_store
from db import SessionLocal
from db.models import Document, DocumentType
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def map_filename_to_document_type(filename: str) -> DocumentType:
    """Mapea el nombre del archivo al tipo de documento."""
    filename_lower = filename.lower()
    
    if "a1" in filename_lower and "a3" in filename_lower:
        return DocumentType.PDF_AESA_A1
    elif "a2" in filename_lower:
        return DocumentType.PDF_AESA_A2
    elif "a3" in filename_lower:
        return DocumentType.PDF_AESA_A3
    else:
        return DocumentType.OTHER


def ingest_documents():
    """Procesa e ingesta todos los PDFs de la carpeta docs/."""
    
    # Rutas
    docs_dir = backend_dir.parent / "docs"
    
    if not docs_dir.exists():
        logger.error(f"❌ No existe la carpeta docs/ en {docs_dir}")
        return
    
    # Obtener PDFs
    pdf_files = list(docs_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"⚠️ No se encontraron PDFs en {docs_dir}")
        return
    
    logger.info(f"📂 Encontrados {len(pdf_files)} PDFs en {docs_dir}")
    
    # Inicializar componentes
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
    vector_store = get_vector_store()
    db = SessionLocal()
    
    try:
        total_chunks = 0
        
        for pdf_path in pdf_files:
            logger.info(f"\n{'='*60}")
            logger.info(f"📄 Procesando: {pdf_path.name}")
            logger.info(f"{'='*60}")
            
            # Determinar tipo de documento
            doc_type = map_filename_to_document_type(pdf_path.name)
            logger.info(f"📌 Tipo de documento: {doc_type.value}")
            
            # Verificar si ya existe en la BD
            existing_doc = db.query(Document).filter(
                Document.filename == pdf_path.name
            ).first()
            
            if existing_doc and existing_doc.processed:
                logger.info(f"⏭️ Ya procesado previamente. Saltando...")
                continue
            
            # Procesar PDF
            chunks, metadatas = processor.process_pdf(pdf_path, doc_type.value)
            
            if not chunks:
                logger.warning(f"⚠️ No se pudieron extraer chunks de {pdf_path.name}")
                continue
            
            # Generar IDs únicos para cada chunk
            chunk_ids = [
                f"{pdf_path.stem}_{i}"
                for i in range(len(chunks))
            ]
            
            # Añadir a ChromaDB
            logger.info(f"💾 Guardando {len(chunks)} chunks en ChromaDB...")
            vector_store.add_documents(
                documents=chunks,
                metadatas=metadatas,
                ids=chunk_ids
            )
            
            # Obtener info del PDF
            pdf_info = processor.get_pdf_info(pdf_path)
            
            # Registrar en la base de datos
            if existing_doc:
                # Actualizar documento existente
                existing_doc.processed = True
                existing_doc.vector_count = len(chunks)
                existing_doc.file_size = pdf_info.get('file_size', 0)
                existing_doc.page_count = pdf_info.get('page_count', 0)
                existing_doc.processed_at = datetime.utcnow()
                logger.info(f"🔄 Documento actualizado en BD")
            else:
                # Crear nuevo documento
                new_doc = Document(
                    filename=pdf_path.name,
                    file_path=str(pdf_path),
                    document_type=doc_type,
                    processed=True,
                    vector_count=len(chunks),
                    file_size=pdf_info.get('file_size', 0),
                    page_count=pdf_info.get('page_count', 0),
                    processed_at=datetime.utcnow()
                )
                db.add(new_doc)
                logger.info(f"➕ Documento registrado en BD")
            
            db.commit()
            
            total_chunks += len(chunks)
            logger.info(f"✅ {pdf_path.name} procesado correctamente")
        
        # Estadísticas finales
        logger.info(f"\n{'='*60}")
        logger.info(f"🎉 PROCESO COMPLETADO")
        logger.info(f"{'='*60}")
        logger.info(f"📊 Estadísticas:")
        logger.info(f"   - PDFs procesados: {len(pdf_files)}")
        logger.info(f"   - Chunks totales: {total_chunks}")
        logger.info(f"   - Documentos en ChromaDB: {vector_store.count()}")
        
        # Verificar en la BD
        doc_count = db.query(Document).filter(Document.processed == True).count()
        logger.info(f"   - Documentos en BD: {doc_count}")
        
    except Exception as e:
        logger.error(f"❌ Error durante la ingesta: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("🚀 Iniciando ingesta de documentos...")
    ingest_documents()