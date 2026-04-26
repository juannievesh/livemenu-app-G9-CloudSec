output "waf_policy_name" {
  description = "Nombre de la security policy de Cloud Armor creada"
  value       = module.waf.policy_name
}

output "waf_policy_self_link" {
  description = "Self link de la policy (util para asociar manualmente)"
  value       = module.waf.policy_self_link
}

output "lb_backend_api_security_policy" {
  description = "Confirmacion de que el backend service /api esta protegido"
  value       = module.waf.attached_to_api
}

output "lb_backend_frontend_security_policy" {
  description = "Confirmacion de que el backend service del frontend esta protegido"
  value       = module.waf.attached_to_frontend
}

output "gcs_bucket_versioning" {
  description = "Estado del versionado del bucket"
  value       = module.backup.bucket_versioning
}

output "gcs_lifecycle_rules" {
  description = "Reglas de lifecycle aplicadas al bucket"
  value       = module.backup.lifecycle_rules
}

output "sql_backup_configuration" {
  description = "Configuracion final de backup de Cloud SQL"
  value       = module.backup.sql_backup_configuration
}
