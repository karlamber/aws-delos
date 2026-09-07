module "dns_record" {
  source = "../../../../../tf-modules/tf-dns_record"

  providers = {
    aws         = aws
    aws.route53 = aws.route53
  }

  region       = var.region
  account_id   = var.account_id
  env          = var.env
  landscape    = var.landscape
  region_short = var.region_short

  app_alias        = "argus"
  record_name      = "argus-${var.env}.${var.hosted_zone_name}"
  record_type      = "CNAME"
  records          = [data.terraform_remote_state.cloudfront.outputs.cloudfront_distribution_domain_name]
  hosted_zone_name = var.hosted_zone_name
  ttl              = 300
}
