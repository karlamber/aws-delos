# tf-vpc

This module builds one regional VPC from a `/21`, which is half of an account `/20` inside the AWS supernet `10.0.0.0/11`. It creates the public, private, and isolated subnets, a route table for each tier, gateway endpoints for S3 and DynamoDB, a Secrets Manager interface endpoint, optional SSM interface endpoints, a security group per tier, VPC flow logs, and a CloudTrail trail. An internet gateway and NAT gateways default to off, and the Kos and Delos stacks leave both off, because API Gateway terminates the public request and the Lambda only needs a path to Aurora. The Secrets Manager endpoint is created with the VPC. The API reads its database password from the Lambda environment, so the function never calls that endpoint, while anything else in the VPC still can. A stack in this landscape calls it with `source = "../../../../tf-modules/tf-vpc"`.

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

A stack sets the module source as follows.

```hcl
terraform {
  source = "../../../../tf-modules/tf-vpc"
}
```
