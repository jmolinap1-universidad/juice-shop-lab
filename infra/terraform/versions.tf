# Fase 2 – Arquitectura AWS de referencia para el entorno ENDURECIDO de Juice Shop.
# Estado: Propuesto. Validado con `terraform validate`, `terraform plan` (sin credenciales,
# modo offline) y Checkov. No se aplica (`apply`) sin aprobación de costos del equipo (D-05).
terraform {
  required_version = ">= 1.9.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.region

  # Permite `terraform plan` sin credenciales reales (evidencia de Fase 2). Con credenciales
  # del equipo, establecer offline_plan = false.
  skip_credentials_validation = var.offline_plan
  skip_requesting_account_id  = var.offline_plan
  skip_metadata_api_check     = var.offline_plan
  access_key                  = var.offline_plan ? "mock_access_key" : null
  secret_key                  = var.offline_plan ? "mock_secret_key" : null

  default_tags {
    tags = {
      Project     = "juice-shop-lab"
      Environment = "hardened"
      Owner       = "MASI-UMG-2026"
      ManagedBy   = "terraform"
    }
  }
}
