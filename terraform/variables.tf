variable "project" {
  description = "Project name used for resource naming and tagging"
  type        = string
  default     = "vedmich-gatewaydemo"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "domain" {
  description = "Domain for the demo (ACM certificate + Route 53)"
  type        = string
  default     = "gateway-demo.vedmich.dev"
}

variable "route53_zone_name" {
  description = "Route 53 hosted zone name"
  type        = string
  default     = "vedmich.dev"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "cluster_version" {
  description = "EKS cluster Kubernetes version"
  type        = string
  default     = "1.32"
}
