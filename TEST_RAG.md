# 📚 Pipeline RAG - Procesar Documentos AESA

Guía para procesar los PDFs de AESA y crear la base de conocimiento vectorial.

## 🎯 ¿Qué hace el Pipeline RAG?

1. **Lee los PDFs** de la carpeta `docs/`
2. **Extrae el texto** de cada página
3. **Divide en chunks** (fragmentos de ~1000 caracteres con solapamiento)
4. **Crea embeddings** (vectores) de cada chunk usando ChromaDB
5. **Indexa** todo en una base de datos vectorial para búsqueda semántica
6. **Registra** los documentos procesados en PostgreSQL

## 📋 Prerrequisitos

Asegúrate de tener los PDFs en la carpeta `docs/`:

```bash
ls docs/
# Deberías ver:
# Formacion.Subcategoria.A1.A3.pdf
# Formacion.Subcategoria.A2.pdf
```

## 🚀 Procesar los Documentos

### Paso 1: Ejecutar el ingestor

```bash
cd backend
python -m rag.ingestor
```

### Paso 2: Ver el proceso

Deberías ver algo como:

```
🚀 Iniciando ingesta de documentos...
📂 Encontrados 2 PDFs en /path/to/docs

============================================================
📄 Procesando: Formacion.Subcategoria.A2.pdf
============================================================
📌 Tipo de documento: pdf_aesa_a2
📄 Extraído texto de 45 páginas de Formacion.Subcategoria.A2.pdf
✂️ Texto dividido en 87 chunks
💾 Guardando 87 chunks en ChromaDB...
✅ Añadidos 87 documentos a ChromaDB
➕ Documento registrado en BD
✅ Formacion.Subcategoria.A2.pdf procesado correctamente

============================================================
📄 Procesando: Formacion.Subcategoria.A1.A3.pdf
============================================================
📌 Tipo de documento: pdf_aesa_a1
📄 Extraído texto de 38 páginas de Formacion.Subcategoria.A1.A3.pdf
✂️ Texto dividido en 72 chunks
💾 Guardando 72 chunks en ChromaDB...
✅ Añadidos 72 documentos a ChromaDB
➕ Documento registrado en BD
✅ Formacion.Subcategoria.A1.A3.pdf procesado correctamente

============================================================
🎉 PROCESO COMPLETADO
============================================================
📊 Estadísticas:
   - PDFs procesados: 2
   - Chunks totales: 159
   - Documentos en ChromaDB: 159
   - Documentos en BD: 2
```

## 🔍 Verificar que Funcionó

### 1. Verificar en ChromaDB

Los vectores se guardan en la carpeta `chroma_data/`:

```bash
ls -lh chroma_data/
```

### 2. Verificar en PostgreSQL

```bash
psql -U postgres -d aesa_agent

-- Ver documentos procesados
SELECT filename, document_type, processed, vector_count, page_count 
FROM documents;

-- Debería mostrar algo como:
--           filename                 | document_type | processed | vector_count | page_count
-- -----------------------------------+---------------+-----------+--------------+------------
--  Formacion.Subcategoria.A2.pdf    | pdf_aesa_a2   | t         |           87 |         45
--  Formacion.Subcategoria.A1.A3.pdf | pdf_aesa_a1   | t         |           72 |         38
```

### 3. Probar búsqueda (Python)

Crea un archivo `test_search.py`:

```python
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from rag import get_vector_store

# Obtener vector store
vs = get_vector_store()

# Probar búsqueda
query = "distancia mínima zonas habitadas"
results = vs.search(query, n_results=3)

print(f"\n🔍 Búsqueda: '{query}'\n")
print(f"📊 Resultados encontrados: {len(results['documents'][0])}\n")

for i, (doc, meta, dist) in enumerate(zip(
    results['documents'][0],
    results['metadatas'][0],
    results['distances'][0]
)):
    print(f"--- Resultado {i+1} ---")
    print(f"Fuente: {meta['source']}")
    print(f"Tipo: {meta['document_type']}")
    print(f"Relevancia: {1 - dist:.2%}")
    print(f"Texto: {doc[:200]}...")
    print()
```

Ejecuta:

```bash
python test_search.py
```

Deberías ver resultados relevantes del PDF de AESA.

## 🔄 Re-procesar Documentos

Si modificas los PDFs o quieres volver a procesarlos:

```bash
# Opción 1: Eliminar y volver a crear
rm -rf chroma_data/
python -m rag.ingestor

# Opción 2: El ingestor detecta documentos ya procesados y los salta
# Solo procesa nuevos PDFs
python -m rag.ingestor
```

## 📊 Estadísticas del Vector Store

Puedes crear un script para ver estadísticas:

```python
from rag import get_vector_store

vs = get_vector_store()
stats = vs.get_stats()

print("📊 Estadísticas del Vector Store:")
print(f"   Total documentos: {stats['total_documents']}")
print(f"   Colección: {stats['collection_name']}")
```

## ⚙️ Configuración Avanzada

### Ajustar tamaño de chunks

En `rag/document_processor.py`, puedes modificar:

```python
processor = DocumentProcessor(
    chunk_size=1000,      # Caracteres por chunk
    chunk_overlap=200     # Solapamiento entre chunks
)
```

**Recomendaciones:**
- `chunk_size=500-1500`: Más pequeño = más preciso, más grande = más contexto
- `chunk_overlap=100-300`: Asegura que no se pierda información en los bordes

### Filtrar búsquedas por tipo de documento

```python
# Solo buscar en documentos A2
results = vs.search(
    query="altura máxima",
    n_results=5,
    where={"document_type": "pdf_aesa_a2"}
)
```

## ❌ Troubleshooting

### Error: "No existe la carpeta docs/"

```bash
# Crear la carpeta y añadir los PDFs
mkdir -p docs
# Copia tus PDFs de AESA aquí
```

### Error: ChromaDB no responde

```bash
# Verificar que el directorio existe y tiene permisos
ls -la chroma_data/

# Si falla, eliminar y recrear
rm -rf chroma_data/
python -m rag.ingestor
```

### No se extrajo texto del PDF

Algunos PDFs pueden estar escaneados (imágenes). Necesitarías OCR:

```bash
pip install pytesseract
```

Pero los PDFs oficiales de AESA deberían tener texto extraíble.

## 🎯 Próximos Pasos

Una vez que los documentos estén procesados:

1. ✅ Crear el agente OpenAI
2. ✅ Integrar RAG en las respuestas del chat
3. ✅ Añadir tools al agente (buscar docs, clasificar, escalar)
4. ✅ Implementar auto-respuesta cuando el usuario envía un mensaje

## 💡 Tips

- Los embeddings se crean automáticamente por ChromaDB
- La búsqueda es semántica, no por palabras clave
- Cuantos más documentos, mejor será la precisión
- El procesamiento es idempotente: puedes ejecutarlo varias veces sin duplicar