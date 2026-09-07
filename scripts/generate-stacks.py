#!/usr/bin/env python3
"""Generate plain-Terraform stack boilerplate for aws-delos."""

from __future__ import annotations

import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

COMMON_VARS = """\
variable "env" {
  type        = string
  description = "Environment acronym (dev, prod)."
}

variable "account_name" {
  type        = string
  description = "AWS account alias used in naming."
}

variable "account_id" {
  type        = string
  description = "AWS account ID."
}

variable "aws_profile" {
  type        = string
  description = "AWS CLI profile for provider and remote state."
}

variable "landscape" {
  type        = string
  description = "Landscape name (delos)."
}

variable "region" {
  type        = string
  description = "AWS region."
}

variable "region_short" {
  type        = string
  description = "Short region code for resource naming (e.g. ue1)."
}

variable "route53_account_id" {
  type        = string
  description = "Account ID that owns the Route53 hosted zone (mgmt)."
}

variable "dns_manager_role_arn" {
  type        = string
  description = "IAM role ARN to assume for Route53 DNS management."
}

variable "artifact_bucket" {
  type        = string
  description = "Shared S3 bucket for Lambda deployment packages."
}

variable "oidc_subjects" {
  type        = list(string)
  description = "GitHub OIDC subjects allowed to assume the deploy role."
}

variable "hosted_zone_name" {
  type        = string
  description = "Public DNS zone for Argus hostnames (e.g. fifty9.net)."
}
"""

VERSIONS = """\
terraform {
  required_version = "~> 1.14.0"

  backend "s3" {
    encrypt      = true
    use_lockfile = true
    # bucket, key, region, and profile are set in backend.hcl at init time.
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
"""

PROVIDERS = """\
provider "aws" {
  region              = var.region
  profile             = var.aws_profile
  allowed_account_ids = [var.account_id]

  default_tags {
    tags = {
      Landscape     = var.landscape
      Environment   = var.env
      ProvisionedBy = "Terraform"
    }
  }
}
"""

PROVIDERS_WITH_ROUTE53 = """\
provider "aws" {
  region              = var.region
  profile             = var.aws_profile
  allowed_account_ids = [var.account_id]

  default_tags {
    tags = {
      Landscape     = var.landscape
      Environment   = var.env
      ProvisionedBy = "Terraform"
    }
  }
}

provider "aws" {
  alias               = "route53"
  region              = "us-east-1"
  profile             = var.aws_profile
  allowed_account_ids = [var.route53_account_id]

  assume_role {
    role_arn = var.dns_manager_role_arn
  }

  default_tags {
    tags = {
      Landscape     = var.landscape
      Environment   = var.env
      ProvisionedBy = "Terraform"
    }
  }
}
"""

REMOTE_STATE_LOCALS = """\
locals {
  remote_state_bucket  = "s3-${var.landscape}-${var.env}-${var.region_short}-terraform-state"
  remote_state_region  = var.region
  remote_state_profile = var.aws_profile
}
"""

REMOTE_STATE_BLOCK = """\
data "terraform_remote_state" "{name}" {{
  backend = "s3"
  config = {{
    bucket  = local.remote_state_bucket
    key     = "live/${{var.env}}/us-east-1/{key}/terraform.tfstate"
    region  = local.remote_state_region
    profile = local.remote_state_profile
  }}
}}
"""


def write_stack(
    env: str,
    stack_key: str,
    *,
    main_body: str,
    outputs_body: str | None = None,
    remote_states: list[tuple[str, str]] | None = None,
    providers_body: str = PROVIDERS,
) -> None:
    """Write a stack under live/<env>/us-east-1/<stack_key>/."""
    stack_dir = REPO / "live" / env / "us-east-1" / stack_key
    stack_dir.mkdir(parents=True, exist_ok=True)

    (stack_dir / "versions.tf").write_text(VERSIONS)
    (stack_dir / "providers.tf").write_text(providers_body)
    (stack_dir / "variables.tf").write_text(COMMON_VARS)

    remote_states = remote_states or []
    remote_path = stack_dir / "remote_state.tf"
    if remote_states:
        remote_tf = [REMOTE_STATE_LOCALS]
        for name, key in remote_states:
            remote_tf.append(REMOTE_STATE_BLOCK.format(name=name, key=key))
        remote_path.write_text("\n".join(remote_tf) + "\n")
    elif remote_path.exists():
        remote_path.unlink()

    (stack_dir / "main.tf").write_text(textwrap.dedent(main_body).strip() + "\n")

    outputs_path = stack_dir / "outputs.tf"
    if outputs_body:
        outputs_path.write_text(textwrap.dedent(outputs_body).strip() + "\n")
    elif outputs_path.exists():
        outputs_path.unlink()

    (stack_dir / "backend.hcl").write_text(
        textwrap.dedent(
            f"""\
            bucket  = "s3-delos-{env}-ue1-terraform-state"
            key     = "live/{env}/us-east-1/{stack_key}/terraform.tfstate"
            region  = "us-east-1"
            profile = "aws-delos-{env}"
            """
        )
    )


def common_module_args() -> str:
    return """
  region       = var.region
  account_id   = var.account_id
  env          = var.env
  landscape    = var.landscape
  region_short = var.region_short
"""


def generate(env: str) -> None:
    write_stack(
        env,
        "cloudwatch_logging",
        main_body=f"""
module "cloudwatch_logging" {{
  source = "../../../../tf-modules/tf-cloudwatch"
{common_module_args().rstrip()}
}}
""",
        outputs_body="""
output "cloudwatch_logging_policy_arn" {
  description = "ARN of the shared CloudWatch logging policy (consumed by Lambda stacks)."
  value       = module.cloudwatch_logging.cloudwatch_logging_policy_arn
}
""",
    )

    # Separate /20 per env (dev 10.0.32.0/20, prod 10.0.80.0/20).
    vpc_cidrs = {
        "dev": ("10.0.32.0/20", "10.0.32.0/21"),
        "prod": ("10.0.80.0/20", "10.0.80.0/21"),
    }
    account_block, vpc_cidr = vpc_cidrs[env]

    write_stack(
        env,
        "vpc",
        main_body=f"""
module "vpc" {{
  source = "../../../../tf-modules/tf-vpc"
{common_module_args().rstrip()}

  availability_zone_ids   = ["use1-az1", "use1-az3"]
  # Account block {account_block} (us-east-1 VPC {vpc_cidr}).
  vpc_cidr                = "{vpc_cidr}"
  create_internet_gateway = false
  create_nat_gateways     = false
  retention_in_days       = 7
}}
""",
        outputs_body="""
output "private_subnet_ids" {
  value = module.vpc.private_subnet_ids
}

output "private_security_group_id" {
  value = module.vpc.private_security_group_id
}

output "isolated_subnet_ids" {
  value = module.vpc.isolated_subnet_ids
}

output "isolated_security_group_id" {
  value = module.vpc.isolated_security_group_id
}

output "availability_zone_ids" {
  value = module.vpc.availability_zone_ids
}
""",
    )

    write_stack(
        env,
        "cognito",
        main_body=f"""
module "cognito" {{
  source = "../../../../tf-modules/tf-cognito"
{common_module_args().rstrip()}

  user_pools = {{
    employees = {{ detail = "employees" }}
  }}

  custom_sign_in_attributes = {{
    employees = [
      {{
        name                = "roles"
        attribute_data_type = "String"
        required            = false
        mutable             = true
        min_length          = 0
        max_length          = 2048
      }}
    ]
  }}

  applications = {{
    argus = {{
      user_pool                    = "employees"
      name                         = "argus-authn"
      domain                       = "argus-authn-${{var.env}}"
      allow_admin_create_user_only = true
      callback_urls = [
        "http://localhost:9000/auth/callback",
        "https://argus-${{var.env}}.${{var.hosted_zone_name}}/auth/callback",
      ]
      logout_urls = [
        "http://localhost:9000/login",
        "https://argus-${{var.env}}.${{var.hosted_zone_name}}/login",
      ]
      allowed_oauth_flows          = ["code"]
      allowed_oauth_scopes         = ["openid", "email", "profile"]
      supported_identity_providers = ["COGNITO"]
      attribute_mapping = {{
        email       = "email"
        given_name  = "given_name"
        family_name = "family_name"
      }}
    }}
  }}
}}
""",
        outputs_body="""
output "user_pool_ids" {
  value = module.cognito.user_pool_ids
}

output "app_client_ids" {
  value = module.cognito.app_client_ids
}

output "cognito_domain_urls" {
  value = module.cognito.cognito_domain_urls
}
""",
    )

    write_stack(
        env,
        "github_oidc_provider",
        main_body="""
module "github_oidc_provider" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-github-oidc-provider"
  version = "5.30.0"

  tags = {
    Name = "provider-${var.landscape}-${var.env}-${var.region_short}-github_oidc"
  }
}
""",
    )

    # Order-only relative to github_oidc_provider (apply provider first).
    # No remote_state — the role module creates its own provider reference.
    write_stack(
        env,
        "github_oidc_role",
        main_body="""
module "github_oidc_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-github-oidc-role"
  version = "5.30.0"

  name = "role-${var.landscape}-${var.env}-${var.region_short}-github_oidc"

  subjects = var.oidc_subjects

  policies = {
    AmazonS3FullAccess   = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
    CloudFrontFullAccess = "arn:aws:iam::aws:policy/CloudFrontFullAccess"
    AWSLambda_FullAccess = "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
  }
}
""",
    )

    write_stack(
        env,
        "argus/iam-lambda_policy",
        main_body=f"""
module "iam_lambda_policy" {{
  source = "../../../../../tf-modules/tf-iam-lambda-policy"
{common_module_args().rstrip()}

  app_alias = "argus"
}}
""",
        outputs_body="""
output "std_lambda" {
  value = module.iam_lambda_policy.std_lambda
}
""",
    )

    write_stack(
        env,
        "argus/rds",
        remote_states=[("vpc", "vpc")],
        main_body=f"""
module "rds" {{
  source = "../../../../../tf-modules/tf-rds"
{common_module_args().rstrip()}

  app_alias               = "argus"
  subnet_tier             = "isolated"
  database_name           = "argus"
  engine                  = "aurora-postgresql"
  engine_version          = "17.4"
  master_username         = "postgres"
  storage_encrypted       = true
  create_kms_key          = false
  subnet_ids              = data.terraform_remote_state.vpc.outputs.isolated_subnet_ids
  vpc_security_group_ids  = [data.terraform_remote_state.vpc.outputs.isolated_security_group_id]
  port                    = 5432
  serverless_min_capacity = 0.5
  serverless_max_capacity = 1
  deletion_protection     = false
  availability_zone_ids   = data.terraform_remote_state.vpc.outputs.availability_zone_ids
  create_parameter_group  = false
  parameter_group_family  = "aurora-postgresql17"
  backup_retention_period = 7
}}
""",
        outputs_body="""
output "cluster_endpoint" {
  value = module.rds.cluster_endpoint
}

output "cluster_port" {
  value = module.rds.cluster_port
}

output "database_name" {
  value = module.rds.database_name
}
""",
    )

    write_stack(
        env,
        "argus/lambda-argus_api",
        remote_states=[
            ("lambda_policy", "argus/iam-lambda_policy"),
            ("cloudwatch_logging", "cloudwatch_logging"),
            ("vpc", "vpc"),
            ("rds", "argus/rds"),
            ("cognito", "cognito"),
        ],
        main_body=f"""
locals {{
  app_alias       = "argus"
  detail          = "argus_api"
  description     = "Argus CMDB API Lambda (argus-api-lambda)"
  artifact_bucket = var.artifact_bucket
  artifact_key    = "${{local.app_alias}}/${{var.env}}/${{local.app_alias}}-${{local.detail}}.zip"
}}

module "lambda_argus_api" {{
  source = "../../../../../tf-modules/tf-lambda"
{common_module_args().rstrip()}

  cloudwatch_logging_policy = data.terraform_remote_state.cloudwatch_logging.outputs.cloudwatch_logging_policy_arn
  policy-std_lambda         = data.terraform_remote_state.lambda_policy.outputs.std_lambda

  vpc_config = {{
    subnet_ids         = data.terraform_remote_state.vpc.outputs.private_subnet_ids
    security_group_ids = [data.terraform_remote_state.vpc.outputs.private_security_group_id]
  }}

  config = {{
    app_alias             = local.app_alias
    detail                = local.detail
    description           = local.description
    architectures         = ["x86_64"]
    handler               = "handler.handler"
    memory_size           = 256
    package_type          = "Zip"
    runtime               = "nodejs24.x"
    timeout               = 30
    application_log_level = "INFO"
    log_format            = "JSON"
    s3_bucket             = local.artifact_bucket
    s3_key                = local.artifact_key
    environment = {{
      variables = {{
        PGHOST                     = data.terraform_remote_state.rds.outputs.cluster_endpoint
        PGPORT                     = tostring(data.terraform_remote_state.rds.outputs.cluster_port)
        PGDATABASE                 = data.terraform_remote_state.rds.outputs.database_name
        PGUSER                     = "argus_lambda"
        PG_SSL                     = "true"
        PG_SSL_REJECT_UNAUTHORIZED = "false"
        PGPASSWORD                 = "<SEED_VIA_SSM_OR_CONSOLE>"
        AUTH_MODE                  = "cognito"
        CORS_ORIGIN                = "https://argus-${{var.env}}.${{var.hosted_zone_name}}"
        COGNITO_USER_POOL_ID       = data.terraform_remote_state.cognito.outputs.user_pool_ids["employees"]
        COGNITO_APP_CLIENT_ID      = data.terraform_remote_state.cognito.outputs.app_client_ids["argus"]
        COGNITO_ISSUER             = "https://cognito-idp.${{var.region}}.amazonaws.com/${{data.terraform_remote_state.cognito.outputs.user_pool_ids["employees"]}}"
        COGNITO_DOMAIN_URL         = data.terraform_remote_state.cognito.outputs.cognito_domain_urls["employees"]
        ADMIN_ROLE_CLAIM_VALUE     = "admin"
        APP_EDIT_ROLE_CLAIM_VALUE  = "app-edit"
        VIEWER_ROLE_CLAIM_VALUE    = "viewer"
        LOG_LEVEL                  = "info"
        SERVICE_NAME               = "argus-api"
        ENV_NAME                   = var.env
      }}
    }}
  }}

  api_gateway_triggers = []
  sqs_triggers         = []
  s3_triggers          = []
  lambda_destinations  = {{}}

  custom_policy = {{
    Version = "2012-10-17"
    Statement = [
      {{
        Sid    = "LambdaVPCAccess"
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:AssignPrivateIpAddresses",
          "ec2:UnassignPrivateIpAddresses",
        ]
        Resource = "*"
      }},
      {{
        Sid      = "ReadDeploymentPackage"
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion"]
        Resource = "arn:aws:s3:::${{local.artifact_bucket}}/*"
      }}
    ]
  }}
}}
""",
        outputs_body="""
output "lambda_function_name" {
  value = module.lambda_argus_api.lambda_function_name
}

output "lambda_function_invoke_arn" {
  value = module.lambda_argus_api.lambda_function_invoke_arn
}
""",
    )

    write_stack(
        env,
        "argus/api-gateway",
        remote_states=[
            ("argus_api_lambda", "argus/lambda-argus_api"),
            ("cognito", "cognito"),
        ],
        main_body=f"""
locals {{
  app_alias = "argus"
}}

module "api_gateway" {{
  source = "../../../../../tf-modules/tf-apigw"
{common_module_args().rstrip()}

  app_alias   = local.app_alias
  detail      = "api"
  description = "HTTP API for Argus SPA (/api) -> argus-api-lambda"

  lambda_function_name = data.terraform_remote_state.argus_api_lambda.outputs.lambda_function_name
  lambda_invoke_arn    = data.terraform_remote_state.argus_api_lambda.outputs.lambda_function_invoke_arn

  enable_access_logs        = true
  access_log_retention_days = 14

  jwt_authorizer = {{
    issuer   = "https://cognito-idp.${{var.region}}.amazonaws.com/${{data.terraform_remote_state.cognito.outputs.user_pool_ids["employees"]}}"
    audience = [data.terraform_remote_state.cognito.outputs.app_client_ids["argus"]]
  }}
  default_route_authorization_type = "JWT"
  authorized_route_keys            = []
}}
""",
        outputs_body="""
output "api_endpoint" {
  value = module.api_gateway.api_endpoint
}
""",
    )

    write_stack(
        env,
        "argus/tls",
        main_body=f"""
module "tls" {{
  source = "../../../../../tf-modules/tf-tls"
{common_module_args().rstrip()}

  app_alias        = "argus"
  domain_name      = "argus-${{var.env}}.${{var.hosted_zone_name}}"
  hosted_zone_name = var.hosted_zone_name
}}
""",
        outputs_body="""
output "certificate_arn" {
  value = module.tls.certificate_arn
}
""",
    )

    write_stack(
        env,
        "argus/cloudfront",
        remote_states=[
            ("api_gateway", "argus/api-gateway"),
            ("tls", "argus/tls"),
        ],
        main_body=f"""
locals {{
  app_alias     = "argus"
  api_origin_id = "${{local.app_alias}}-apigw-origin"
  domain_name   = "argus-${{var.env}}.${{var.hosted_zone_name}}"
}}

module "cloudfront" {{
  source = "../../../../../tf-modules/tf-cloudfront"
{common_module_args().rstrip()}

  app_alias                  = local.app_alias
  cloudfront_aliases         = [local.domain_name]
  cloudfront_certificate_arn = data.terraform_remote_state.tls.outputs.certificate_arn

  cloudfront_default_root_object = "index.html"
  cloudfront_http_version        = "http2and3"

  apigw_origin_host = replace(data.terraform_remote_state.api_gateway.outputs.api_endpoint, "https://", "")

  spa_origin = {{
    domain_name = "s3-${{local.app_alias}}-${{var.env}}-${{var.region_short}}-spa.s3.${{var.region}}.amazonaws.com"
    origin_id   = "${{local.app_alias}}-spa-origin"
  }}

  ordered_cache_behaviors = [
    {{
      path_pattern     = "/api/*"
      target_origin_id = local.api_origin_id
      allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
      cached_methods   = ["GET", "HEAD"]
      compress         = true
    }}
  ]

  custom_error_responses = [
    {{
      error_code            = 403
      response_code         = 200
      response_page_path    = "/index.html"
      error_caching_min_ttl = 10
    }},
    {{
      error_code            = 404
      response_code         = 200
      response_page_path    = "/index.html"
      error_caching_min_ttl = 10
    }}
  ]
}}
""",
        outputs_body="""
output "cloudfront_distribution_domain_name" {
  value = module.cloudfront.cloudfront_distribution_domain_name
}

output "cloudfront_distribution_id" {
  value = module.cloudfront.cloudfront_distribution_id
}
""",
    )

    write_stack(
        env,
        "argus/dns_record",
        remote_states=[("cloudfront", "argus/cloudfront")],
        providers_body=PROVIDERS_WITH_ROUTE53,
        main_body=f"""
module "dns_record" {{
  source = "../../../../../tf-modules/tf-dns_record"

  providers = {{
    aws         = aws
    aws.route53 = aws.route53
  }}
{common_module_args().rstrip()}

  app_alias        = "argus"
  record_name      = "argus-${{var.env}}.${{var.hosted_zone_name}}"
  record_type      = "CNAME"
  records          = [data.terraform_remote_state.cloudfront.outputs.cloudfront_distribution_domain_name]
  hosted_zone_name = var.hosted_zone_name
  ttl              = 300
}}
""",
    )

    write_stack(
        env,
        "argus/ssm_param",
        remote_states=[("rds", "argus/rds")],
        main_body=f"""
locals {{
  app_alias = "argus"
}}

module "ssm_param" {{
  source = "../../../../../tf-modules/tf-ssm_param"
{common_module_args().rstrip()}

  parameters = [
    {{
      comp        = "AURORA"
      app_alias   = upper(local.app_alias)
      name        = "WRITE_DB_HOST"
      value       = data.terraform_remote_state.rds.outputs.cluster_endpoint
      type        = "String"
      description = "AuroraDB Host used to connect to Argus DB for write"
    }},
    {{
      comp        = "AURORA"
      app_alias   = upper(local.app_alias)
      name        = "USERNAME"
      value       = "${{local.app_alias}}_service_acct"
      type        = "String"
      description = "Non DBO username for argus database"
    }},
    {{
      comp        = "AURORA"
      app_alias   = upper(local.app_alias)
      name        = "PASSWORD"
      value       = "<SEED_OUTSIDE_TERRAFORM>"
      type        = "SecureString"
      description = "Non DBO password for argus database"
    }},
    {{
      comp        = "ENV"
      app_alias   = upper(local.app_alias)
      name        = "LOG_LEVEL"
      value       = "debug"
      type        = "String"
      description = "Log level for argus"
    }},
  ]
}}
""",
    )


def main() -> None:
    for env in ("dev", "prod"):
        generate(env)
    print("Generated stacks for dev and prod.")


if __name__ == "__main__":
    main()
