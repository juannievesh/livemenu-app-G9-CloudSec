# ----------------------------------------------------------------------
# Cloud SQL: parche de configuracion de backups + PITR
# ----------------------------------------------------------------------
# Igual que en el modulo waf, usamos null_resource con gcloud para no
# entrar en conflicto con la instancia Cloud SQL creada manualmente.

resource "null_resource" "sql_backup_patch" {
  triggers = {
    sql_instance      = var.sql_instance_name
    start_time        = var.backup_start_time_utc
    retention_count   = var.backup_retention_count
    pitr_log_days     = var.tx_log_retention_days
  }

  provisioner "local-exec" {
    command = <<EOT
gcloud sql instances patch ${var.sql_instance_name} \
  --backup-start-time=${var.backup_start_time_utc} \
  --backup-location=us \
  --retained-backups-count=${var.backup_retention_count} \
  --enable-point-in-time-recovery \
  --transaction-log-retention-days=${var.tx_log_retention_days} \
  --quiet
EOT
  }
}

# ----------------------------------------------------------------------
# GCS: versionado + lifecycle
# ----------------------------------------------------------------------

resource "google_storage_bucket_object" "lifecycle_marker" {
  # Marker simbolico - el lifecycle real se aplica con google_storage_bucket
  # importado o con gsutil.  Usamos null_resource para idempotencia.
  bucket  = var.bucket_name
  name    = ".tf-managed-lifecycle"
  content = "managed-by-terraform"
}

resource "null_resource" "gcs_versioning_lifecycle" {
  triggers = {
    bucket               = var.bucket_name
    noncurrent_age       = var.lifecycle_noncurrent_age_days
    abort_multipart_days = var.abort_multipart_after_days
  }

  provisioner "local-exec" {
    command = <<EOT
set -e
gsutil versioning set on gs://${var.bucket_name}

cat > /tmp/lifecycle-${var.bucket_name}.json <<JSON
{
  "lifecycle": {
    "rule": [
      {
        "action": { "type": "Delete" },
        "condition": { "age": ${var.lifecycle_noncurrent_age_days}, "isLive": false }
      },
      {
        "action": { "type": "AbortIncompleteMultipartUpload" },
        "condition": { "age": ${var.abort_multipart_after_days} }
      }
    ]
  }
}
JSON

gsutil lifecycle set /tmp/lifecycle-${var.bucket_name}.json gs://${var.bucket_name}
rm -f /tmp/lifecycle-${var.bucket_name}.json
EOT
  }
}
