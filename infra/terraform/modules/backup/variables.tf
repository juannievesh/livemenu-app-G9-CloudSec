variable "sql_instance_name" {
  type        = string
  description = "Nombre de la instancia Cloud SQL"
}

variable "bucket_name" {
  type        = string
  description = "Nombre del bucket de imagenes"
}

variable "backup_start_time_utc" {
  type    = string
  default = "08:00"
}

variable "backup_retention_count" {
  type    = number
  default = 15
}

variable "tx_log_retention_days" {
  type    = number
  default = 7
}

variable "lifecycle_noncurrent_age_days" {
  type    = number
  default = 30
}

variable "abort_multipart_after_days" {
  type    = number
  default = 7
}
