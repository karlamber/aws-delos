# tf-rds

This module creates the Aurora PostgreSQL cluster for the Argus database on the isolated subnets. Terraform creates the empty database named `argus` and stops there. Tables and the `argus_lambda` login are applied as SQL after the cluster exists, from the landscape `initial-config.sql` where that file is present and from easycmdb-api otherwise. The master password is managed outside the Terraform files that are committed. A stack in this landscape calls it with `source = "../../../../../tf-modules/tf-rds"`.

## Required inputs

- `region`
- `account_id`
- `env`
- `landscape`
- `region_short`
- `app_alias`
- `engine`
- `engine_version`
- `database_name`
- `master_username`
- `storage_encrypted`
- `create_kms_key`
- `kms_key_id`
- `backup_retention_period`
- `preferred_backup_window`
- `preferred_maintenance_window`
- `port`
- `serverless_min_capacity`
- `serverless_max_capacity`
- `deletion_protection`
- `vpc_security_group_ids`
- `subnet_ids`
- `subnet_tier`
- `availability_zone_ids`
- `create_parameter_group`
- `parameter_group_family`
- `parameter_group_name`
- `parameter_group_parameters`
- `enabled_cloudwatch_logs_exports`
- `performance_insights_enabled`
- `performance_insights_retention_period`
- `performance_insights_kms_key_id`

## Usage

A stack sets the module source as follows.

```hcl
terraform {
  source = "../../../../../tf-modules/tf-rds"
}
```
