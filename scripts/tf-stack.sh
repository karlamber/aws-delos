#!/usr/bin/env bash
# Helper for running Terraform in an aws-delos stack directory.
#
# Usage (from repo root):
#   ./scripts/tf-stack.sh live/dev/us-east-1/vpc init
#   ./scripts/tf-stack.sh live/dev/us-east-1/vpc plan
#   ./scripts/tf-stack.sh live/dev/us-east-1/argus/api-gateway apply
#
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <stack-path-relative-to-repo-root> <terraform-command> [args...]" >&2
  exit 1
fi

STACK_PATH="$1"
shift
CMD="$1"
shift || true

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STACK_DIR="${REPO_ROOT}/${STACK_PATH}"

if [[ ! -d "$STACK_DIR" ]]; then
  echo "Stack directory not found: $STACK_DIR" >&2
  exit 1
fi

# live/dev/... -> dev
ENV="$(echo "$STACK_PATH" | cut -d/ -f2)"
VAR_FILE="${REPO_ROOT}/environments/${ENV}/terraform.tfvars"
LOCAL_VAR_FILE="${REPO_ROOT}/environments/${ENV}/terraform.tfvars.local"

cd "$STACK_DIR"

VAR_ARGS=()
if [[ -f "$VAR_FILE" ]]; then
  VAR_ARGS+=(-var-file="$VAR_FILE")
fi
if [[ -f "$LOCAL_VAR_FILE" ]]; then
  VAR_ARGS+=(-var-file="$LOCAL_VAR_FILE")
fi

if [[ "$CMD" == "init" ]]; then
  terraform init -backend-config=backend.hcl "$@"
elif [[ "$CMD" == "plan" || "$CMD" == "apply" || "$CMD" == "destroy" || "$CMD" == "validate" || "$CMD" == "import" || "$CMD" == "console" ]]; then
  terraform "$CMD" "${VAR_ARGS[@]}" "$@"
else
  terraform "$CMD" "$@"
fi
