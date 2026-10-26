# tf-dns_record

This module creates a Route 53 record in a public hosted zone. The zone often lives in a different account from the workload, so the aliased provider `aws.route53` assumes the DNS manager role there and writes the record with those credentials while the rest of the stack stays in the member account. Apply it after the TLS certificate and the CloudFront distribution exist, because the lab hostname points at that distribution. A stack in this landscape calls it with `source = "../../../../../tf-modules/tf-dns_record"`.

## Required inputs

- `region`
- `account_id`
- `env`
- `landscape`
- `region_short`
- `app_alias`
- `record_name`
- `record_type`
- `records`
- `hosted_zone_name`
- `ttl`
- `allow_overwrite`
- `alias`

## Usage

A stack sets the module source as follows.

```hcl
module "dns_record" {
  source = "../../../../../tf-modules/tf-dns_record"

  providers = {
    aws         = aws
    aws.route53 = aws.route53
  }
}
```

The calling stack declares the `aws.route53` alias the same way the TLS stack does, because the record is written in the account that owns the zone.
