# tf-tls

This module requests an ACM certificate in the workload account and writes the DNS validation records in the hosted zone through the provider alias `aws.route53`. Validation cannot finish until those records exist, which is why the alias assumes the DNS manager role in the account that owns the zone. The CloudFront stack consumes `certificate_arn` after this stack has been applied. A stack in this landscape calls it with `source = "../../../../../tf-modules/tf-tls"`.

## Required inputs

- `region`
- `account_id`
- `env`
- `landscape`
- `region_short`
- `app_alias`
- `domain_name`
- `hosted_zone_name`

## Usage

A stack sets the module source as follows.

```hcl
module "tls" {
  source = "../../../../../tf-modules/tf-tls"

  providers = {
    aws         = aws
    aws.route53 = aws.route53
  }
}
```

The calling stack declares `provider "aws"` and a second provider with `alias = "route53"` that assumes `dns_manager_role_arn`. The module receives both through the `providers` argument above.
