output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data for the cluster"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "acm_certificate_arn" {
  description = "ACM certificate ARN for TLS termination"
  value       = aws_acm_certificate.main.arn
}

output "ecr_repository_urls" {
  description = "ECR repository URLs for service images"
  value       = { for k, v in aws_ecr_repository.services : k => v.repository_url }
}

output "region" {
  description = "AWS region"
  value       = var.region
}

output "account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "route53_zone_id" {
  description = "Route 53 hosted zone ID"
  value       = data.aws_route53_zone.main.zone_id
}

output "aws_lb_controller_role_arn" {
  description = "IAM role ARN for AWS Load Balancer Controller"
  value       = module.aws_lb_controller_irsa.iam_role_arn
}
