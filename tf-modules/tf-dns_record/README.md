# tf-dns_record

**Provenance:** Deduplicated from landscape archives and sanitized.

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

Reference from Terragrunt:

```hcl
terraform {
  source = "../../../tf-modules/tf-dns_record"
}
```
