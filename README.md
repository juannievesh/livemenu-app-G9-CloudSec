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
cd livemenu-app-G8-CloudSec
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y ajusta las variables según necesites:

```bash
cp env.example .env
```

Edita el archivo `.env` y cambia especialmente:
- `SECRET_KEY`: Genera una clave secreta segura para JWT:
  - **Windows (PowerShell):** `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - **Linux/Mac:** `openssl rand -hex 32` o `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `POSTGRES_PASSWORD`: Cambia la contraseña de la base de datos

### 3. Levantar los servicios con Docker Compose

```bash
docker compose up -d
```

Esto levantará:
- PostgreSQL en el puerto 5432
- Backend FastAPI en el puerto 8000

### 4. Verificar que todo funciona

- Backend API: http://localhost:8000
- Documentación API (Swagger): http://localhost:8000/api/docs
- Health check: http://localhost:8000/health

### 5. Ejecutar migraciones de base de datos

Una vez que los modelos estén definidos, ejecuta:

```bash
docker compose exec backend alembic upgrade head
```

## Estructura del Proyecto

```
livemenu-app-G8-CloudSec/
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
├── frontend/                # Frontend (a desarrollar)
├── docker-compose.yml
├── env.example
└── README.md
```

## Desarrollo

### Ejecutar en modo desarrollo

El backend se ejecuta con auto-reload habilitado:

```bash
docker compose up
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

Ver `env.example` para todas las variables disponibles. Las principales son:

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

