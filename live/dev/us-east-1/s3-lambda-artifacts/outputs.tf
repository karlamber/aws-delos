output "bucket_name" {
  description = "Name of the shared Lambda artifact bucket."
  value       = module.s3_lambda_artifacts.bucket_name
}

output "bucket_arn" {
  description = "ARN of the shared Lambda artifact bucket."
  value       = module.s3_lambda_artifacts.bucket_arn
}
