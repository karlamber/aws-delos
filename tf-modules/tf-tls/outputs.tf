output "certificate_arn" {
  description = "The ARN of the ACM certificate."
  value       = aws_acm_certificate.tls_cert.arn
}

output "certificate_domain_name" {
  description = "The domain name for the ACM certificate."
  value       = aws_acm_certificate.tls_cert.domain_name
}

output "certificate_validation_method" {
  description = "The validation method for the ACM certificate."
  value       = aws_acm_certificate.tls_cert.validation_method
}

output "validation_records" {
  description = "CNAME record information required for DNS Validation"
  value = aws_acm_certificate.tls_cert.domain_validation_options
}