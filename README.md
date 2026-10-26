# aws-delos

This repository is the plain-Terraform layout for the same easyCMDB landscape that [aws-delphi](https://github.com/karlamber/aws-delphi) runs with Terragrunt and [aws-kos](https://github.com/karlamber/aws-kos) runs with a Python orchestrator. The infrastructure alias is `argus`. The API is [easycmdb-api](https://github.com/karlamber/easycmdb-api) and the UI is [easycmdb-web](https://github.com/karlamber/easycmdb-web). All three repositories create the same kinds of resources, including the VPC, Cognito, Aurora, the API Lambda, API Gateway, CloudFront, TLS, and DNS. Delos is the version in which you pass shared settings with `-var-file` and apply each folder yourself, or with `scripts/tf-stack.sh`, so the wiring that a wrapper would hide stays visible in the stack directory.

| Repository | What runs the stacks | Where shared settings live | How order is decided | How one stack reads another | Layout |
|---|---|---|---|---|---|
| [aws-delphi](https://github.com/karlamber/aws-delphi) | Terragrunt | `account.hcl` and `root.hcl` | `dependency` blocks in each unit | Terragrunt `dependency` outputs | `aws-delphi-<env>/us-east-1/…` |
| [aws-kos](https://github.com/karlamber/aws-kos) | Python in `orchestrator/` | `account.json` and `region.json` | `stacks.json` | `data.terraform_remote_state` | `aws-kos-<env>/us-east-1/…` |
| aws-delos (this repository) | Terraform CLI, with an optional shell helper | `environments/<env>/terraform.tfvars` | The order in this README | `data.terraform_remote_state` | `live/<env>/us-east-1/…` |

Hostnames in this lab use the fifty9 domain, for example `argus-dev.fifty9.net`. Committed configuration uses placeholders. Replace them before an apply, and apply only after a real account, filled-in tfvars, and a state bucket exist.

## How a stack receives its settings

Terraform reads only the files inside one stack folder. It cannot walk up to a parent directory and inherit shared settings the way Terragrunt does. Delphi fills that gap with Terragrunt, and Kos fills it with Python that writes tfvars before each run. Delos leaves the step explicit. Shared account and region values live in `environments/<env>/terraform.tfvars`, and every plan or apply passes that file with `-var-file`, which is what `scripts/tf-stack.sh` does for you. Stacks are applied in dependency order so remote state exists for the next stack. Cross-stack values come from `remote_state.tf` through `data.terraform_remote_state`.

Terraform still creates and changes the AWS resources. There is no wrapper that invents providers, backends, or merge logic at runtime, because those files already live in each stack directory. An optional `environments/<env>/terraform.tfvars.local` is gitignored and, when `tf-stack.sh` is used, is applied after the committed tfvars. Each stack's `main.tf` holds settings that belong only to that stack, such as the VPC CIDR, the Cognito URLs, and the Lambda environment. Each stack's `backend.hcl` holds the S3 state bucket, key, and profile. Modules under `tf-modules/` are the reusable Terraform for the landscape. `scripts/generate-stacks.py` can regenerate stack boilerplate for both `dev` and `prod` after a structural change. Day-to-day settings still belong in `main.tf`.

A VPC, as a concrete example, is edited in `live/<env>/us-east-1/vpc/main.tf`, receives its account ID from `environments/<env>/terraform.tfvars`, and is planned with `terraform plan -var-file=…` or `./scripts/tf-stack.sh … plan`. The same stack in Delphi is `vpc/terragrunt.hcl`, and in Kos it is `vpc/main.tf` planned through `python3 -m orchestrator plan vpc`.

## Apply order

Two kinds of dependency show up in this tree, and they do not have the same requirement before a plan can succeed. An order-only relationship means apply B after A, for example the OIDC provider before the OIDC role, and B does not need A's state file. An output-wiring relationship means stack B has a `remote_state.tf` that reads A, so A must already have been applied and its state object must exist in S3. `terraform plan` previews changes and does not write that object. State appears after a successful apply.

Apply one stack at a time, in this order: `cloudwatch_logging`, then `vpc`, then `cognito`, then `github_oidc_provider` followed by `github_oidc_role`, then `argus/iam-lambda_policy`, then `argus/rds`, then `argus/lambda-argus_api`, then `argus/api-gateway`, then `argus/tls`, then `argus/cloudfront`, then `argus/dns_record`, and finally `argus/ssm_param`. The dev and prod VPC stacks set `create_internet_gateway` and `create_nat_gateways` to false, because API Gateway terminates the public request and the Lambda only needs a path to Aurora inside the VPC.

## Layout

```text
aws-delos/
├── environments/
│   ├── dev/terraform.tfvars(.example)
│   └── prod/terraform.tfvars(.example)
├── tf-modules/
├── live/
│   ├── dev/us-east-1/
│   │   ├── cloudwatch_logging, vpc, cognito, github_oidc_*
│   │   └── argus/
│   └── prod/us-east-1/
└── scripts/
    ├── tf-stack.sh
    └── generate-stacks.py
```

Each stack folder is an ordinary Terraform root: `main.tf`, `variables.tf`, `providers.tf`, `versions.tf`, `backend.hcl`, and, when the stack reads another stack, `remote_state.tf` and `outputs.tf`.

## Commands

`scripts/tf-stack.sh` selects the environment tfvars that match the stack path, runs `terraform init` with that stack's `backend.hcl`, and then plans or applies. The first three commands below init logging, plan logging, and apply the VPC. The manual equivalent is `terraform init -backend-config=backend.hcl` and `terraform plan -var-file=../../../../environments/dev/terraform.tfvars` from `live/dev/us-east-1/vpc`.

```bash
cd ~/Projects/aws-delos
./scripts/tf-stack.sh live/dev/us-east-1/cloudwatch_logging init
./scripts/tf-stack.sh live/dev/us-east-1/cloudwatch_logging plan
./scripts/tf-stack.sh live/dev/us-east-1/vpc apply
```

Prod uses the same pattern with `live/prod/…` and `environments/prod/terraform.tfvars`.

## Before the first apply

Create the AWS account you will use, for example `aws-delos-dev`. Edit `environments/dev/terraform.tfvars`, or copy the example and keep real values in a gitignored `terraform.tfvars.local`. Set `account_id`, `route53_account_id`, `dns_manager_role_arn`, `artifact_bucket`, and `oidc_subjects`. `hosted_zone_name` defaults to `fifty9.net` and can stay or change with the zone you can actually write. When this environment needs public DNS or the shared Lambda zip, grant the member account access in the management shared-services account.

Sign in and confirm the profile with `aws sso login --profile aws-delos-dev` and `aws sts get-caller-identity --profile aws-delos-dev`. Create the state bucket once for the account and region:

```bash
aws --profile aws-delos-dev s3 mb s3://s3-delos-dev-ue1-terraform-state --region us-east-1
```

Put secrets into SSM Parameter Store yourself, as `SecureString` parameters. The `argus/ssm_param` stack uses `<SEED_OUTSIDE_TERRAFORM>` as the database-password placeholder, and a real password does not belong in Terraform or in git. Then apply the stacks in the order above, one at a time.

## What stays local

Commit `environments/*/terraform.tfvars` and the example files when they contain placeholder IDs, the stack `main.tf` files without real GitHub organization or repository node IDs, the modules, the scripts, and this README. Keep `terraform.tfvars.local`, `.terraform/`, `*.tfstate*`, `tfplan`, and `.env*` on the machine that applies them. Before a push, `git status` and the search below should show no access-key prefix and no private-key block.

```bash
git status
git grep -E 'AKIA[0-9A-Z]{16}|BEGIN (RSA |OPENSSH )?PRIVATE' -- ':!*.lock.hcl' || true
```

Account IDs, GitHub OIDC subject IDs, and database or SSM passwords stay out of git. After the first successful `terraform init` on a machine, commit the generated `.terraform.lock.hcl` files so later runs resolve the same provider versions.

## Network

Each environment receives its own `/20` inside the AWS supernet `10.0.0.0/11`, so dev and prod never share a CIDR. Azure VNets, when they appear in the wider lab, use `10.32.0.0/11` and stay outside this block.

| Environment | Account block | us-east-1 VPC | Set in |
|---|---|---|---|
| `dev` | `10.0.32.0/20` | `10.0.32.0/21` | `live/dev/us-east-1/vpc/main.tf` |
| `prod` | `10.0.80.0/20` | `10.0.80.0/21` | `live/prod/us-east-1/vpc/main.tf` |

Those blocks sit apart from Delphi (`10.0.0.0/20` and `10.0.48.0/20`) and from Kos (`10.0.16.0/20` and `10.0.64.0/20`).
