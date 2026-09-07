locals {
  app_alias     = "argus"
  api_origin_id = "${local.app_alias}-apigw-origin"
  domain_name   = "argus-${var.env}.${var.hosted_zone_name}"
}

module "cloudfront" {
  source = "../../../../../tf-modules/tf-cloudfront"

  region       = var.region
  account_id   = var.account_id
  env          = var.env
  landscape    = var.landscape
  region_short = var.region_short

  app_alias                  = local.app_alias
  cloudfront_aliases         = [local.domain_name]
  cloudfront_certificate_arn = data.terraform_remote_state.tls.outputs.certificate_arn

  cloudfront_default_root_object = "index.html"
  cloudfront_http_version        = "http2and3"

  apigw_origin_host = replace(data.terraform_remote_state.api_gateway.outputs.api_endpoint, "https://", "")

  spa_origin = {
    domain_name = "s3-${local.app_alias}-${var.env}-${var.region_short}-spa.s3.${var.region}.amazonaws.com"
    origin_id   = "${local.app_alias}-spa-origin"
  }

  ordered_cache_behaviors = [
    {
      path_pattern     = "/api/*"
      target_origin_id = local.api_origin_id
      allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
      cached_methods   = ["GET", "HEAD"]
      compress         = true
    }
  ]

  custom_error_responses = [
    {
      error_code            = 403
      response_code         = 200
      response_page_path    = "/index.html"
      error_caching_min_ttl = 10
    },
    {
      error_code            = 404
      response_code         = 200
      response_page_path    = "/index.html"
      error_caching_min_ttl = 10
    }
  ]
}
