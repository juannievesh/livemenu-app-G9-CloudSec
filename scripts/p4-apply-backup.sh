#!/usr/bin/env bash
#
# scripts/p4-apply-backup.sh
# ----------------------------------------------------------------------
# Activa la estrategia de backup descrita en docs/backup-strategy.md:
#  - Cloud SQL: backups diarios + PITR + retención 15
#  - GCS bucket livemenu-images-prod: versionado + lifecycle 30 dias
#
# Pensado para ejecutarse en Google Cloud Shell (proyecto livemenu-project).
# Idempotente.
#
# Uso:
#   bash scripts/p4-apply-backup.sh           # aplicar
#   bash scripts/p4-apply-backup.sh --dry-run # solo imprimir
# ----------------------------------------------------------------------

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-livemenu-project}"
SQL_INSTANCE="${SQL_INSTANCE:-livemenu-db}"
GCS_BUCKET="${GCS_BUCKET:-livemenu-images-prod}"
BACKUP_START_TIME_UTC="${BACKUP_START_TIME_UTC:-08:00}"   # 03:00 UTC-5
BACKUP_RETENTION="${BACKUP_RETENTION:-15}"
TX_LOG_RETENTION_DAYS="${TX_LOG_RETENTION_DAYS:-7}"

LIFECYCLE_FILE="$(dirname "$0")/gcs-lifecycle.json"

DRY=""
if [[ "${1:-}" == "--dry-run" ]]; then DRY="echo [DRY-RUN]"; fi

echo ">>> Proyecto activo: $PROJECT_ID"
$DRY gcloud config set project "$PROJECT_ID" >/dev/null

# ----------------------------------------------------------------------
# 1. Cloud SQL - backups + PITR
# ----------------------------------------------------------------------
echo ">>> Configurando backups en Cloud SQL '$SQL_INSTANCE' ..."
$DRY gcloud sql instances patch "$SQL_INSTANCE" \
  --backup-start-time="$BACKUP_START_TIME_UTC" \
  --backup-location="us" \
  --retained-backups-count="$BACKUP_RETENTION" \
  --enable-point-in-time-recovery \
  --transaction-log-retention-days="$TX_LOG_RETENTION_DAYS" \
  --quiet

echo ">>> Verificando configuracion ..."
$DRY gcloud sql instances describe "$SQL_INSTANCE" \
  --format="yaml(settings.backupConfiguration)"

# ----------------------------------------------------------------------
# 2. GCS - versionado + lifecycle
# ----------------------------------------------------------------------
echo ">>> Activando versioning en bucket '$GCS_BUCKET' ..."
$DRY gsutil versioning set on "gs://${GCS_BUCKET}"

echo ">>> Aplicando lifecycle desde '$LIFECYCLE_FILE' ..."
if [[ ! -f "$LIFECYCLE_FILE" ]]; then
  echo "ERROR: no se encontro $LIFECYCLE_FILE" >&2
  exit 1
fi
$DRY gsutil lifecycle set "$LIFECYCLE_FILE" "gs://${GCS_BUCKET}"

echo ">>> Verificando lifecycle ..."
$DRY gsutil lifecycle get "gs://${GCS_BUCKET}"

# ----------------------------------------------------------------------
# 3. Resumen
# ----------------------------------------------------------------------
echo ""
echo "============================================================"
echo "Backup + versionado aplicado."
echo ""
echo "Recordatorios pendientes (cross-team):"
echo "  - P1: pasar Cloud SQL a HA Regional"
echo "        gcloud sql instances patch $SQL_INSTANCE \\"
echo "          --availability-type=REGIONAL"
echo "  - P2: forzar TLS en la conexion a Cloud SQL"
echo "        gcloud sql instances patch $SQL_INSTANCE \\"
echo "          --ssl-mode=ENCRYPTED_ONLY"
echo "============================================================"
