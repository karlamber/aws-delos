# tf-iam-lambda-policy

This module creates the standard execution policy the Argus API Lambda attaches to its role. The policy covers the baseline the function needs in this account, and any extra statement, such as reading the artifact zip, is added by the stack that calls `tf-lambda` rather than by widening this policy into an administrator document. A stack in this landscape calls it with `source = "../../../../../tf-modules/tf-iam-lambda-policy"`.

## Required inputs

- `region`
- `account_id`
- `env`
- `landscape`
- `region_short`
- `app_alias`

## Usage

A stack sets the module source as follows.

```hcl
terraform {
  source = "../../../../../tf-modules/tf-iam-lambda-policy"
}
```
