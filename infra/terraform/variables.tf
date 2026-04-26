variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "livemenu-project"
}

variable "region" {
  description = "GCP region principal"
  type        = string
  default     = "us-central1"
}

variable "gcs_bucket_name" {
  description = "Bucket de imagenes de LiveMenu (se asume existente)"
  type        = string
  default     = "livemenu-images-prod"
}

variable "sql_instance_name" {
  description = "Nombre de la instancia Cloud SQL (se asume existente)"
  type        = string
  default     = "livemenu-db"
}

variable "lb_backend_api" {
  description = "Backend service del LB que sirve /api/*"
  type        = string
  default     = "backend-backend"
}

variable "lb_backend_frontend" {
  description = "Backend service del LB que sirve el frontend"
  type        = string
  default     = "frontend-backend"
}

variable "waf_rate_limit_rpm" {
  description = "Requests por minuto permitidos por IP en /api/*"
  type        = number
  default     = 100
}

variable "waf_rate_limit_path_prefix" {
  description = "Prefijo de path al que aplica el rate limit"
  type        = string
  default     = "/api/"
}

variable "backup_retention_count" {
  description = "Cantidad de backups automaticos a retener en Cloud SQL"
  type        = number
  default     = 15
}

variable "backup_start_time_utc" {
  description = "Hora de inicio del backup automatico (HH:MM en UTC)"
  type        = string
  default     = "08:00" # 03:00 UTC-5
}

variable "tx_log_retention_days" {
  description = "Retencion del transaction log para PITR"
  type        = number
  default     = 7
}

variable "lifecycle_noncurrent_age_days" {
  description = "Edad en dias para borrar versiones no actuales del bucket"
  type        = number
  default     = 30
}

variable "remove_default_compute_sa_editor" {
  description = "Si true, retira el rol Editor de la Compute default SA"
  type        = bool
  default     = false
}

variable "default_compute_sa_member" {
  description = "Member de la Compute default SA (project-number@developer.gserviceaccount.com)"
  type        = string
  default     = "serviceAccount:403658009429-compute@developer.gserviceaccount.com"
}

variable "enable_geo_filtering" {
  description = "Si true, agrega regla de bloqueo por pais"
  type        = bool
  default     = false
}

variable "geo_block_regions" {
  description = "Lista de codigos ISO-3166 a bloquear si enable_geo_filtering=true"
  type        = list(string)
  default     = ["CN", "RU", "KP"]
}
