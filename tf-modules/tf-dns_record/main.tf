# Get the hosted zone ID from the hub account
data "aws_route53_zone" "dns_zone" {
  provider     = aws.hub
  name         = var.hosted_zone_name
  private_zone = false
}

# Create Route53 record in the hub account
resource "aws_route53_record" "dns_record" {
  provider = aws.hub

  allow_overwrite = var.allow_overwrite
  name            = var.record_name
  records         = var.records
  ttl             = var.ttl
  type            = var.record_type
  zone_id         = data.aws_route53_zone.dns_zone.zone_id

  dynamic "alias" {
    for_each = var.alias != null ? [var.alias] : []
    content {
      name                   = alias.value.name
      zone_id                = alias.value.zone_id
      evaluate_target_health = alias.value.evaluate_target_health
    }
  }
}

