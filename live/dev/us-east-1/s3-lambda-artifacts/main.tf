# Account-wide bucket for Lambda deployment zips. Each Lambda uses its own object key.

module "s3_lambda_artifacts" {
  source = "../../../../tf-modules/tf-s3"

  region       = var.region
  account_id   = var.account_id
  env          = var.env
  landscape    = var.landscape
  region_short = var.region_short

  # Landscape slot: this bucket is shared by every Lambda in the account.
  app_alias = var.landscape
  detail    = "lambda-artifacts"

  versioning_enabled                    = true
  encryption_enabled                    = true
  multipart_abort_days_after_initiation = 7
}
