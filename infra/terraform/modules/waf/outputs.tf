output "policy_name" {
  value = google_compute_security_policy.this.name
}

output "policy_self_link" {
  value = google_compute_security_policy.this.self_link
}

output "attached_to_api" {
  value = "Asociado a ${var.backend_service_api}"
  depends_on = [null_resource.attach_to_api]
}

output "attached_to_frontend" {
  value = "Asociado a ${var.backend_service_frontend}"
  depends_on = [null_resource.attach_to_frontend]
}
