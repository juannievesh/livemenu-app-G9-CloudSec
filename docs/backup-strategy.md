# LiveMenu – Estrategia de Backup, Versionado y Resiliencia

> **Responsable:** Persona 4 – WAF + Backup + Resiliencia + IaC
> **Criterio evaluado:** Estrategia de Backup (5%)
> **Documento complementario:** [`rpo-rto.md`](rpo-rto.md) (definición formal de RPO/RTO)

---

## 1. Resumen ejecutivo

| Recurso | Mecanismo | Frecuencia | Retención | Estado actual |
|---------|-----------|------------|-----------|---------------|
| Cloud SQL `livemenu-db` | Backups automáticos + PITR (transaction log) | Diario 03:00 UTC-5 | 15 backups + 7 días de tx-log | ❌ **Inhabilitado** |
| GCS `livemenu-images-prod` | Object Versioning | Continuo | 30 días para versiones no actuales | ❌ No configurado |
| GCS `livemenu-images-prod` | Lifecycle (limpieza) | Diario | Borra versiones >30 días | ❌ No configurado |
| Imágenes Docker | Artifact Registry | Por release | Indefinida | ✅ Activo |
| Código fuente | Git / GitHub | Continuo | Indefinida | ✅ Activo |
| Secret Manager | Versionado nativo + rotación 40 d | Continuo | Indefinida (versiones disabled tras rotación) | ✅ Activo (P2) |

> El estado "❌" indica que la configuración descrita en este documento aún **no está aplicada en GCP**; debe ejecutarse el script [`scripts/p4-apply-backup.sh`](../scripts/p4-apply-backup.sh).

---

## 2. Cloud SQL – Backups automáticos

### 2.1 Política

| Parámetro | Valor objetivo | Justificación |
|-----------|---------------|---------------|
| Backups automáticos | `enabled=true` | Requisito mínimo de la entrega |
| Hora de inicio | `03:00` UTC-5 (08:00 UTC) | Hora de mínimo tráfico (ventana fuera del horario de almuerzo y cena) |
| Retención (count) | `15` backups | El enunciado pide ≥15 días |
| Point-in-Time Recovery | `enabled=true` | Permite restaurar a cualquier segundo de los últimos 7 días |
| Retención del transaction log | `7` días | Equilibrio costo / RPO granular |
| Ubicación | `us` (multi-region) | Recuperación posible incluso si `us-central1` cae |

### 2.2 Aplicación con `gcloud`

```bash
gcloud sql instances patch livemenu-db \
  --backup-start-time=08:00 \
  --backup-location=us \
  --retained-backups-count=15 \
  --enable-point-in-time-recovery \
  --retained-transaction-log-days=7
```

### 2.3 Verificación

```bash
gcloud sql instances describe livemenu-db \
  --format="yaml(settings.backupConfiguration)"
```

Salida esperada (resumida):

```yaml
settings:
  backupConfiguration:
    backupRetentionSettings:
      retainedBackups: 15
      retentionUnit: COUNT
    enabled: true
    location: us
    pointInTimeRecoveryEnabled: true
    startTime: "08:00"
    transactionLogRetentionDays: 7
```

### 2.4 Procedimiento de restore

#### A. Restore completo desde backup automático

```bash
# 1. Listar backups disponibles
gcloud sql backups list --instance=livemenu-db

# 2. Restaurar a una nueva instancia (NUNCA sobre la productiva)
gcloud sql backups restore <BACKUP_ID> \
  --restore-instance=livemenu-db-restore \
  --backup-instance=livemenu-db

# 3. Verificar datos en livemenu-db-restore
# 4. (Si OK) cambiar nombres / actualizar secret livemenu-db-url
# 5. Reiniciar Cloud Run para que recargue el secret
gcloud run services update livemenu-backend --region=us-central1 \
  --update-env-vars=RESTART=$(date +%s)
```

#### B. Point-in-Time Recovery (PITR) – ej. recuperar el estado de hace 2 horas

```bash
TS=$(date -u -d '2 hours ago' +"%Y-%m-%dT%H:%M:%S.000Z")
gcloud sql instances clone livemenu-db livemenu-db-pitr \
  --point-in-time="$TS"
```

### 2.5 Tiempos esperados

| Operación | Tiempo típico | Cumple RTO 30 min |
|-----------|---------------|-------------------|
| Restore desde backup | 10–20 min | ✅ |
| Clone PITR | 5–15 min | ✅ |
| Promoción a productiva (rename + update secret + restart Cloud Run) | 5 min | ✅ |

---

## 3. Cloud Storage – Object Versioning + Lifecycle

### 3.1 Política

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| Bucket | `livemenu-images-prod` | Único bucket con datos de usuario |
| Versionado | `on` | Protege contra borrado/sobre-escritura accidental |
| Lifecycle: borrar versiones no actuales | `> 30 días` | Equilibrio costo vs ventana de recuperación |
| Lifecycle: borrar `multipart` incompletos | `> 7 días` | Higiene de costos |

### 3.2 Aplicación

```bash
# Versionado
gsutil versioning set on gs://livemenu-images-prod

# Lifecycle (ver scripts/gcs-lifecycle.json)
gsutil lifecycle set scripts/gcs-lifecycle.json gs://livemenu-images-prod
```

### 3.3 Verificación

```bash
gsutil versioning get gs://livemenu-images-prod
# → gs://livemenu-images-prod: Enabled

gsutil lifecycle get gs://livemenu-images-prod
# → JSON con las 2 reglas
```

### 3.4 Procedimiento de restore – objeto borrado/corrompido

```bash
# 1. Listar todas las versiones de un objeto específico
gsutil ls -a gs://livemenu-images-prod/dishes/<dish-id>/large.webp

# 2. Restaurar la versión deseada (copia sobre la actual)
gsutil cp \
  gs://livemenu-images-prod/dishes/<dish-id>/large.webp#<GENERATION> \
  gs://livemenu-images-prod/dishes/<dish-id>/large.webp
```

### 3.5 Restauración masiva (ej. tras eliminación accidental de un prefijo)

```bash
# Listar versiones tombstone del último día
gsutil ls -al -p livemenu-project gs://livemenu-images-prod/dishes/** | \
  grep "$(date -u -d 'yesterday' +%Y-%m-%d)"

# Restaurar usando script auxiliar (recorrer cada uno)
# – ver scripts/restore-gcs-prefix.sh (a generar bajo demanda)
```

---

## 4. Backup de configuración / Infraestructura

| Recurso | Estrategia | Comando de verificación |
|---------|------------|-------------------------|
| Configuración de Cloud Armor | Versionado vía IaC (Terraform en `infra/terraform/`) | `gcloud compute security-policies export livemenu-waf-policy --file-name=- --file-format=yaml` |
| Manifiestos Cloud Run | En el repo (`deploy/`) y en Cloud Build history | `gcloud run revisions list --service=livemenu-backend` |
| Secretos | Versionado nativo de Secret Manager + topic `livemenu-secret-rotate` para Pub/Sub | `gcloud secrets versions list livemenu-db-url` |
| Imágenes Docker | Artifact Registry conserva todas las imágenes pusheadas | `gcloud artifacts docker images list us-central1-docker.pkg.dev/livemenu-project/livemenu-repo` |

---

## 5. Resiliencia regional (riesgos y mitigaciones)

| Componente | Single point of failure | Mitigación actual | Mitigación recomendada |
|-----------|------------------------|-------------------|------------------------|
| Cloud SQL | Sí (`ZONAL`) | Backup diario | **Pasar a HA Regional** (`--availability-type=REGIONAL`). Ya escalado al equipo P1. |
| Cloud Run | No (auto multi-zonal por región) | Default | OK |
| Load Balancer (Classic) | No (global anycast) | Default | Migrar a "Global External Application LB" para Cloud Armor edge security |
| GCS bucket | No (multi-region `us`) | Default | OK |
| Secret Manager | No (replicación automática) | Default | OK |

---

## 6. Checklist operativo

### Diario (automatizado)

- [ ] Backup Cloud SQL ejecutado correctamente (alerta si `latestBackupRunStatus != SUCCESSFUL`).
- [ ] Sin errores 5xx > 1% en Cloud Run (Cloud Monitoring uptime check).

### Semanal (manual, persona 4)

- [ ] Verificar tamaño del bucket `livemenu-images-prod` y que el lifecycle está borrando versiones antiguas (`gsutil du -sh gs://livemenu-images-prod`).
- [ ] Probar un restore de prueba a una instancia desechable (1 vez al mes mínimo).
- [ ] Revisar el log del topic `livemenu-secret-rotate` para confirmar que las rotaciones de la semana fueron exitosas.

### Mensual

- [ ] Drill completo de DR: restaurar Cloud SQL desde backup a instancia separada y validar integridad con `pg_dump | wc -l` comparado con producción.
- [ ] Auditar IAM (`gcloud projects get-iam-policy livemenu-project --format=yaml > iam-snapshot-$(date +%Y%m%d).yaml`).

---

## 7. Alertas (Cloud Monitoring)

```yaml
# Pseudo-config – instrumentar con Terraform o consola
- displayName: "Cloud SQL backup failed"
  conditions:
    - filter: 'resource.type="cloudsql_database" AND metric.type="cloudsql.googleapis.com/database/backup/last_status"'
      comparison: COMPARISON_LT
      thresholdValue: 1
      duration: 600s
  notificationChannels: ["livemenu-team-email"]

- displayName: "GCS bucket size > 50 GB"
  conditions:
    - filter: 'resource.type="gcs_bucket" AND metric.type="storage.googleapis.com/storage/total_bytes"'
      comparison: COMPARISON_GT
      thresholdValue: 53687091200
```

---

## 8. Hallazgos abiertos (a coordinar con el equipo)

| Hallazgo | Owner | Impacto en nota | Acción |
|----------|-------|-----------------|--------|
| Cloud SQL `availabilityType=ZONAL` | P1 | Despliegue (-3pts), Backup (-1pt) | `gcloud sql instances patch livemenu-db --availability-type=REGIONAL` |
| Cloud SQL acepta conexiones sin TLS | P2 | Cifrado en tránsito (-3pts) | `gcloud sql instances patch livemenu-db --ssl-mode=ENCRYPTED_ONLY` |
| Bucket `livemenu-images-prod` con acceso público | P1/P2 | Cifrado / IAM | Confirmar si las imágenes deben servirse vía LB con CDN en lugar de URL pública |
| Default Compute SA con rol `Editor` | P4 (incluido en este doc, sección 8 de `waf-config.md`) | IAM least-privilege | Remover binding |

---

## 9. Cumplimiento del rúbrica

| Criterio del enunciado | Cumplimiento |
|------------------------|--------------|
| Backups automáticos diarios | ✅ Sección 2.1 |
| Retención mínima 15 días | ✅ `retainedBackups=15` |
| Versionamiento de Object Storage | ✅ Sección 3.1 |
| Documentación de RPO/RTO | ✅ Documento separado [`rpo-rto.md`](rpo-rto.md) |
| Procedimiento de restore documentado | ✅ Secciones 2.4 y 3.4 |
