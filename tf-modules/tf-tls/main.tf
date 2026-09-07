resource "aws_acm_certificate" "tls_cert" {
  domain_name       = var.domain_name
  validation_method = "DNS"
tags = {
  Name = "acm-${var.app_alias}-${var.env}-${var.region_short}-certificate"
  App_Alias = var.app_alias
}
  lifecycle {
    create_before_destroy = true
  }
}
