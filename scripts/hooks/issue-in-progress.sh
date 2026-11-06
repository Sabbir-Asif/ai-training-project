#!/usr/bin/env bash
# Claude Code PreToolUse hook (Edit|Write): before the first code change on a
# feat/T##-slug branch, move the matching issue to "In Progress" on the board.
# Runs once per branch (marker in .git). Never blocks the tool call.
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null) || exit 0
[[ "$branch" =~ ^feat/T0*([0-9]+)- ]] || exit 0
issue="${BASH_REMATCH[1]}"
marker="$(git rev-parse --git-dir)/devpulse-in-progress-${issue}"
[ -e "$marker" ] && exit 0
if scripts/set-issue-status.sh "$issue" "In Progress" >&2; then
  touch "$marker"
else
  echo "warning: could not update board status for #$issue" >&2
fi
exit 0
