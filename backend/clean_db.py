import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from db import SessionLocal
from db.models import Document

db = SessionLocal()

try:
    # Eliminar todos los documentos
    deleted = db.query(Document).delete()
    db.commit()
    print(f"✅ Eliminados {deleted} documentos de la BD")
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()