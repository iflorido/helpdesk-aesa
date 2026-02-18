# 🚀 Deploy a Producción en VPS con Plesk

Guía para desplegar Helpdesk AESA A2 en tu VPS usando Docker y Plesk.

## 📋 Tu Configuración en VPS

### Base de datos PostgreSQL (ya existente en el VPS)
- **Base de datos:** `admin_aesa`
- **Usuario:** `admin_agenteaesa`
- **Contraseña:** `zG4c0nxSHez%!fr4`
- **Host:** `localhost:5432` (desde dentro del VPS)

### Dominio
- Tu dominio o subdominio configurado en Plesk

## 🏗️ Preparación Inicial

### 1. Conectar al VPS por SSH

```bash
ssh tu-usuario@tu-vps-ip
```

### 2. Clonar el repositorio

```bash
cd /var/www/vhosts/tu-dominio
git clone tu-repositorio helpdesk-aesa
cd helpdesk-aesa
```

### 3. Subir los PDFs de AESA

Copia los PDFs a la carpeta `docs/` del VPS:

```bash
# Opción 1: Desde tu máquina local con SCP
scp docs/*.pdf tu-usuario@tu-vps-ip:/var/www/vhosts/tu-dominio/helpdesk-aesa/docs/

# Opción 2: Usando el gestor de archivos de Plesk
# Sube los archivos a: /var/www/vhosts/tu-dominio/helpdesk-aesa/docs/
```

## 🔐 Configurar Variables de Entorno en Plesk

**Importante:** NO uses archivo `.env` en producción. Configura las variables en Plesk.

### En Plesk:
1. Ve a tu dominio → **Docker** → **Variables de Entorno**
2. Añade estas variables:

```env
# OpenAI
OPENAI_API_KEY=sk-tu-api-key-de-produccion

# Database (PostgreSQL del VPS)
DATABASE_URL=postgresql://admin_agenteaesa:zG4c0nxSHez%!fr4@localhost:5432/admin_aesa

# Security (genera uno nuevo para producción)
SECRET_KEY=genera-uno-nuevo-con-openssl-rand-hex-32

# CORS (tu dominio real)
ALLOWED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com

# Application
ENVIRONMENT=production
DEBUG=False
PROJECT_NAME=Helpdesk AESA A2

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

**Generar SECRET_KEY seguro:**
```bash
openssl rand -hex 32
```

## 🐳 Desplegar con Docker

### Opción A: Usando docker-compose (Recomendado)

```bash
cd /var/www/vhosts/tu-dominio/helpdesk-aesa

# Construir y desplegar
docker-compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f backend

# Verificar estado
docker-compose -f docker-compose.prod.yml ps
```

### Opción B: Construcción manual de la imagen

```bash
# Construir imagen
docker build -t helpdesk-aesa:latest ./backend

# Ejecutar contenedor
docker run -d \
  --name helpdesk-aesa-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://admin_agenteaesa:zG4c0nxSHez%!fr4@host.docker.internal:5432/admin_aesa" \
  -e OPENAI_API_KEY="sk-tu-key" \
  -e SECRET_KEY="tu-secret-key" \
  -e ENVIRONMENT="production" \
  -e DEBUG="False" \
  -e ALLOWED_ORIGINS="https://tu-dominio.com" \
  -v /var/www/vhosts/tu-dominio/helpdesk-aesa/docs:/app/docs:ro \
  helpdesk-aesa:latest
```

## 🌐 Configurar Proxy Inverso en Plesk

### 1. Configurar Apache/Nginx

En Plesk, configura un proxy reverso:

**Para Apache:** En "Configuración Apache & nginx":

```apache
ProxyPass / http://localhost:8000/
ProxyPassReverse / http://localhost:8000/
```

**Para Nginx:**

```nginx
location / {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 2. Configurar SSL

En Plesk:
1. Ve a **SSL/TLS Certificates**
2. Usa **Let's Encrypt** para generar certificado gratuito
3. Activa **Redirigir HTTP a HTTPS**

## 🗄️ Migraciones de Base de Datos

Si necesitas crear las tablas iniciales:

```bash
# Entrar al contenedor
docker exec -it helpdesk-aesa-backend bash

# Ejecutar migraciones (cuando las crees con Alembic)
alembic upgrade head

# Salir
exit
```

## 📚 Procesar PDFs (Crear Vectores)

Una vez desplegado, procesa los PDFs de AESA:

```bash
# Entrar al contenedor
docker exec -it helpdesk-aesa-backend bash

# Ejecutar el ingestor (cuando esté implementado)
python -m backend.rag.ingestor

# Verificar que se crearon los vectores
ls -lh /app/chroma_data/

# Salir
exit
```

## 🔍 Verificar Despliegue

### Test 1: Desde el VPS
```bash
curl http://localhost:8000/health
```

### Test 2: Desde internet
```bash
curl https://tu-dominio.com/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "environment": "production"
}
```

### Test 3: Documentación API
Abre en tu navegador: https://tu-dominio.com/docs

## 📊 Monitoreo

### Ver logs en tiempo real
```bash
docker logs -f helpdesk-aesa-backend
```

### Ver uso de recursos
```bash
docker stats helpdesk-aesa-backend
```

### Ver contenedores corriendo
```bash
docker ps
```

## 🔄 Actualizar la Aplicación

Cuando hagas cambios:

```bash
# 1. En tu máquina local, commitea cambios
git add .
git commit -m "Nuevas funcionalidades"
git push

# 2. En el VPS, actualiza
cd /var/www/vhosts/tu-dominio/helpdesk-aesa
git pull

# 3. Reconstruir y redesplegar
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Verificar logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

## 💾 Backup

### Backup de ChromaDB (vectores)
```bash
# Crear backup
docker exec helpdesk-aesa-backend tar -czf /tmp/chroma-backup.tar.gz /app/chroma_data

# Copiar a host
docker cp helpdesk-aesa-backend:/tmp/chroma-backup.tar.gz ./backups/

# Descargar a local
scp tu-usuario@tu-vps-ip:/path/to/backups/chroma-backup.tar.gz ./
```

### Backup de PostgreSQL
```bash
# Desde el VPS
pg_dump -U admin_agenteaesa admin_aesa > backup_$(date +%Y%m%d).sql

# Comprimir
gzip backup_$(date +%Y%m%d).sql
```

## 🐛 Troubleshooting

### El contenedor no arranca

```bash
# Ver logs detallados
docker logs helpdesk-aesa-backend

# Ver configuración
docker inspect helpdesk-aesa-backend
```

### Error de conexión a PostgreSQL

Verifica que la DATABASE_URL usa `localhost` o `host.docker.internal`:
```bash
# Dentro del contenedor
docker exec -it helpdesk-aesa-backend bash
python -c "from backend.core.config import settings; print(settings.DATABASE_URL)"
```

Si PostgreSQL está en el host (no en contenedor):
- Usa `host.docker.internal:5432` en lugar de `localhost:5432`
- O configura la red de Docker apropiadamente

### Error 502 Bad Gateway

- Verifica que el contenedor está corriendo: `docker ps`
- Verifica que el puerto 8000 está abierto: `netstat -tlnp | grep 8000`
- Verifica la configuración del proxy en Plesk

### Puerto 8000 ya en uso

```bash
# Ver qué está usando el puerto
lsof -i :8000

# Matar proceso si es necesario
kill -9 <PID>
```

## 🔐 Seguridad en Producción

### Checklist:
- ✅ Variables de entorno en Plesk (no en `.env`)
- ✅ `DEBUG=False` en producción
- ✅ `SECRET_KEY` único y seguro
- ✅ SSL/HTTPS configurado (Let's Encrypt)
- ✅ Firewall configurado (solo 80, 443 abiertos)
- ✅ PostgreSQL sin puerto expuesto públicamente
- ✅ ChromaDB sin puerto expuesto públicamente
- ✅ CORS configurado solo para tu dominio
- ✅ Rate limiting activado

### Firewall (iptables o ufw):
```bash
# Permitir solo SSH, HTTP y HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

## 📈 Optimización

### Aumentar workers de Uvicorn
En `docker-compose.prod.yml`, ajusta según CPU del VPS:
```yaml
command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Regla general: `workers = (2 x num_cores) + 1`

### Limitar recursos del contenedor
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs: `docker logs helpdesk-aesa-backend`
2. Verifica variables de entorno en Plesk
3. Confirma que PostgreSQL del VPS está accesible
4. Verifica que los PDFs están en `docs/`