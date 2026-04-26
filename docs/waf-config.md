# LiveMenu – Configuración del WAF (Google Cloud Armor)

> **Responsable:** Persona 4 – WAF + Backup + Resiliencia + IaC
> **Criterio evaluado:** WAF (15%) + Grupos de seguridad / least-privilege
> **Estado del entorno:** ver sección [9. Estado actual y hallazgos](#9-estado-actual-y-hallazgos)

---

## 1. Objetivo

Proteger la aplicación LiveMenu desplegada en GCP frente a ataques a nivel de aplicación (capa 7) mediante **Google Cloud Armor**, posicionado delante del balanceador de cargas HTTPS clásico `livemenu-map`. El WAF debe:

1. Mitigar el OWASP Top 10 (SQLi, XSS, LFI/RFI, RCE, Scanner Detection) con las reglas pre-configuradas de Google basadas en ModSecurity Core Rule Set (CRS) v3.3.
2. Reforzar el **rate limiting** ya implementado en el middleware FastAPI (`backend/app/core/rate_limit.py`) con un control perimetral a nivel de IP.
3. (Opcional) Habilitar **geo-filtering** para restringir o priorizar tráfico según país.
4. Generar **registros (logs)** de cada request bloqueado para auditoría y para la sustentación del proyecto.

---

## 2. Arquitectura del WAF

```
                     Internet
                         │
                         ▼
            ┌────────────────────────┐
            │  Cloud Armor Policy    │  ◄── livemenu-waf-policy
            │  (OWASP + Rate Limit)  │
            └───────────┬────────────┘
                        │ allow / deny-403 / throttle
                        ▼
        ┌──────────────────────────────────┐
        │  HTTPS Load Balancer             │  ◄── livemenu-map
        │  35.190.117.209:443              │
        │  cert: livemenu-cert             │
        │  TLS policy: livemenu-tls12      │
        └──────────────┬───────────────────┘
                       │
        ┌──────────────┴───────────────┐
        ▼                              ▼
  /api/* → backend-backend     /* → frontend-backend
        │                              │
        ▼                              ▼
  backend-neg (NEG)            frontend-neg (NEG)
        │                              │
        ▼                              ▼
  Cloud Run: livemenu-backend  Cloud Run: livemenu-frontend
```

La política se asocia a **ambos** backend services del LB (`backend-backend` y `frontend-backend`). Esto cubre tanto el menú público como el panel administrativo.

---

## 3. Reglas implementadas

### 3.1 Reglas pre-configuradas OWASP (CRS v3.3)

| Prioridad | Regla | Acción | Severidad mínima | Cobertura |
|-----------|-------|--------|------------------|-----------|
| 1000 | `sqli-v33-stable` | `deny-403` | sensitivity 1 | OWASP A03 – Injection (SQLi) |
| 1001 | `xss-v33-stable` | `deny-403` | sensitivity 1 | OWASP A03 – Cross-Site Scripting |
| 1002 | `lfi-v33-stable` | `deny-403` | sensitivity 1 | Local File Inclusion |
| 1003 | `rfi-v33-stable` | `deny-403` | sensitivity 1 | Remote File Inclusion |
| 1004 | `rce-v33-stable` | `deny-403` | sensitivity 1 | Remote Code Execution |
| 1005 | `scannerdetection-v33-stable` | `deny-403` | sensitivity 1 | Detección de scanners (sqlmap, nikto…) |
| 1006 | `protocolattack-v33-stable` | `deny-403` | sensitivity 1 | HTTP smuggling, request splitting |
| 1007 | `sessionfixation-v33-stable` | `deny-403` | sensitivity 1 | Session fixation |

> Documentación oficial de las reglas pre-configuradas: <https://cloud.google.com/armor/docs/rule-tuning>

### 3.2 Rate limiting perimetral

| Prioridad | Match | Acción | Conformidad | Excedente | Ventana | Clave |
|-----------|-------|--------|-------------|-----------|---------|-------|
| 2000 | `request.path.startsWith("/api/")` | `throttle` | 100 req/min | `deny-429` | 60 s | IP origen |

Esto **refuerza** (no reemplaza) el `RateLimitMiddleware` de FastAPI. El control perimetral es más barato (no consume cómputo de Cloud Run) y bloquea atacantes antes de llegar al backend.

### 3.3 Geo-filtering (opcional, **no aplicado por defecto**)

Si en algún momento se decide restringir tráfico:

| Prioridad | Match | Acción | Comentario |
|-----------|-------|--------|------------|
| 3000 | `origin.region_code == 'CN' \|\| origin.region_code == 'RU'` | `deny-403` | Bloqueo regiones de alta hostilidad |
| 3001 | `!(origin.region_code in ['CO','US','MX','PE','AR','CL','EC'])` | `deny-403` | Whitelist Latam + US (recomendado solo si se confirma alcance) |

> El menú público es global; antes de activar geo-filtering, P4 debe confirmar con producto el alcance objetivo.

### 3.4 Regla por defecto

| Prioridad | Match | Acción |
|-----------|-------|--------|
| 2147483647 | `*` | `allow` |

---

## 4. Aplicación con `gcloud` (Cloud Shell)

> Ver script ejecutable en [`scripts/p4-apply-waf.sh`](../scripts/p4-apply-waf.sh).

### 4.1 Variables base

```bash
export PROJECT_ID="livemenu-project"
export REGION="us-central1"
export POLICY_NAME="livemenu-waf-policy"
export BACKEND_SVC_API="backend-backend"
export BACKEND_SVC_FRONT="frontend-backend"

gcloud config set project "$PROJECT_ID"
```

### 4.2 Crear la política

```bash
gcloud compute security-policies create "$POLICY_NAME" \
  --description="LiveMenu WAF – OWASP Top 10 + Rate Limiting" \
  --type=CLOUD_ARMOR

# Habilitar logging detallado (clave para la sustentación)
gcloud compute security-policies update "$POLICY_NAME" \
  --log-level=VERBOSE
```

### 4.3 Cargar las reglas OWASP

```bash
declare -A RULES=(
  ["1000"]="sqli-v33-stable|OWASP: SQL Injection"
  ["1001"]="xss-v33-stable|OWASP: Cross-Site Scripting"
  ["1002"]="lfi-v33-stable|OWASP: Local File Inclusion"
  ["1003"]="rfi-v33-stable|OWASP: Remote File Inclusion"
  ["1004"]="rce-v33-stable|OWASP: Remote Code Execution"
  ["1005"]="scannerdetection-v33-stable|Scanner Detection"
  ["1006"]="protocolattack-v33-stable|Protocol Attack"
  ["1007"]="sessionfixation-v33-stable|Session Fixation"
)

for PRIORITY in "${!RULES[@]}"; do
  IFS='|' read -r EXPR DESC <<< "${RULES[$PRIORITY]}"
  gcloud compute security-policies rules create "$PRIORITY" \
    --security-policy="$POLICY_NAME" \
    --expression="evaluatePreconfiguredExpr('${EXPR}')" \
    --action=deny-403 \
    --description="$DESC"
done
```

### 4.4 Cargar el rate limiting

```bash
gcloud compute security-policies rules create 2000 \
  --security-policy="$POLICY_NAME" \
  --expression="request.path.startsWith('/api/')" \
  --action=throttle \
  --rate-limit-threshold-count=100 \
  --rate-limit-threshold-interval-sec=60 \
  --conform-action=allow \
  --exceed-action=deny-429 \
  --enforce-on-key=IP \
  --description="Rate limit perimetral 100 req/min por IP en /api/*"
```

### 4.5 Asociar la política a los backend services

```bash
gcloud compute backend-services update "$BACKEND_SVC_API" \
  --security-policy="$POLICY_NAME" --global

gcloud compute backend-services update "$BACKEND_SVC_FRONT" \
  --security-policy="$POLICY_NAME" --global
```

### 4.6 Habilitar logs de los backend services (para auditoría)

```bash
gcloud compute backend-services update "$BACKEND_SVC_API" \
  --enable-logging --logging-sample-rate=1.0 --global
gcloud compute backend-services update "$BACKEND_SVC_FRONT" \
  --enable-logging --logging-sample-rate=1.0 --global
```

---

## 5. Verificación y pruebas

### 5.1 Verificar la política

```bash
gcloud compute security-policies describe "$POLICY_NAME"
gcloud compute security-policies rules list --security-policy="$POLICY_NAME"

gcloud compute backend-services describe "$BACKEND_SVC_API" --global \
  --format="value(securityPolicy)"
```

### 5.2 Pruebas de bloqueo (¡estas son las que graban en el video demo!)

```bash
# Sustituye por la IP real del LB (en este entorno: 35.190.117.209)
export LB="https://livemenu.duckdns.org"   # o https://35.190.117.209 con -k

# 1. SQL Injection
curl -i "$LB/api/v1/menu/test'%20OR%201=1--"
# Esperado: HTTP/1.1 403 Forbidden

# 2. Cross-Site Scripting
curl -i "$LB/api/v1/menu/test?q=<script>alert(1)</script>"
# Esperado: HTTP/1.1 403 Forbidden

# 3. Path traversal
curl -i "$LB/api/v1/menu/../../etc/passwd"
# Esperado: HTTP/1.1 403 Forbidden

# 4. Rate limiting
for i in $(seq 1 150); do
  curl -s -o /dev/null -w "%{http_code}\n" "$LB/api/v1/menu/test"
done | sort | uniq -c
# Esperado: las primeras ~100 devuelven 200/404 y las restantes 429
```

### 5.3 Tráfico legítimo (debe seguir pasando)

```bash
curl -i "$LB/health"                         # 200
curl -i "$LB/api/v1/menu/restaurante-demo"   # 200 o 404 (no 403)
```

---

## 6. Monitoreo y observabilidad

### 6.1 Logs en Cloud Logging

```
resource.type="http_load_balancer"
jsonPayload.enforcedSecurityPolicy.name="livemenu-waf-policy"
jsonPayload.enforcedSecurityPolicy.outcome="DENY"
```

Vista directa: <https://console.cloud.google.com/logs/query>

### 6.2 Métricas (Cloud Monitoring)

| Métrica | Significado |
|---------|-------------|
| `loadbalancing.googleapis.com/https/request_count` (filtro `response_code=403`) | Volumen de bloqueos |
| `loadbalancing.googleapis.com/https/request_count` (filtro `response_code=429`) | Throttling activo |
| `networksecurity.googleapis.com/...rule_match_count` | Cuántas veces matcheó cada regla |

### 6.3 Alertas recomendadas

1. **Spike de 403**: > 50 bloqueos por minuto durante 5 min → notificar al equipo (posible ataque dirigido).
2. **Política removida**: si `securityPolicy` de `backend-backend` cambia a vacío → alerta crítica.
3. **Throttling sostenido**: > 20 req/min en 429 durante 10 min → analizar si subir el límite o si es ataque.

---

## 7. Política de tuning

- Cuando se añadan endpoints nuevos al backend, validar que las reglas OWASP no generen falsos positivos antes de pasar la regla a `deny-403`.
- Estrategia recomendada para reglas nuevas: empezar en `--action=preview`, observar matches en logs durante 7 días, y luego promover a `deny-403`.
- El rate limit de 100 req/min se calibró para el menú público (~10 sucursales × 10 escaneos/min en horas pico). Reevaluar trimestralmente.

---

## 8. Grupos de seguridad y least-privilege (refuerza el 15% del WAF)

### Service Accounts existentes (verificadas en consola IAM)

| SA | Rol(es) | Comentario |
|----|---------|------------|
| `livemenu-backend-sa@livemenu-project.iam.gserviceaccount.com` | `roles/cloudsql.client`, `roles/storage.objectCreator`, `roles/secretmanager.secretAccessor` | ✅ Least-privilege correcto |
| `livemenu-cicd-sa@livemenu-project.iam.gserviceaccount.com` | `roles/artifactregistry.writer` | ✅ Solo escribe imágenes |
| `403658009429-compute@developer.gserviceaccount.com` (default Compute SA) | `roles/editor` | ⚠️ **Permisos excedidos (11334/11338)** – ver acción correctiva |

### Acción correctiva (default Compute SA)

Cloud Run usa por defecto la SA `*-compute@developer` con rol `Editor` salvo que se indique otra. Como nuestros servicios sí están corriendo con `livemenu-backend-sa`, podemos retirar `Editor` del default sin romper nada:

```bash
gcloud projects remove-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:403658009429-compute@developer.gserviceaccount.com" \
  --role="roles/editor"
```

> **Validar primero** que ningún Cloud Build trigger ni servicio sigue usando esta SA.

---

## 9. Estado actual y hallazgos

| Componente | Estado | Acción |
|------------|--------|--------|
| Cloud Armor policy `livemenu-waf-policy` | ❌ No existe | Aplicar `scripts/p4-apply-waf.sh` |
| Asociación a `backend-backend` | ❌ `Política de seguridad: Ninguna` | Idem |
| Asociación a `frontend-backend` | ❌ `Política de seguridad: Ninguna` | Idem |
| Logs de backend services | ❌ Inhabilitados | Habilitados como parte del script |
| Vulnerability Scanning Artifact Registry | ❌ Inhabilitado | (Opcional P3) `gcloud artifacts settings enable-upgrade-redirection` y activar Container Analysis API |
| Rol `Editor` en default Compute SA | ⚠️ Activo | Remover (sección 8) |

### Hallazgos cross-team (**comunicar al equipo**)

- **P1** – Cloud SQL `livemenu-db` tiene `availabilityType=ZONAL`. El wiki promete HA Regional. Requiere `gcloud sql instances patch livemenu-db --availability-type=REGIONAL` (provoca downtime de ~5 min y duplica costo).
- **P2** – Cloud SQL acepta conexiones sin TLS (`requireSsl=false`, `sslMode=ALLOW_UNENCRYPTED_AND_ENCRYPTED`). Romperá el criterio de "cifrado en tránsito 100%". Aplicar `--ssl-mode=ENCRYPTED_ONLY` y validar que Cloud Run sigue conectando vía Cloud SQL Auth Proxy (que usa TLS internamente).

---

## 10. Rollback de emergencia

Si Cloud Armor bloquea tráfico legítimo durante la sustentación:

```bash
# Quitar la política sin destruirla (puede reenchufarse después)
gcloud compute backend-services update backend-backend \
  --security-policy="" --global
gcloud compute backend-services update frontend-backend \
  --security-policy="" --global
```

Para destruirla por completo:

```bash
gcloud compute security-policies delete livemenu-waf-policy --quiet
```
