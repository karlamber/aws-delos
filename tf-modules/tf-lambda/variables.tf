# Common Variables
# The following variables are used in every module

variable "region" {
  description = "The AWS region where resources will be created."
  type        = string
}

variable "account_id" {
  description = "AWS account ID."
  type        = string
}

variable "env" {
  description = "Environment acronym"
  type = string
}

variable "landscape" {
  description = "Landscape name"
  type = string
}

variable "region_short" {
  description = "Shortened version of the AWS Region for naming resources"
}

variable "log_retention" {
  description = "Number of days to retain CloudWatch logs for the Lambda function"
  type        = number
  default     = 30
}

# Module Specific Variables
# The following variables are required for specific resource values
variable "config" {
  type = object({
    app_alias = string
    detail = string
    architectures                  = list(string)          # ["x86_64"]
    code_signing_config_arn        = string                # null
    description                    = string                # ""
    handler                        = string                # "index.handler"
    kms_key_arn                    = string                # null
    layers                         = list(string)          # []
    memory_size                    = number                # 10240
    package_type                   = string                # "Zip"
    publish                        = bool                  # false
    reserved_concurrent_executions = number                # -1
    runtime                        = string                # "nodejs20.x"
    skip_destroy                   = bool                  # false
    source_code_hash               = string                # null
    timeout                        = number                # 900
    ephemeral_storage_size         = number                # 10240
    application_log_level          = string                # null
    log_format                     = string                # "Text"
    system_log_level               = string                # null
    tracing_mode                   = string                # "PassThrough"
    filename                       = string                # null
    image_uri                      = string                # null
    s3_bucket                      = string                # null
    s3_key                         = string                # null
    s3_object_version              = string                # null
    environment                    = optional(object({
      variables = map(string)
    }), null)
  })

  validation {
    condition = (
      var.config.package_type == "Image" ?
      (
        var.config.image_uri != null &&
        var.config.filename == null &&
        var.config.s3_bucket == null &&
        var.config.s3_key == null &&
        var.config.s3_object_version == null
      ) :
      var.config.package_type == "Zip" ?
      (
        var.config.image_uri == null &&
        var.config.runtime != null &&
        var.config.handler != null &&
        (
          var.config.filename != null ||
          (var.config.s3_bucket != null && var.config.s3_key != null)
        )
      ) :
      true
    )

    error_message = "For package_type \"Image\", set image_uri and leave filename/s3_* null. For \"Zip\", provide runtime, handler, and either filename or s3_bucket + s3_key (image_uri must be null)."
  }
}

variable "vpc_config" {
  description = "Optional VPC configuration for the Lambda function."
  type = object({
    subnet_ids         = list(string)
    security_group_ids = list(string)
  })
  default = null

  validation {
    condition     = var.vpc_config == null ? true : (length(var.vpc_config.subnet_ids) > 0 && length(var.vpc_config.security_group_ids) > 0)
    error_message = "When vpc_config is provided, both subnet_ids and security_group_ids must be non-empty lists."
  }
}

variable "custom_policy" {
  description = "Custom IAM policy content for the Lambda. Set to null if not needed."
  type        = any
  default     = null
}

variable "policy-std_lambda" {
  description = "ARN of PD Standard Lambda Policy"
  type = string
}

variable "cloudwatch_logging_policy" {
  description = "ARN of Cloudwatch Logging Policy"
  type = string
}

variable "sqs_triggers" {
  description = "List of triggers for the Lambda function, each with event_source_arn, batch_size, and enabled."
  type = list(
    object({
      event_source_arn = string
      batch_size       = number
      enabled          = bool
    })
  )
  default = []
}

variable "api_gateway_triggers" {
  description = "List of API Gateway triggers for the Lambda function."
  type = list(
    object({
      api_url = string
      resource = string
      method = string
    })
  )
  default = []
}

variable "s3_triggers" {
  description = "List of s3 triggers for the Lambda function."
  type = list(
    object({
      s3_arn = string
    })
  )
  default = []
}

variable "lambda_destinations" {
  description = "Map of Lambda destinations for success and failure, including retry attempts"
  type = map(object({
    destination_arn       = string  # ARN of the destination (SQS, SNS, Lambda, EventBridge)
    maximum_retry_attempts = optional(number, 2)  # Default retry attempts = 2
  }))
  default = {}
}

variable "additional_policy_arns" {
  description = "List of additional IAM policy ARNs to attach to the Lambda role"
  type        = list(string)
  default     = []
}
