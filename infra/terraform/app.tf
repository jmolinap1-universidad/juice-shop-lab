# Cómputo: ECR + ECS Fargate en subredes privadas detrás de ALB con TLS 1.3.

resource "aws_ecr_repository" "app" {
  name                 = var.name
  image_tag_mutability = "IMMUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.main.arn
  }
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/${var.name}/app"
  retention_in_days = 365
  kms_key_id        = aws_kms_key.main.arn
}

resource "aws_ecs_cluster" "this" {
  name = var.name
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "app" {
  #checkov:skip=CKV_AWS_336:Juice Shop escribe la BD SQLite y logs en su árbol de trabajo al iniciar; mitigado con usuario no root, drop ALL y FS de solo lectura en el compose endurecido local (Fase 5).
  family                   = var.name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([{
    name                   = "juice-shop"
    image                  = var.image
    essential              = true
    readonlyRootFilesystem = false # Juice Shop escribe en data/ y logs/ (ver docs/fase-5)
    user                   = "65532"
    privileged             = false
    linuxParameters        = { capabilities = { drop = ["ALL"] }, initProcessEnabled = true }
    portMappings           = [{ containerPort = 3000, protocol = "tcp" }]
    environment            = [{ name = "NODE_ENV", value = "production" }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.app.name
        awslogs-region        = var.region
        awslogs-stream-prefix = "app"
      }
    }
  }])
}

resource "aws_ecs_service" "app" {
  name            = var.name
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "juice-shop"
    container_port   = 3000
  }
}

# --- Logs de acceso del ALB en S3 cifrado, versionado y sin acceso público ---
resource "aws_s3_bucket" "logs" {
  # Riesgos aceptados (ISO/IEC 27005), documentados en docs/fase-2:
  #checkov:skip=CKV_AWS_145:Los access logs de ALB solo admiten SSE-S3 (AES-256); SSE-KMS no es compatible.
  #checkov:skip=CKV_AWS_18:Bucket destino de logs; registrar su acceso en sí mismo crea bucles. Se cubre con CloudTrail data events.
  #checkov:skip=CKV_AWS_144:Replicación entre regiones fuera de presupuesto del laboratorio (D-05).
  #checkov:skip=CKV2_AWS_62:Sin consumidor de eventos; la ingesta al SIEM se hace por lectura programada.
  bucket = "${var.name}-alb-logs-${var.account_id}"
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Los logs de ALB solo admiten SSE-S3 (AES-256) como cifrado del bucket destino.
resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id
  rule {
    id     = "retencion"
    status = "Enabled"
    filter {}
    expiration {
      days = 365
    }
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

resource "aws_s3_bucket_policy" "logs" {
  bucket = aws_s3_bucket.logs.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "ElbLogDelivery"
        Effect    = "Allow"
        Principal = { Service = "logdelivery.elasticloadbalancing.amazonaws.com" }
        Action    = "s3:PutObject"
        Resource  = "${aws_s3_bucket.logs.arn}/alb/*"
      },
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [aws_s3_bucket.logs.arn, "${aws_s3_bucket.logs.arn}/*"]
        Condition = { Bool = { "aws:SecureTransport" = "false" } }
      }
    ]
  })
}

resource "aws_lb" "this" {
  name                       = var.name
  load_balancer_type         = "application"
  internal                   = false
  subnets                    = aws_subnet.public[*].id
  security_groups            = [aws_security_group.alb.id]
  drop_invalid_header_fields = true
  enable_deletion_protection = true

  access_logs {
    bucket  = aws_s3_bucket.logs.id
    prefix  = "alb"
    enabled = true
  }
}

resource "aws_lb_target_group" "app" {
  name        = var.name
  port        = 3000
  protocol    = "HTTP" # tráfico interno VPC; TLS termina en el ALB
  target_type = "ip"
  vpc_id      = aws_vpc.this.id
  health_check {
    path    = "/rest/admin/application-version"
    matcher = "200"
  }
}

# Solo HTTPS con política TLS 1.3 (sin listener HTTP).
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-3-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
