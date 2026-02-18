"""
Script para inicializar la base de datos.
Crea las tablas y la primera migración.
"""
import sys
import os
from pathlib import Path

# ───────────────────────────────
# Añadir la raíz del proyecto al PATH
# ───────────────────────────────
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ───────────────────────────────
# Cargar variables de entorno desde .env si existe
# ───────────────────────────────
from dotenv import load_dotenv

env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Archivo .env cargado desde {env_path}")
else:
    print(f"⚠️  No se encontró .env en {env_path}")
    print("    Asegúrate de tener configurado DATABASE_URL como variable de entorno")

# ───────────────────────────────
# Verificar DATABASE_URL
# ───────────────────────────────
if not os.getenv("DATABASE_URL"):
    print("❌ ERROR: DATABASE_URL no está configurado")
    print("\nConfigúralo en .env:")
    print("DATABASE_URL=postgresql://postgres:tu-password@localhost:5432/aesa_agent")
    sys.exit(1)

# ───────────────────────────────
# Imports de base y modelos
# ───────────────────────────────
from db.base import Base, engine
from db.models.user import User
from db.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory
from db.models.message import Message, MessageRole
from db.models.document import Document, DocumentType

# ───────────────────────────────
# Función para inicializar la DB
# ───────────────────────────────
def init_db():
    """Crea todas las tablas en la base de datos."""
    print("\n🗄️  Inicializando base de datos...")
    print(f"📍 Database URL: {os.getenv('DATABASE_URL')}")
    
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("\n✅ Tablas creadas exitosamente:")
        
        for table_name in Base.metadata.tables.keys():
            print(f"   ✓ {table_name}")
        
        print("\n🎉 Base de datos inicializada correctamente!")
        print("\n📝 Próximos pasos:")
        print("   1. (Opcional) Crea migraciones con Alembic:")
        print("      alembic revision --autogenerate -m 'Initial migration'")
        print("      alembic upgrade head")
        print("\n   2. Verifica las tablas en PostgreSQL:")
        print("      psql -U postgres -d aesa_agent")
        print("      \\dt")
        
    except Exception as e:
        print(f"\n❌ Error al crear las tablas: {e}")
        print("\nVerifica que:")
        print("  - PostgreSQL esté corriendo")
        print("  - La base de datos 'aesa_agent' existe")
        print("  - Las credenciales en DATABASE_URL son correctas")
        sys.exit(1)


# ───────────────────────────────
# Ejecutar si es el script principal
# ───────────────────────────────
if __name__ == "__main__":
    init_db()
