#!/usr/bin/env bash
# Upload a placeholder Lambda zip when the account artifact key is missing.
# Same behavior as the aws-delphi lambda before_hook. A later application
# deploy overwrites this object. Apply s3-lambda-artifacts before this runs.
#
# Usage (from anywhere):
#   ./scripts/ensure-lambda-zip.sh dev
#   ./scripts/ensure-lambda-zip.sh prod
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <dev|prod>" >&2
  exit 1
fi

ENV_NAME="$1"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VAR_FILE="${REPO_ROOT}/environments/${ENV_NAME}/terraform.tfvars"
LOCAL_VAR_FILE="${REPO_ROOT}/environments/${ENV_NAME}/terraform.tfvars.local"

if [[ ! -f "$VAR_FILE" ]]; then
  echo "Missing tfvars: $VAR_FILE" >&2
  exit 1
fi

read_var() {
  local key="$1"
  local val=""
  local file found
  for file in "$VAR_FILE" "$LOCAL_VAR_FILE"; do
    [[ -f "$file" ]] || continue
    found="$(sed -n "s/^${key}[[:space:]]*=[[:space:]]*\"\\([^\"]*\\)\".*/\\1/p" "$file" | tail -n 1)"
    if [[ -n "$found" ]]; then
      val="$found"
    fi
  done
  printf '%s' "$val"
}

LANDSCAPE="$(read_var landscape)"
REGION_SHORT="$(read_var region_short)"
ACCOUNT_ID="$(read_var account_id)"
AWS_PROFILE="$(read_var aws_profile)"
TF_ENV="$(read_var env)"

if [[ -z "$LANDSCAPE" || -z "$REGION_SHORT" || -z "$ACCOUNT_ID" || -z "$AWS_PROFILE" || -z "$TF_ENV" ]]; then
  echo "tfvars is missing landscape, region_short, account_id, aws_profile, or env" >&2
  exit 1
fi

if [[ "$TF_ENV" != "$ENV_NAME" ]]; then
  echo "Refusing to upload: environments/${ENV_NAME} has env=${TF_ENV}" >&2
  exit 1
fi

BUCKET="s3-${LANDSCAPE}-${TF_ENV}-${REGION_SHORT}-${ACCOUNT_ID}-lambda-artifacts"
KEY="argus/${TF_ENV}/argus-argus_api.zip"

if aws --profile "$AWS_PROFILE" s3api head-object --bucket "$BUCKET" --key "$KEY" >/dev/null 2>&1; then
  echo "Lambda artifact already exists at s3://${BUCKET}/${KEY}"
  exit 0
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cat > "$tmp/handler.js" <<'JS'
exports.handler = async () => ({
  statusCode: 200,
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ status: "placeholder" }),
});
JS
TMP_ARTIFACT="$tmp" python3 - <<'PY'
import os
import pathlib
import zipfile

root = pathlib.Path(os.environ["TMP_ARTIFACT"])
with zipfile.ZipFile(root / "placeholder.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
    archive.write(root / "handler.js", "handler.js")
PY
echo "Uploading placeholder zip to s3://${BUCKET}/${KEY}"
if ! aws --profile "$AWS_PROFILE" s3 cp "$tmp/placeholder.zip" "s3://${BUCKET}/${KEY}" --content-type application/zip; then
  echo "Apply live/${ENV_NAME}/us-east-1/s3-lambda-artifacts before planning the Lambda stack." >&2
  exit 1
fi
