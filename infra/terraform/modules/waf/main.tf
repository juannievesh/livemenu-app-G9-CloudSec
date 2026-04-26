locals {
  owasp_rules = {
    1000 = { expr = "sqli-v33-stable",            desc = "OWASP: SQL Injection" }
    1001 = { expr = "xss-v33-stable",             desc = "OWASP: Cross-Site Scripting" }
    1002 = { expr = "lfi-v33-stable",             desc = "OWASP: Local File Inclusion" }
    1003 = { expr = "rfi-v33-stable",             desc = "OWASP: Remote File Inclusion" }
    1004 = { expr = "rce-v33-stable",             desc = "OWASP: Remote Code Execution" }
    1005 = { expr = "scannerdetection-v33-stable", desc = "Scanner Detection" }
    1006 = { expr = "protocolattack-v33-stable",  desc = "Protocol Attack" }
    1007 = { expr = "sessionfixation-v33-stable", desc = "Session Fixation" }
  }
}

resource "google_compute_security_policy" "this" {
  name        = var.policy_name
  description = "LiveMenu WAF - OWASP Top 10 + Rate Limiting"
  type        = "CLOUD_ARMOR"

  # Reglas OWASP CRS v3.3
  dynamic "rule" {
    for_each = local.owasp_rules
    content {
      action      = "deny(403)"
      priority    = rule.key
      description = rule.value.desc
      match {
        expr {
          expression = "evaluatePreconfiguredExpr('${rule.value.expr}')"
        }
      }
    }
  }

  # Rate limiting perimetral
  rule {
    action      = "throttle"
    priority    = 2000
    description = "Rate limit ${var.rate_limit_rpm} req/min por IP en ${var.rate_limit_path_prefix}*"
    match {
      expr {
        expression = "request.path.startsWith('${var.rate_limit_path_prefix}')"
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      rate_limit_threshold {
        count        = var.rate_limit_rpm
        interval_sec = 60
      }
    }
  }

  # Geo-filtering opcional
  dynamic "rule" {
    for_each = var.enable_geo_filtering ? [1] : []
    content {
      action      = "deny(403)"
      priority    = 3000
      description = "Geo block: ${join(",", var.geo_block_regions)}"
      match {
        expr {
          expression = join(" || ", [
            for r in var.geo_block_regions : "origin.region_code == '${r}'"
          ])
        }
      }
    }
  }

  # Default rule (obligatoria)
  rule {
    action      = "allow"
    priority    = 2147483647
    description = "Default allow"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
  }

  advanced_options_config {
    log_level = "VERBOSE"
  }
}

# ----------------------------------------------------------------------
# Asociar la policy a los backend services existentes
# ----------------------------------------------------------------------
# Nota: usamos null_resource + gcloud porque "google_compute_backend_service"
# como recurso entraria en conflicto con los backend services creados
# manualmente por P1. Esto es una asociacion idempotente "side-channel".

resource "null_resource" "attach_to_api" {
  triggers = {
    policy_id = google_compute_security_policy.this.id
    backend   = var.backend_service_api
  }
  provisioner "local-exec" {
    command = <<EOT
gcloud compute backend-services update ${var.backend_service_api} \
  --security-policy=${google_compute_security_policy.this.name} \
  --global \
  --quiet
gcloud compute backend-services update ${var.backend_service_api} \
  --enable-logging --logging-sample-rate=1.0 --global --quiet
EOT
  }
}

resource "null_resource" "attach_to_frontend" {
  triggers = {
    policy_id = google_compute_security_policy.this.id
    backend   = var.backend_service_frontend
  }
  provisioner "local-exec" {
    command = <<EOT
gcloud compute backend-services update ${var.backend_service_frontend} \
  --security-policy=${google_compute_security_policy.this.name} \
  --global \
  --quiet
gcloud compute backend-services update ${var.backend_service_frontend} \
  --enable-logging --logging-sample-rate=1.0 --global --quiet
EOT
  }
}
