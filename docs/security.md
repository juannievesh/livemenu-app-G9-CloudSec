# LiveMenu - Controles de seguridad

## 1. Cifrado de datos

### 1.1 Cifrado en reposo
- Cloud SQL y Cloud Storage utilizan el cifrado en reposo predeterminado de Google Cloud.

- Cloud Storage cifra los datos de usuario en reposo con AES-256 de forma predeterminada.

- Si es necesario, se puede habilitar CMEK posteriormente mediante Cloud KMS para Cloud SQL y Cloud Storage.

### 1.2 Cifrado en tránsito
- Todo el tráfico a la aplicación se sirve a través de HTTPS.

- Cloud Run expone un punto final HTTPS estable de forma predeterminada.

- El menú público solo debe ser accesible a través de `https://`.

## 2. Gestión de secretos

### 2.1 No se permiten archivos `.env` en producción
- Los archivos `.env` solo están permitidos en el entorno de desarrollo local.

- Las credenciales de producción se almacenan en Google Secret Manager.

### 2.2 Carga de secretos en tiempo de ejecución
- El backend lee los secretos en tiempo de ejecución desde Secret Manager.
- El módulo `backend/app/core/secrets.py` encapsula la recuperación de secretos.

- Los secretos se cargan solo cuando `ENVIRONMENT=production`.

### 2.3 ID de secretos
- `livemenu-db-url`
- `livemenu-secret-key`
- `livemenu-gcs-bucket`

### 2.4 Versiones de secretos
- Se accede a los secretos utilizando la versión más reciente.

- La rotación crea una nueva versión sin modificar el código de la aplicación.

## 3. Política de rotación
- La URL de la base de datos y el secreto JWT rotan cada 40 días.

- Los programas de rotación del Administrador de secretos se configuran a nivel de secreto.

- La rotación debe emitir notificaciones para que la nueva versión esté disponible para el siguiente despliegue/reinicio.

## 4. Principio de mínimo privilegio de IAM
- La cuenta de servicio del backend solo recibe los permisos mínimos necesarios.
- Roles recomendados:

- `roles/secretmanager.secretAccessor`

- `roles/storage.objectCreator`

- `roles/cloudsql.client`

## 5. Notas operativas
- Cloud Run debe ejecutarse con su propia cuenta de servicio dedicada.

- El entorno de desarrollo local utiliza `.env`; el entorno de producción utiliza Secret Manager.

- Tras una rotación de secretos, el servicio debe reiniciarse o volver a implementarse para que se aplique la nueva versión del secreto.