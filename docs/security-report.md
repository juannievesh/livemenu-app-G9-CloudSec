# Reporte de Seguridad y CI/CD - LiveMenu

## 1. Arquitectura de Autenticación (Zero-Trust)
Establecer un modelo de seguridad basado en la confianza cero (Zero-Trust) para la comunicación entre el entorno de Integración Continua y Google Cloud Platform (GCP). Implementar la arquitectura de Workload Identity Federation (WIF) mediante OpenID Connect (OIDC), con el propósito de eliminar definitivamente el uso y almacenamiento de claves estáticas de cuentas de servicio (archivos JSON) de larga duración.
Garantizar, mediante esta configuración, que el integrador continuo solicite tokens de acceso efímeros, con una vida útil máxima de una hora, directamente a la API de Google Cloud. Restringir la emisión de estos tokens de forma criptográfica, aplicando una condición de seguridad (attribute.condition) que autoriza exclusivamente al repositorio oficial del proyecto a suplantar la identidad de la cuenta de servicio aprovisionada.
Rutas de código fuente asociadas:
- Implementación del proveedor de identidad y autenticación en el pipeline: .github/workflows/ci.yml (Bloque deploy-to-gcp, acción google-github-actions/auth@v2).

## 2. Integración Continua y Escaneo de Contenedores (DevSecOps)
Integrar la herramienta de análisis estático Trivy dentro del flujo de trabajo automatizado, estableciendo una barrera de seguridad infranqueable (Quality Gate) antes de cualquier proceso de despliegue. Configurar el escáner de vulnerabilidades para auditar las imágenes de los contenedores Docker (tanto del frontend como del backend) de forma paralela y aislada.
Configurar la regla de interrupción estricta en el pipeline, forzando un código de salida por fallo (exit-code: '1') que aborta automáticamente la construcción del sistema en caso de detectar vulnerabilidades catalogadas con severidad HIGH o CRITICAL. Asegurar la inmutabilidad y transparencia del análisis requiriendo que la verificación de dependencias se complete exitosamente, generando un reporte en formato SARIF, antes de autorizar la compresión y envío de los artefactos hacia el Artifact Registry de GCP.
Rutas de código fuente asociadas:
- Configuración del motor de escaneo y generación de reportes SARIF: .github/workflows/ci.yml (Bloque security-scan).
- Definición del entorno base del contenedor para el análisis del Backend: backend/Dockerfile (Capa de instalación de dependencias del sistema operativo).
- Definición del entorno base del contenedor para el análisis del Frontend: frontend/Dockerfile.

## 3. Gestión de Riesgos Aceptados y Excepciones (.trivyignore)
Documentar y formalizar las vulnerabilidades identificadas durante los escaneos preliminares que no poseen un parche oficial proveído por el fabricante (Upstream) o que presentan conflictos de dependencias estrictos y circulares en la arquitectura de software actual.
Registrar las siguientes excepciones en el manifiesto de control del escáner, asumiendo un riesgo temporal controlado para permitir la operatividad del sistema sin comprometer las políticas de Integración Continua:
- CVE-2025-69720 (Componentes ncurses / libtinfo6): Aceptar el riesgo asociado a un posible desbordamiento de búfer (Buffer Overflow) en las librerías de interfaz de terminal del sistema operativo base Debian 13.4. Confirmar la inexistencia de una versión parcheada disponible en los repositorios oficiales al momento de la auditoría.
- CVE-2026-29111 (Componentes systemd / libudev1): Aceptar el riesgo crítico en la gestión de comunicación entre procesos (IPC) nativa de Debian 13.4, cuya explotación requiere acceso previo al contenedor. Mantener el riesgo documentado hasta la publicación de un parche oficial por parte del mantenedor del sistema operativo.
- CVE-2024-23342 (Librería Python ecdsa): Aceptar el riesgo de vulnerabilidad criptográfica por ataque de canal lateral basado en tiempos de ejecución (Ataque Minerva). Documentar la falta de una versión corregida compatible con la estructura del proyecto.
- CVE-2026-30922 (Librería Python pyasn1): Aceptar el riesgo de vulnerabilidad por recursión infinita (Stack Exhaustion). Evidenciar que la actualización hacia la versión mitigadora (0.6.3) es incompatible debido a una dependencia circular estricta (<0.5.0) impuesta por la librería central de gestión de tokens criptográficos del proyecto.
Rutas de código fuente asociadas:
- Manifiesto de exclusión de vulnerabilidades: .trivyignore.
- Declaración de dependencias del sistema: backend/requirements.txt.

## 4. Evidencias de Ejecución
### A. Tabla de Resultados del Análisis de Seguridad (Frontend)

### B. Tabla de Resultados del Análisis de Seguridad (Backend)

### C. Evidencia de Ejecución en GitHub Actions
[Insertar aquí la captura de pantalla del reporte de Code Scanning o del log de GitHub Actions con los pasos de construcción y seguridad validados]
### D. Evidencia de Repositorio en GCP Artifact Registry
<img width="975" height="247" alt="image" src="https://github.com/user-attachments/assets/c96dff2a-1af3-445b-8248-667ce5317133" />
