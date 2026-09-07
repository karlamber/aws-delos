terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
      configuration_aliases = [aws.hub]
    }
  }
  required_version = "~>1.9.8"
}

