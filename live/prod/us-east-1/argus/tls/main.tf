module "tls" {
  source = "../../../../../tf-modules/tf-tls"

  region       = var.region
  account_id   = var.account_id
  env          = var.env
  landscape    = var.landscape
  region_short = var.region_short

  app_alias        = "argus"
  domain_name      = "argus-${var.env}.${var.hosted_zone_name}"
  hosted_zone_name = var.hosted_zone_name
}
