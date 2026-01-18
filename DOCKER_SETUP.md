# 🐳 Guía Completa: Iniciar Docker desde Cero

## 📋 Requisitos Previos

- Docker Desktop instalado y corriendo
- Clave API de Google Gemini (gratuita)

---

## 🚀 Paso a Paso: Iniciar desde Cero

### Paso 1: Preparar el archivo `.env`

En la raíz del proyecto, crea o edita el archivo `.env`:

```bash
# Si no existe, créalo desde el template
cp .env.example .env
```

**Edita `.env` y agrega tu GEMINI_API_KEY:**

```env
GEMINI_API_KEY=tu_clave_aqui_xxxxxxx
POSTGRES_USER=enrichment_user
POSTGRES_PASSWORD=enrichment_pass
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=lead_enrichment
CHROMA_PERSIST_DIR=./chroma_data
DEBUG=true
```

**📝 Obtener GEMINI_API_KEY:**
- Ve a: https://makersuite.google.com/app/apikey
- Crea una cuenta o inicia sesión
- Genera una nueva API key
- Cópiala al archivo `.env`

---

### Paso 2: Limpiar contenedores anteriores (si existen)

```bash
# Detener y eliminar contenedores anteriores
docker-compose down

# Si quieres limpiar también volúmenes (elimina datos de PostgreSQL)
docker-compose down -v
```

---

### Paso 3: Construir y levantar los servicios

```bash
# Construir imágenes y levantar todo
docker-compose up --build
```

**O en modo detached (corre en segundo plano):**

```bash
docker-compose up -d --build
```

**⏱️ Tiempo esperado:** 2-5 minutos (primera vez descarga imágenes)

---

### Paso 4: Verificar que todo está corriendo

**1. Ver logs del backend:**

```bash
docker-compose logs backend
```

Deberías ver algo como:
```
🚀 Starting AI Lead Enrichment Pipeline...
✅ Vector DB initialized. Collection: 0 documents
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**2. Verificar contenedores:**

```bash
docker-compose ps
```

Deberías ver:
- `lead-enrichment-db` (PostgreSQL) - Status: Up
- `lead-enrichment-api` (FastAPI) - Status: Up

**3. Health Check HTTP:**

```bash
curl http://localhost:8000/
```

O abre en el navegador: http://localhost:8000/

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "services": {
    "api": true,
    "enrichment": true,
    "vector_db": true
  }
}
```

---

### Paso 5: Probar la API (Swagger UI)

Abre en tu navegador: **http://localhost:8000/docs**

Aquí puedes:
- ✅ Ver todos los endpoints
- ✅ Probar la API interactivamente
- ✅ Ver ejemplos de requests/responses

---

## 🧪 Ejecutar Tests en Docker

### Opción 1: Ejecutar tests dentro del contenedor backend

```bash
# Ejecutar todos los tests
docker-compose exec backend pytest

# Ejecutar tests con verbose
docker-compose exec backend pytest -v

# Ejecutar un test específico
docker-compose exec backend pytest tests/test_main.py -v

# Ejecutar con coverage
docker-compose exec backend pytest --cov=. --cov-report=html
```

### Opción 2: Servicio dedicado de tests (Recomendado)

Ya está configurado en `docker-compose.yml`. Ejecuta:

```bash
# Ejecutar tests (crea contenedor temporal, ejecuta tests, y se elimina)
docker-compose run --rm test

# Con verbose
docker-compose run --rm test pytest -v

# Con coverage
docker-compose run --rm test pytest --cov=. --cov-report=term
```

### Opción 3: Ejecutar tests manualmente en contenedor

```bash
# Entrar al contenedor
docker-compose exec backend bash

# Dentro del contenedor:
cd /app
pytest -v
exit
```

---

## 📝 Comandos Útiles de Docker

### Ver logs en tiempo real

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo postgres
docker-compose logs -f postgres
```

### Detener servicios

```bash
# Detener sin eliminar volúmenes
docker-compose stop

# Detener y eliminar contenedores (mantiene volúmenes)
docker-compose down

# Detener y eliminar TODO (incluyendo volúmenes - ⚠️ borra datos)
docker-compose down -v
```

### Reconstruir después de cambios

```bash
# Si cambias código o requirements.txt
docker-compose up --build

# O solo reconstruir backend
docker-compose build backend
docker-compose up -d backend
```

### Acceder a la base de datos PostgreSQL

```bash
# Entrar a PostgreSQL
docker-compose exec postgres psql -U enrichment_user -d lead_enrichment

# Comandos útiles dentro de psql:
\dt          # Listar tablas
\d tabla     # Describir tabla
\q           # Salir
```

### Limpiar todo (reiniciar desde cero)

```bash
# ⚠️ CUIDADO: Esto elimina TODO (contenedores, volúmenes, redes)
docker-compose down -v --rmi all

# Luego reconstruir
docker-compose up --build
```

---

## 🐛 Solución de Problemas Comunes

### ❌ Error: "GEMINI_API_KEY not found"

**Solución:** Verifica que `.env` existe y tiene `GEMINI_API_KEY=tu_clave`

```bash
# Ver contenido del .env
cat .env

# Reiniciar después de agregar la clave
docker-compose restart backend
```

### ❌ Error: "Port 8000 already in use"

**Solución:** Cambia el puerto en `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Cambia 8000 por 8001 (o cualquier otro)
```

### ❌ Error: "Cannot connect to postgres"

**Solución:** Espera unos segundos y verifica:

```bash
# Ver estado de PostgreSQL
docker-compose ps postgres

# Ver logs de PostgreSQL
docker-compose logs postgres

# Si está iniciando, espera ~10 segundos
```

### ❌ Error: Tests no encuentran módulos

**Solución:** Los tests deben ejecutarse dentro del contenedor donde PYTHONPATH está configurado:

```bash
# ✅ Correcto
docker-compose exec backend pytest

# ❌ Incorrecto (desde tu máquina local)
pytest  # No funcionará si no tienes dependencias instaladas
```

---

## ✅ Checklist: Todo está funcionando si...

- [ ] `docker-compose ps` muestra ambos contenedores como "Up"
- [ ] `curl http://localhost:8000/` devuelve `{"status": "healthy"}`
- [ ] Swagger UI abre en http://localhost:8000/docs
- [ ] Puedes hacer un POST a `/enrich` desde Swagger
- [ ] Los tests se ejecutan sin errores: `docker-compose run --rm test`

---

## 🎯 Próximos Pasos

1. **Probar endpoints manualmente:**
   - Health Check: http://localhost:8000/
   - Swagger UI: http://localhost:8000/docs
   - Enriquecer una empresa desde Swagger

2. **Ejecutar tests:**
   ```bash
   docker-compose run --rm test
   ```

3. **Revisar logs si hay problemas:**
   ```bash
   docker-compose logs -f backend
   ```

---

**¡Listo! Tu backend está corriendo en Docker 🚀**
