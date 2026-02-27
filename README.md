# livemenu-app-G8-CloudSec

LiveMenu: Gestor de menús digitales para restaurantes

## Descripción

LiveMenu es una plataforma SaaS que permite a restaurantes gestionar su menú digital de forma dinámica. El sistema genera una landing page optimizada para móvil y un código QR estático que los clientes escanean.

## Documentación del Proyecto

La guía de división de trabajo está disponible en la wiki del repositorio.

## Requisitos Previos

- Docker y Docker Compose instalados
- Git

## Instalación y Setup

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd livemenu-app-G9-CloudSec
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y ajusta las variables:

```bash
cp .env.example .env
```

Edita `.env` y cambia:
- `SECRET_KEY`: Genera una clave segura para JWT:
  - **Windows (PowerShell):** `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - **Linux/Mac:** `openssl rand -hex 32` o `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `POSTGRES_PASSWORD`: Contraseña de la base de datos

**Imágenes (GCP):** El backend monta `gcp-credentials.json` desde la raíz. Crea el archivo antes de levantar:
- Con GCP: coloca tu archivo de credenciales de servicio.
- Sin GCP: `echo {} > gcp-credentials.json` (el backend arranca; la subida de imágenes fallará hasta configurar GCP).

### 3. Levantar la base de datos y ejecutar migraciones

**Importante:** Las migraciones deben ejecutarse antes de que el backend cree tablas. Sigue este orden:

```bash
# 1. Levantar solo la base de datos
docker compose up -d db

# 2. Esperar a que esté lista (unos segundos) y ejecutar migraciones
docker compose run --rm backend alembic upgrade head

# 3. Levantar el resto de servicios
docker compose up -d
```

### 4. Verificar que todo funciona

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/api/docs
- Health: http://localhost:8000/health

**Servicios y puertos:**
- PostgreSQL: **54320** (host)
- Backend: **8000**
- Frontend: **3000**

### Si las migraciones fallan con "relation already exists"

Si ya ejecutaste `docker compose up -d` antes de las migraciones, el backend habrá creado tablas con `create_all`. En ese caso:

```bash
docker compose exec backend alembic stamp head
```

Esto marca la base de datos como actualizada sin ejecutar migraciones. Luego reinicia el backend si es necesario.

## Estructura del Proyecto

```
livemenu-app-G9-CloudSec/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/          # Endpoints de la API
│   │   ├── core/            # Configuración y base de datos
│   │   ├── models/          # Modelos de SQLAlchemy
│   │   ├── services/        # Lógica de negocio
│   │   ├── repositories/    # Acceso a datos
│   │   └── workers/         # Worker pool para imágenes
│   ├── alembic/             # Migraciones de base de datos
│   ├── tests/               # Tests unitarios e integración
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # Frontend React + Vite + Tailwind
├── docker-compose.yml
├── .env.example
└── README.md
```

## Desarrollo

### Ejecutar en modo desarrollo

```bash
docker compose up
```

El backend y frontend se ejecutan con auto-reload. Para desarrollar solo el frontend sin Docker:

```bash
cd frontend
cp .env.example .env   # Ajusta VITE_API_URL si el backend está en otra URL
npm install
npm run dev
```

### Ejecutar tests

```bash
docker compose exec backend pytest
```

### Ver logs

```bash
docker compose logs -f backend
docker compose logs -f db
```

## Variables de Entorno

Ver `.env.example` para todas las variables disponibles. Las principales son:

- `DATABASE_URL`: URL de conexión a PostgreSQL
- `SECRET_KEY`: Clave secreta para JWT (cambiar en producción)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Tiempo de expiración de tokens
- `STORAGE_TYPE`: Tipo de almacenamiento (local, s3, etc.)
- `WORKER_POOL_SIZE`: Número de workers para procesamiento de imágenes

## API Endpoints

Una vez implementados, los endpoints estarán disponibles en:

- Autenticación: `/api/v1/auth/*`
- Restaurantes: `/api/v1/admin/restaurant`
- Categorías: `/api/v1/admin/categories`
- Platos: `/api/v1/admin/dishes`
- Menú público: `/api/v1/menu/:slug`
- Upload: `/api/v1/admin/upload`
- QR: `/api/v1/admin/qr`

Ver documentación completa en: http://localhost:8000/api/docs

