# tf-cognito

This module creates the Cognito user pool and the Argus app client that API Gateway uses to validate tokens. Callback and logout URLs are inputs on the stack, and in this lab they include the fifty9 hostname for the environment. The API expects a role claim the stack configures, so a user who should administer easyCMDB needs that claim on the pool user before the SPA will show Management. A stack in this landscape calls it with `source = "../../../../tf-modules/tf-cognito"`.

## Required inputs

- `region`
- `account_id`
- `env`
- `landscape`
- `region_short`
- `app_alias`
- `detail`
- `user_pools`
- `applications`
- `custom_sign_in_attributes`
- `token_configuration`

## Usage

A stack sets the module source as follows.

```hcl
terraform {
  source = "../../../../tf-modules/tf-cognito"
}
```
