# tf-waf

This module creates a WAFv2 web ACL and the optional logging and IP-set configuration the inputs describe. `tf-cloudfront` can also create a default web ACL when `enable_default_waf` is true, so this module is the path for a web ACL you want to design yourself and then pass in as `web_acl_id`. Attaching either ACL adds the paid WAF charge. A stack in this landscape calls it with `source = "../../../../../tf-modules/tf-waf"`.

## Required inputs

- `name`
- `description`
- `scope`
- `resource_type`
- `default_action`
- `rules`
- `visibility_config`
- `app_alias`
- `tags`
- `enable_logging`
- `log_group_name`
- `log_retention_in_days`
- `maintenance_mode_enabled`
- `maintenance_allowed_ips`
- `ip_sets`

## Usage

A stack sets the module source as follows.

```hcl
terraform {
  source = "../../../../../tf-modules/tf-waf"
}
```
