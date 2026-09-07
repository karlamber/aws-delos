# aws-delos — Delos landscape (plain Terraform)

This repo builds the same Argus app infrastructure as **aws-delphi** and **aws-kos**, using **plain Terraform only** — no Terragrunt and no Python orchestrator. You `cd` into each stack folder (or use the small helper script) and run `terraform` yourself.

In short: same AWS resources and modules, different way of running the stacks.

Hostnames in this lab use the **fifty9** domain (for example `argus-dev.fifty9.net`). The repo is meant as a learnable / portfolio example of multi-stack AWS infrastructure. Committed config uses placeholders; replace them before you apply.

Sibling landscapes (same Argus stacks, different glue):

| Repo | How stacks are run |
|---|---|
| `aws-delphi` | Terragrunt |
| `aws-kos` | Python orchestrator + Terraform |
| **`aws-delos`** (this repo) | Plain Terraform only |

---

## Delphi vs Kos vs Delos

| | Delphi | Kos | Delos |
|---|---|---|---|
| What runs the stacks | Terragrunt | Python (`orchestrator/`) | You + Terraform CLI |
| Shared account settings | `account.hcl` + `root.hcl` | `account.json` + `region.json` | `environments/<env>/terraform.tfvars` |
| Which stack runs when | `dependency` blocks in HCL | `stacks.json` | Documented apply order (and optional `scripts/tf-stack.sh`) |
| How one stack reads another’s outputs | Terragrunt `dependency.x.outputs` | `data.terraform_remote_state` | `data.terraform_remote_state` |
| Layout | `aws-delphi-dev/us-east-1/…` | `aws-kos-dev/us-east-1/…` | `live/<env>/us-east-1/…` |

Do not apply until you have a real AWS account, filled-in env tfvars, and a state bucket (see [Before first apply](#before-first-apply)).

---

## How it works

Terraform only looks at files inside a stack folder. It cannot walk up to a parent folder and pull in shared settings the way Terragrunt does.

In Delphi, Terragrunt fills that gap. In Kos, Python does. In Delos, **you** do it explicitly:

1. Put shared account/region values in `environments/<env>/terraform.tfvars`
2. Pass that file on every plan/apply (`-var-file=…`, or `./scripts/tf-stack.sh …`)
3. Apply stacks in dependency order so remote state exists for the next stack
4. Cross-stack values come from `remote_state.tf` → `data.terraform_remote_state`

Terraform still creates and changes AWS resources. There is no wrapper that invents providers, backends, or merge logic at runtime — those files live in each stack directory.

### What you edit

| File | Purpose |
|---|---|
| `environments/<env>/terraform.tfvars` | Shared values: account ID, DNS role, OIDC subjects, artifact bucket, hosted zone |
| Optional `environments/<env>/terraform.tfvars.local` | Local overrides (gitignored); applied after the committed tfvars when using `tf-stack.sh` |
| Each stack’s `main.tf` | Settings unique to that stack (VPC CIDR, Cognito URLs, Lambda env, …) |
| Each stack’s `backend.hcl` | S3 state bucket/key/profile for that stack |
| Modules under `tf-modules/` | Reusable Terraform for this landscape |

Optional: `scripts/generate-stacks.py` regenerates stack boilerplate for both `dev` and `prod` (useful after structural changes). Prefer editing `main.tf` for day-to-day stack settings.

### Dependencies between stacks

| Kind | How it shows up | Needed before `plan`? |
|---|---|---|
| Order-only | Apply B after A (for example OIDC provider before OIDC role) | No remote state required |
| Output wiring | Stack B has `remote_state.tf` reading A | Yes — A must already be **applied** so its state exists in S3 |

Suggested apply order:

1. `cloudwatch_logging`
2. `vpc`
3. `cognito`
4. `github_oidc_provider` → `github_oidc_role`
5. `argus/iam-lambda_policy`
6. `argus/rds`
7. `argus/lambda-argus_api`
8. `argus/api-gateway`
9. `argus/tls`
10. `argus/cloudfront`
11. `argus/dns_record`
12. `argus/ssm_param`

---

## Compared to Delphi / Kos (one stack)

Example: the `vpc` stack

| | Delphi | Kos | Delos |
|---|---|---|---|
| Where you edit stack settings | `vpc/terragrunt.hcl` | `vpc/main.tf` | `live/<env>/…/vpc/main.tf` |
| Where the shared account ID comes from | Parent `account.hcl` | `account.json` → written into tfvars by Python | `environments/<env>/terraform.tfvars` via `-var-file` |
| How you run it | `terragrunt plan` in the stack folder | `python3 -m orchestrator plan vpc` | `terraform plan -var-file=…` (or `./scripts/tf-stack.sh … plan`) |

Reusable modules live under `tf-modules/`. The application name is still **argus**.

---

## Layout

```text
aws-delos/
├── environments/
│   ├── dev/terraform.tfvars(.example)   # shared config for all dev stacks
│   └── prod/terraform.tfvars(.example)
├── tf-modules/                          # shared Terraform modules for this landscape
├── live/
│   ├── dev/us-east-1/
│   │   ├── cloudwatch_logging, vpc, cognito, github_oidc_*
│   │   └── argus/                       # rds, lambda, apigw, tls, cloudfront, dns, ssm, iam
│   └── prod/us-east-1/                  # same stacks, prod tfvars / backends
└── scripts/
    ├── tf-stack.sh                      # init/plan/apply helper (picks env tfvars)
    └── generate-stacks.py               # regenerates live/ boilerplate
```

Each stack folder is a normal Terraform root: `main.tf`, `variables.tf`, `providers.tf`, `versions.tf`, `backend.hcl`, plus `remote_state.tf` / `outputs.tf` when needed.

---

## Commands

```bash
cd ~/Projects/aws-delos

# Helper (recommended): init with backend.hcl, plan/apply with the right env tfvars
./scripts/tf-stack.sh live/dev/us-east-1/cloudwatch_logging init
./scripts/tf-stack.sh live/dev/us-east-1/cloudwatch_logging plan
./scripts/tf-stack.sh live/dev/us-east-1/vpc apply

# Manual equivalent
cd live/dev/us-east-1/vpc
terraform init -backend-config=backend.hcl
terraform plan -var-file=../../../../environments/dev/terraform.tfvars
```

`prod` uses the same pattern with `live/prod/…` and `environments/prod/terraform.tfvars`.

---

## Before first apply

1. Create the AWS account(s) you will use (for example `aws-delos-dev`).
2. Edit `environments/dev/terraform.tfvars` (or copy `.example` and maintain a gitignored `terraform.tfvars.local`):
   - set real `account_id`, `route53_account_id`, `dns_manager_role_arn`
   - set `artifact_bucket` and `oidc_subjects`
   - keep or change `hosted_zone_name` (default `fifty9.net`)
3. If this environment needs DNS or shared Lambda artifacts, grant the member account access in the management shared-services account.
4. Sign in and confirm you are in the right account:
   ```bash
   aws sso login --profile aws-delos-dev
   aws sts get-caller-identity --profile aws-delos-dev
   ```
5. Create the S3 bucket that stores Terraform state (once per account/region):
   ```bash
   aws --profile aws-delos-dev s3 mb s3://s3-delos-dev-ue1-terraform-state --region us-east-1
   ```
6. Put secrets into SSM Parameter Store yourself (SecureString). Do not put real passwords in Terraform or git. The `argus/ssm_param` stack uses `<SEED_OUTSIDE_TERRAFORM>` for the DB password placeholder.
7. Apply stacks in the order listed above (one at a time).

`terraform plan` only previews changes; it does not write state to S3. State appears after a successful `apply`. Stacks with `remote_state.tf` need their parent stacks applied first.

---

## What belongs in git vs what stays local

| Safe to commit | Keep local (gitignored) |
|---|---|
| `environments/*/terraform.tfvars` / `.example` with placeholder IDs | `terraform.tfvars.local` with real account IDs, DNS role ARN, OIDC subjects, artifact bucket |
| Stack `main.tf` without real GitHub org/repo node IDs | `.terraform/`, `*.tfstate*`, `tfplan` |
| Modules, scripts, README | `.env*` |

Before you push (especially before making the repo public):

```bash
git status
git grep -E 'AKIA[0-9A-Z]{16}|BEGIN (RSA |OPENSSH )?PRIVATE' -- ':!*.lock.hcl' || true
```

Do not commit real AWS account IDs, GitHub OIDC subject IDs, or database/SSM passwords. After the first successful `terraform init` on a machine, **do** commit any generated `.terraform.lock.hcl` files so everyone uses the same provider versions.

---

## Network

Each env gets its own `/20` (no CIDR overlap between dev and prod):

| Env | Account block | us-east-1 VPC | Set in |
|---|---|---|---|
| `dev` | `10.0.32.0/20` | `10.0.32.0/21` | `live/dev/us-east-1/vpc/main.tf` |
| `prod` | `10.0.80.0/20` | `10.0.80.0/21` | `live/prod/us-east-1/vpc/main.tf` |

These blocks do not overlap Delphi (`10.0.0.0/20` / `10.0.48.0/20`) or Kos (`10.0.16.0/20` / `10.0.64.0/20`).
