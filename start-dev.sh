#!/bin/bash

echo "🚁 Iniciando Helpdesk AESA A2 en desarrollo local..."
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. Verificar que estamos en el directorio correcto
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Ejecuta este script desde la raíz del proyecto${NC}"
    exit 1
fi

# 2. Verificar que existe .env
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ No existe archivo .env${NC}"
    echo -e "${YELLOW}Copiando .env.example a .env...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  IMPORTANTE: Edita .env y configura:${NC}"
    echo "   - OPENAI_API_KEY (tu API key de OpenAI)"
    echo "   - DATABASE_URL (tu conexión PostgreSQL local)"
    echo "   - SECRET_KEY (se generará automáticamente si no lo cambias)"
    echo ""
    echo -e "${YELLOW}Abre .env y completa la configuración, luego ejecuta este script de nuevo.${NC}"
    exit 1
fi

# 3. Verificar que está configurado OPENAI_API_KEY
if grep -q "sk-your-openai-api-key-here" .env || ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo -e "${RED}❌ OPENAI_API_KEY no está configurado en .env${NC}"
    echo -e "${YELLOW}Por favor edita .env y añade tu API key de OpenAI${NC}"
    exit 1
fi

# 4. Generar SECRET_KEY si no está configurado
if grep -q "your-secret-key-here" .env; then
    echo -e "${YELLOW}🔐 Generando SECRET_KEY...${NC}"
    SECRET_KEY=$(openssl rand -hex 32)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-generate-with-openssl-rand-hex-32/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here-generate-with-openssl-rand-hex-32/$SECRET_KEY/" .env
    fi
    echo -e "${GREEN}✓ SECRET_KEY generado automáticamente${NC}"
fi

# 5. Verificar que existe el entorno conda/venv
if [ ! -d "backend/venv" ] && [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${YELLOW}⚠️  No se detectó entorno virtual${NC}"
    echo "Creando entorno virtual en backend/venv..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✓ Entorno virtual creado e instalado${NC}"
    echo ""
fi

# 6. Verificar/Activar entorno virtual
if [ -d "backend/venv" ] && [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${BLUE}Activando entorno virtual...${NC}"
    source backend/venv/bin/activate
    echo -e "${GREEN}✓ Entorno virtual activado${NC}"
elif [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${GREEN}✓ Usando entorno conda: $CONDA_DEFAULT_ENV${NC}"
fi

# 7. Verificar que existen las dependencias
echo -e "${BLUE}📦 Verificando dependencias Python...${NC}"
cd backend
python -c "import fastapi, uvicorn, sqlalchemy, openai" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Instalando dependencias faltantes...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencias instaladas${NC}"
else
    echo -e "${GREEN}✓ Dependencias OK${NC}"
fi
cd ..

# 8. Verificar conexión a PostgreSQL
echo -e "${BLUE}🗄️  Verificando conexión a base de datos...${NC}"
python -c "
import sys
sys.path.insert(0, 'backend')
from backend.core.config import settings
from sqlalchemy import create_engine
try:
    engine = create_engine(settings.DATABASE_URL)
    conn = engine.connect()
    conn.close()
    print('✓ Conexión a PostgreSQL OK')
except Exception as e:
    print(f'❌ Error conectando a PostgreSQL: {e}')
    print('Verifica que PostgreSQL esté corriendo y que DATABASE_URL en .env sea correcto')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo -e "${RED}No se pudo conectar a la base de datos${NC}"
    exit 1
fi

# 9. Verificar que existen los PDFs
echo -e "${BLUE}📚 Verificando PDFs de AESA...${NC}"
if [ ! -d "docs" ]; then
    mkdir docs
    echo -e "${YELLOW}⚠️  Carpeta docs/ creada${NC}"
fi

PDF_COUNT=$(ls docs/*.pdf 2>/dev/null | wc -l)
if [ $PDF_COUNT -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No se encontraron PDFs en docs/${NC}"
    echo "El sistema funcionará, pero no tendrá documentación AESA para consultar."
    echo "Coloca los PDFs:"
    echo "  - Formacion.Subcategoria.A1.A3.pdf"
    echo "  - Formacion.Subcategoria.A2.pdf"
else
    echo -e "${GREEN}✓ Encontrados $PDF_COUNT PDF(s) en docs/${NC}"
    ls -1 docs/*.pdf
fi

# 10. Crear directorios necesarios
echo -e "${BLUE}📁 Verificando estructura de directorios...${NC}"
mkdir -p logs
mkdir -p chroma_data
echo -e "${GREEN}✓ Directorios OK${NC}"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Configuración completada${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}🚀 Iniciando servidor FastAPI...${NC}"
echo ""

# 11. Iniciar FastAPI
#cd backend
python -m backend.main

# Si el usuario interrumpe con Ctrl+C
echo ""
echo -e "${YELLOW}Servidor detenido${NC}"
