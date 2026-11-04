output "alb_dns_name" {
  value = aws_lb.this.dns_name
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "waf_acl_arn" {
  value = aws_wafv2_web_acl.this.arn
}
