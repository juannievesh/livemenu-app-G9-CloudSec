# docs/rpo-rto.md

# LiveMenu – Análisis RPO / RTO

## Objetivo del servicio

Mantener la operación del menú público de LiveMenu con alta disponibilidad y capacidad de recuperación ante incidentes.

---

# Valores definidos

## RPO: 24 horas

Se acepta una pérdida máxima de datos de hasta **24 horas** en caso de falla crítica de base de datos.

Esto significa:

- Si ocurre una caída total hoy a las 6:00 p.m.
- La información podría restaurarse hasta el último backup exitoso realizado dentro de las últimas 24 horas.

## RTO: 30 minutos

Tiempo máximo objetivo para restaurar el servicio después de una interrupción grave:

- Frontend fuera de línea
- Backend caído
- Error severo en despliegue
- Falla de base de datos

El sistema debe volver a operar en máximo **30 minutos**.

---

# Arquitectura considerada

- Frontend en Cloud Run
- Backend FastAPI en Cloud Run
- Base de datos Cloud SQL PostgreSQL
- Artifact Registry
- HTTPS Load Balancer
- DNS público

---

# Procedimientos de recuperación

## Escenario 1: caída del frontend

### Acción

1. Verificar Cloud Run frontend
2. Revisar logs
3. Restaurar revisión anterior estable
4. Validar acceso web

### Tiempo estimado

5 a 10 minutos

---

## Escenario 2: caída del backend

### Acción

1. Revisar logs de Cloud Run
2. Confirmar variables de entorno
3. Verificar conexión con Cloud SQL
4. Redeploy de última imagen funcional
5. Validar endpoints `/docs` y `/api`

### Tiempo estimado

10 a 20 minutos

---

## Escenario 3: falla de base de datos

### Acción

1. Ingresar a Cloud SQL
2. Restaurar backup automático más reciente
3. Reconectar backend
4. Validar autenticación y datos

### Tiempo estimado

20 a 30 minutos

---

## Escenario 4: error en despliegue

### Acción

1. Rollback inmediato a revisión anterior en Cloud Run
2. Redirigir tráfico a versión estable

### Tiempo estimado

5 minutos

---

# Estrategia de backups

| Recurso | Método | Frecuencia |
|--------|--------|------------|
| Base de datos | Backup automático Cloud SQL | Diario |
| Código fuente | GitHub / Git | Continuo |
| Imágenes | Artifact Registry | Cada release |

---

# Cumplimiento operativo

Para sostener RTO de 30 min:

- Revisiones previas listas en Cloud Run
- Imágenes versionadas
- Acceso administrativo inmediato
- Monitoreo activo
- Procedimientos documentados

---

# Riesgos residuales

- Error DNS externo
- Daño lógico de datos previo al backup
- Mala configuración humana
- Dependencia de GCP regional

---

# Recomendaciones futuras

- Backups cada 6 horas
- Réplica regional secundaria
- Alertas automáticas
- CI/CD con rollback automático
- Monitoreo sintético

---

# Responsable

Persona 1 – Despliegue en Nube + Arquitectura