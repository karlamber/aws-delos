# tf-vpc

**Provenance:** Deduplicated from landscape archives and sanitized.

## Required inputs

- `region`
- `account_id`
- `env`
- `landscape`
- `region_short`
- `vpc_cidr`
- `create_internet_gateway`
- `create_nat_gateways`
- `retention_in_days`
- `availability_zone_ids`
- `create_ssm_vpc_endpoints`

## Usage

Reference from Terragrunt:

```hcl
terraform {
  source = "../../../tf-modules/tf-vpc"
}
```
