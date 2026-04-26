variable "policy_name" {
  type        = string
  description = "Nombre de la security policy"
}

variable "rate_limit_rpm" {
  type        = number
  description = "Requests por minuto permitidos por IP en /api/*"
}

variable "rate_limit_path_prefix" {
  type        = string
  description = "Prefijo de path al que aplica el rate limit"
}

variable "backend_service_api" {
  type        = string
  description = "Nombre del backend service que sirve /api/*"
}

variable "backend_service_frontend" {
  type        = string
  description = "Nombre del backend service del frontend"
}

variable "enable_geo_filtering" {
  type    = bool
  default = false
}

variable "geo_block_regions" {
  type    = list(string)
  default = []
}
