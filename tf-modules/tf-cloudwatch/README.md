# tf-cloudwatch

This module creates the CloudWatch logging role for the account. API Gateway, Lambda, and the other services named in the assume-role policy use it when they write log groups, which is why the apply order places this stack first. Later stacks can then attach the logging policy without creating the role themselves. A stack in this landscape calls it with `source = "../../../../tf-modules/tf-cloudwatch"`.

## Required inputs

- `region`
- `account_id`
- `env`
- `landscape`
- `region_short`

## Usage

A stack sets the module source as follows.

```hcl
terraform {
  source = "../../../../tf-modules/tf-cloudwatch"
}
```
