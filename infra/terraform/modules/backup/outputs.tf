output "bucket_versioning" {
  value      = "Enabled (gestionado por null_resource)"
  depends_on = [null_resource.gcs_versioning_lifecycle]
}

output "lifecycle_rules" {
  value = {
    delete_noncurrent_after_days   = var.lifecycle_noncurrent_age_days
    abort_multipart_after_days     = var.abort_multipart_after_days
  }
  depends_on = [null_resource.gcs_versioning_lifecycle]
}

output "sql_backup_configuration" {
  value = {
    start_time_utc          = var.backup_start_time_utc
    retention_count         = var.backup_retention_count
    pitr_enabled            = true
    tx_log_retention_days   = var.tx_log_retention_days
  }
  depends_on = [null_resource.sql_backup_patch]
}
