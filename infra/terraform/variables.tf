variable "region" {
  description = "Región AWS"
  type        = string
  default     = "us-east-1"
}

variable "offline_plan" {
  description = "true = plan sin credenciales (solo evidencia); false = credenciales reales"
  type        = bool
  default     = true
}

variable "account_id" {
  description = "ID de cuenta AWS (se usa en políticas KMS; ficticio en modo offline)"
  type        = string
  default     = "111111111111"
}

variable "name" {
  description = "Prefijo de nombres"
  type        = string
  default     = "juice-hardened"
}

variable "azs" {
  description = "Zonas de disponibilidad (dos, para alta disponibilidad)"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "vpc_cidr" {
  type    = string
  default = "10.40.0.0/16"
}

variable "allowed_cidrs" {
  description = "Rangos autorizados a acceder al ALB (acceso restringido, regla 1 de CLAUDE.md)"
  type        = list(string)
  default     = ["203.0.113.0/24"] # TEST-NET-3: reemplazar por la IP pública del equipo
}

variable "certificate_arn" {
  description = "ARN del certificado ACM para TLS"
  type        = string
  default     = "arn:aws:acm:us-east-1:111111111111:certificate/00000000-0000-0000-0000-000000000000"
}

variable "image" {
  description = "Imagen endurecida (ECR, por digest)"
  type        = string
  default     = "111111111111.dkr.ecr.us-east-1.amazonaws.com/juice-hardened@sha256:0000000000000000000000000000000000000000000000000000000000000000"
}
