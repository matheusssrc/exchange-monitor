variable "aws_region" {
  description = "AWS region for the deployment."
  type        = string
  default     = "sa-east-1"
}

variable "project_name" {
  description = "Prefix applied to resource names."
  type        = string
  default     = "trillia"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the public (ALB) subnets."
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for the private (ECS/RDS) subnets."
  type        = list(string)
  default     = ["10.20.11.0/24", "10.20.12.0/24"]
}

variable "availability_zones" {
  description = "Availability zones for the subnets."
  type        = list(string)
  default     = ["sa-east-1a", "sa-east-1c"]
}

variable "db_instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t3.micro"
}

variable "api_image" {
  description = "Container image for the API task (ECR URI)."
  type        = string
  default     = "trillia-backend:latest"
}

variable "frontend_image" {
  description = "Container image for the frontend task (ECR URI)."
  type        = string
  default     = "trillia-frontend:latest"
}

variable "api_desired_count" {
  description = "Number of API tasks behind the ALB."
  type        = number
  default     = 2
}
