# tf-modules

These modules are the Terraform implementation of the Delos landscape, kept beside the `live/` stacks that call them. A stack's `main.tf` sets `module.<name>.source` to the module directory, and shared account values arrive through `environments/<env>/terraform.tfvars` rather than through a wrapper that generates them. The same module shapes exist in [aws-kos](https://github.com/karlamber/aws-kos) and [aws-delphi](https://github.com/karlamber/aws-delphi). What differs is the runner, not the resource model.

`tf-vpc` builds the regional `/21`, with `/25` public subnets, `/24` private subnets, and `/25` isolated subnets across one to three availability zones. `tf-cognito` creates the user pool and the Argus app client. `tf-rds` creates the Aurora PostgreSQL cluster. `tf-lambda` creates the API function from a zip in the artifact bucket named in the environment tfvars. `tf-apigw` routes the HTTP API to the function. `tf-cloudfront` creates the SPA distribution, and by default it also creates a web ACL because `enable_default_waf` defaults to true. `tf-tls` requests an ACM certificate and writes the DNS validation records through the `aws.route53` alias, and `tf-dns_record` writes the application record in the same zone. `tf-s3` is the general-purpose bucket module. `tf-cloudwatch` creates the account logging role. `tf-iam-lambda-policy` attaches the standard Lambda execution permissions. `tf-ssm_param` writes SSM parameters whose values Terraform then ignores. `tf-waf` is the optional standalone web ACL, separate from the default ACL inside `tf-cloudfront`.

A regional stack under `live/<env>/us-east-1/` reaches a module with `../../../../tf-modules/<module>`. An application stack under `argus/` goes one level further, to `../../../../../tf-modules/<module>`.

```hcl
module "vpc" {
  source = "../../../../tf-modules/tf-vpc"
}
```
