# Shared variables for all stacks in aws-delos-dev.
# Pass with: terraform plan -var-file=../../../../environments/dev/terraform.tfvars
# (depth varies for argus/* stacks — use scripts/tf-stack.sh to pick the path).
#
# Committed values are placeholders safe for a public repo.
# Replace 000000000000 / EXAMPLE_* with your own before apply.

env          = "dev"
account_name = "aws-delos-dev"
account_id   = "000000000000"
aws_profile  = "aws-delos-dev"
landscape    = "delos"
region       = "us-east-1"
region_short = "ue1"

route53_account_id    = "000000000000"
dns_manager_role_arn  = "arn:aws:iam::000000000000:role/role-EXAMPLE-root-ue1-dns_manager"
artifact_bucket       = "s3-EXAMPLE-mgmt-ue1-shared-lambda"
hosted_zone_name      = "fifty9.net"

oidc_subjects = [
  "EXAMPLE_GITHUB_ORG/argus-api-lambda:*",
  "EXAMPLE_GITHUB_ORG/argus-front-end:*",
]
