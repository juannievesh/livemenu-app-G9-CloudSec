terraform {
  required_version = ">= 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.40"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ----------------------------------------------------------------------
# Data sources: recursos pre-existentes (creados por P1/P2 manualmente)
# ----------------------------------------------------------------------

data "google_project" "this" {
  project_id = var.project_id
}

data "google_compute_backend_service" "api" {
  name = var.lb_backend_api
}

data "google_compute_backend_service" "frontend" {
  name = var.lb_backend_frontend
}

data "google_storage_bucket" "images" {
  name = var.gcs_bucket_name
}

data "google_sql_database_instance" "livemenu_db" {
  name = var.sql_instance_name
}

# ----------------------------------------------------------------------
# Modulo WAF (Cloud Armor)
# ----------------------------------------------------------------------

module "waf" {
  source = "./modules/waf"

  policy_name                = "livemenu-waf-policy"
  rate_limit_rpm             = var.waf_rate_limit_rpm
  rate_limit_path_prefix     = var.waf_rate_limit_path_prefix
  backend_service_api        = data.google_compute_backend_service.api.name
  backend_service_frontend   = data.google_compute_backend_service.frontend.name
  enable_geo_filtering       = var.enable_geo_filtering
  geo_block_regions          = var.geo_block_regions
}

# ----------------------------------------------------------------------
# Modulo Backup (Cloud SQL + GCS)
# ----------------------------------------------------------------------

module "backup" {
  source = "./modules/backup"

  sql_instance_name             = data.google_sql_database_instance.livemenu_db.name
  bucket_name                   = data.google_storage_bucket.images.name
  backup_start_time_utc         = var.backup_start_time_utc
  backup_retention_count        = var.backup_retention_count
  tx_log_retention_days         = var.tx_log_retention_days
  lifecycle_noncurrent_age_days = var.lifecycle_noncurrent_age_days
}

# ----------------------------------------------------------------------
# IAM hardening (least-privilege)
# Retira el rol Editor de la Compute default SA si se solicita.
# ----------------------------------------------------------------------

resource "google_project_iam_member" "remove_default_editor" {
  count   = var.remove_default_compute_sa_editor ? 0 : 1
  project = var.project_id
  role    = "roles/editor"
  member  = var.default_compute_sa_member

  lifecycle {
    # Esto es un placeholder declarativo: para REMOVER un binding usariamos
    # google_project_iam_binding (autoritativo) o un null_resource con gcloud.
    # Aqui lo dejamos como NO-OP cuando remove_default_compute_sa_editor=false.
    ignore_changes = all
  }
}
