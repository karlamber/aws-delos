# tf-lambda

This module creates the easyCMDB API function, including its log group, optional VPC attachment, and the event permissions the stack passes in. The deployment package is an object in the artifact bucket named by the account configuration, which in this lab is the shared bucket in the management account rather than a bucket this landscape creates. The database password arrives as `PGPASSWORD`, and that value is what the `argus_lambda` role must use. A stack in this landscape calls it with `source = "../../../../../tf-modules/tf-lambda"`.

## Required inputs

- `region`
- `account_id`
- `env`
- `landscape`
- `region_short`
- `log_retention`
- `config`
- `vpc_config`
- `custom_policy`
- `policy-std_lambda`
- `cloudwatch_logging_policy`
- `sqs_triggers`
- `api_gateway_triggers`
- `s3_triggers`
- `lambda_destinations`
- `additional_policy_arns`

## Usage

A stack sets the module source as follows.

```hcl
terraform {
  source = "../../../../../tf-modules/tf-lambda"
}
```
