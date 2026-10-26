# tf-ssm_param

This module writes SSM parameters and then ignores later changes to `value`, so a secret seeded in the console or with the CLI is not overwritten the next time the stack is applied. The Argus API connects with `PGPASSWORD` from the Lambda environment. These parameters are the place to keep that secret outside Terraform, and the stack's committed placeholder is the marker that the real value was set elsewhere. A stack in this landscape calls it with `source = "../../../../../tf-modules/tf-ssm_param"`.

## Required inputs

- `region`
- `account_id`
- `env`
- `landscape`
- `region_short`
- `parameters`

## Usage

A stack sets the module source as follows.

```hcl
terraform {
  source = "../../../../../tf-modules/tf-ssm_param"
}
```
