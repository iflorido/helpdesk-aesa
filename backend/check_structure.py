"""
Script para verificar que toda la estructura de archivos está correcta.
"""
import os
from pathlib import Path

def check_structure():
    """Verifica que todos los archivos necesarios existen."""
    
    backend_dir = Path(__file__).parent
    
    required_files = [
        # Core
        "core/__init__.py",
        "core/config.py",
        "core/security.py",
        
        # DB
        "db/__init__.py",
        "db/base.py",
        
        # DB Models
        "db/models/__init__.py",
        "db/models/user.py",
        "db/models/ticket.py",
        "db/models/message.py",
        "db/models/document.py",
        
        # Main
        "main.py",
        
        # Requirements
        "requirements.txt",
    ]
    
    print("🔍 Verificando estructura de archivos...\n")
    
    missing = []
    found = []
    
    for file_path in required_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            found.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing.append(file_path)
            print(f"❌ {file_path} - FALTA")
    
    print(f"\n📊 Resumen:")
    print(f"   ✅ Encontrados: {len(found)}/{len(required_files)}")
    
    if missing:
        print(f"   ❌ Faltan: {len(missing)}")
        print(f"\n⚠️  Archivos faltantes:")
        for f in missing:
            print(f"      - {f}")
        return False
    else:
        print(f"\n🎉 ¡Todos los archivos necesarios están presentes!")
        return True


if __name__ == "__main__":
    success = check_structure()
    exit(0 if success else 1)