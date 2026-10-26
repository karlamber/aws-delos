# tf-cloudfront

This module creates the CloudFront distribution that serves the easyCMDB single-page app, together with the origins the stack configures. The stack passes `cloudfront_aliases` and the ACM certificate from the TLS stack, so the hostname is `argus-<env>.<zone>` once DNS validation has finished. `enable_default_waf` defaults to true, which creates a web ACL on the distribution. That ACL is a paid AWS WAF control, and setting the flag to false leaves the distribution without it. A stack in this landscape calls it with `source = "../../../../../tf-modules/tf-cloudfront"`.

## Required inputs

- `region`
- `account_id`
- `env`
- `region_short`
- `app_alias`
- `cloudfront_aliases`
- `cloudfront_certificate_arn`
- `cloudfront_default_root_object`
- `additional_origins`
- `default_cache_behavior`
- `ordered_cache_behaviors`
- `custom_error_responses`
- `geo_restriction`
- `response_headers_policy_name`
- `web_acl_id`
- `enable_default_waf`

## Usage

A stack sets the module source as follows.

```hcl
terraform {
  source = "../../../../../tf-modules/tf-cloudfront"
}
```
