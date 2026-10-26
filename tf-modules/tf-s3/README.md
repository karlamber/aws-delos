# tf-s3

This module creates a general-purpose S3 bucket with the versioning, encryption, lifecycle, and cross-account access the inputs describe. Stacks that need their own bucket, outside the origin created with the CloudFront distribution, call this module and pass the detail that becomes part of the bucket name. A stack in this landscape calls it with `source = "../../../../../tf-modules/tf-s3"`.

## Required inputs

- `region`
- `account_id`
- `env`
- `landscape`
- `region_short`
- `app_alias`
- `detail`
- `lifecycle_rule`
- `multipart_abort_days_after_initiation`
- `versioning_enabled`
- `encryption_enabled`
- `encryption_algorithm`
- `kms_key_id`
- `allowed_accounts`
- `organization_id`
- `cross_account_readonly`
- `cross_account_full_access`
- `full_access_roles`
- `readonly_roles`

## Usage

A stack sets the module source as follows.

```hcl
terraform {
  source = "../../../../../tf-modules/tf-s3"
}
```
