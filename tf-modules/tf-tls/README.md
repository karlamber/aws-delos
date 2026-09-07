# tf-tls

**Provenance:** Deduplicated from landscape archives and sanitized.

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

Reference from Terragrunt:

```hcl
terraform {
  source = "../../../tf-modules/tf-tls"
}
```
