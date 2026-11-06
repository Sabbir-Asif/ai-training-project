#!/usr/bin/env bash
# Usage: scripts/set-issue-status.sh <issue-number> <Todo|"In Progress"|Done>
# Moves an issue's card on the DevPulse GitHub Project board (owner Sabbir-Asif, project #10).
set -euo pipefail
OWNER="${DEVPULSE_PROJECT_OWNER:-Sabbir-Asif}"
PROJECT="${DEVPULSE_PROJECT_NUMBER:-10}"
issue="${1:?issue number}"; status="${2:?status name}"

project_id=$(gh project view "$PROJECT" --owner "$OWNER" --format json --jq .id)
field=$(gh project field-list "$PROJECT" --owner "$OWNER" --format json \
  --jq '.fields[] | select(.name=="Status")')
field_id=$(jq -r .id <<<"$field")
option_id=$(jq -r --arg s "$status" '.options[] | select(.name==$s) | .id' <<<"$field")
[ -n "$option_id" ] || { echo "Unknown status: $status" >&2; exit 1; }
item_id=$(gh project item-list "$PROJECT" --owner "$OWNER" --limit 200 --format json \
  --jq ".items[] | select(.content.number==$issue) | .id")
[ -n "$item_id" ] || { echo "Issue #$issue not on board" >&2; exit 1; }

gh project item-edit --id "$item_id" --project-id "$project_id" \
  --field-id "$field_id" --single-select-option-id "$option_id" >/dev/null
echo "Issue #$issue -> $status"
