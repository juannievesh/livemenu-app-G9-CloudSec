# LiveMenu – Infraestructura como Código (Terraform)

> **Responsable:** Persona 4 – WAF + Backup + Resiliencia + IaC
> **Estado:** Documental / parcialmente desplegado.
>
> La infraestructura productiva fue inicialmente provisionada de forma
> manual por **P1 / P2** (Cloud Run, Cloud SQL, Load Balancer, Secret
> Manager). Este módulo Terraform:
>
> 1. **Documenta** toda la arquitectura como código (cumple el bonus de IaC del enunciado).
> 2. **Gestiona desde cero** los recursos que añade P4: Cloud Armor, lifecycle de GCS y los IAM bindings de mínimo privilegio.
> 3. **Referencia** los recursos pre-existentes mediante `data` sources (no los recrea).

## Estructura

```
infra/terraform/
├── README.md                  ← este archivo
├── main.tf                    ← provider + recursos P4 + data sources
├── variables.tf               ← variables de entrada
├── outputs.tf                 ← outputs útiles para CI/CD
├── terraform.tfvars.example   ← plantilla (NO commitear el .tfvars real)
└── modules/
    ├── waf/                   ← Cloud Armor policy (auto-contenida)
    └── backup/                ← Versionado GCS + lifecycle
```

## Pre-requisitos

- Terraform >= 1.6
- Cuenta GCP con permisos `roles/owner` o equivalente sobre `livemenu-project`
- Variable de entorno `GOOGLE_APPLICATION_CREDENTIALS` o `gcloud auth application-default login` ejecutado.

## Uso

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
# editar terraform.tfvars con tus valores

terraform init
terraform plan   -out=plan.out
terraform apply  plan.out
```

Para revertir solo el WAF:

```bash
terraform destroy -target=module.waf
```

## Importación de recursos pre-existentes (opcional)

Si en el futuro se quiere migrar TODA la infra a Terraform (no solo lo de P4), se importan así:

```bash
terraform import google_sql_database_instance.livemenu_db livemenu-project/livemenu-db
terraform import google_cloud_run_v2_service.backend  projects/livemenu-project/locations/us-central1/services/livemenu-backend
terraform import google_cloud_run_v2_service.frontend projects/livemenu-project/locations/us-central1/services/livemenu-frontend
terraform import google_compute_backend_service.backend_api   projects/livemenu-project/global/backendServices/backend-backend
terraform import google_compute_backend_service.backend_front projects/livemenu-project/global/backendServices/frontend-backend
terraform import google_compute_url_map.livemenu_map projects/livemenu-project/global/urlMaps/livemenu-map
```

Luego se rellenan los recursos en `main.tf` con los valores reales y se valida que el `terraform plan` salga vacío.

## Estado remoto (recomendado para producción)

Por defecto se usa state local (`terraform.tfstate`). Para producción se debería migrar a un bucket GCS:

```hcl
terraform {
  backend "gcs" {
    bucket = "livemenu-tfstate"
    prefix = "infra/main"
  }
}
```

## Notas de seguridad

- `terraform.tfvars` está en `.gitignore`. Nunca commitearlo.
- Los secretos sensibles (passwords, JWT keys) se escriben directamente en Secret Manager desde Terraform usando recursos `google_secret_manager_secret_version`, pero su valor **viene de variables marcadas `sensitive = true`**. Considerar usar `terraform.tfvars.json` cifrado con `sops` o pasar los valores con `-var` desde CI.
