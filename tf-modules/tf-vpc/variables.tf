# Common Variables
# The following variables are used in every module

variable "region" {
  description = "The AWS region where resources will be created."
  type        = string
}

variable "account_id" {
  description = "AWS account ID."
  type        = string
}

variable "env" {
  description = "Environment acronym"
  type = string
}

variable "landscape" {
  description = "Landscape name"
  type = string
}

variable "region_short" {
  description = "Shortened version of the AWS Region for naming resources"
}

# Module Specific Variables
# The following variables are required for specific resource values

variable "vpc_cidr" {
  description = "The CIDR block for the VPC (e.g., 10.0.0.0/20)."
  type        = string
}

# Define a boolean variable to control the creation
variable "create_internet_gateway" {
  description = "Should an internet gateway be created?"
  type        = bool
  default     = false
}

# Define a boolean variable to control the creation
variable "create_nat_gateways" {
  description = "Should an NAT gateways be created?"
  type        = bool
  default     = false
}

variable "retention_in_days" {
  description = "Number of days to retain log data"
  type = number
  default = 30
}

variable "availability_zone_ids" {
  description = "List of specific Availability Zone IDs to use for subnets. If not provided, will use the first two AZs in the region. Max 4 (CIDR layout: public 0-3, private 4-7, isolated 8-11 in /20)."
  type        = list(string)
  default     = null

  validation {
    condition     = var.availability_zone_ids == null || (length(var.availability_zone_ids) >= 1 && length(var.availability_zone_ids) <= 4)
    error_message = "availability_zone_ids must contain 1 to 4 AZs. A /20 only has space for 4 AZs with this module's subnet layout (public, private, isolated each need one /24 per AZ)."
  }
}

variable "create_ssm_vpc_endpoints" {
  description = "Create VPC interface endpoints for SSM (ssm, ec2messages, ssmmessages). Required for SSM Session Manager / port forwarding when the VPC has no Internet Gateway or NAT Gateways."
  type        = bool
  default     = false
}
