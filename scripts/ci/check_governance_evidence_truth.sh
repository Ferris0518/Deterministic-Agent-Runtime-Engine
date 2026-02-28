#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

failures=0

log() {
  echo "[governance-evidence-truth] $*"
}

if command -v rg >/dev/null 2>&1; then
  SEARCH_BIN="rg"
else
  SEARCH_BIN="grep"
fi

search_has_match() {
  local pattern="$1"
  local file="$2"
  if [[ "$SEARCH_BIN" == "rg" ]]; then
    rg -q -- "$pattern" "$file"
  else
    grep -Eq -- "$pattern" "$file"
  fi
}

require_pattern() {
  local pattern="$1"
  local file="$2"
  local label="$3"
  if ! search_has_match "$pattern" "$file"; then
    log "missing $label in $file"
    failures=$((failures + 1))
  fi
}

extract_section() {
  local file="$1"
  local start_heading="$2"
  awk -v start="$start_heading" '
    $0 == start {in_section=1; next}
    in_section && $0 ~ /^## / {in_section=0}
    in_section {print}
  ' "$file"
}

extract_subsection() {
  local file="$1"
  local start_heading="$2"
  awk -v start="$start_heading" '
    $0 == start {in_section=1; next}
    in_section && $0 ~ /^### / {in_section=0}
    in_section && $0 ~ /^## / {in_section=0}
    in_section {print}
  ' "$file"
}

check_feature_doc() {
  local file="$1"

  log "checking $file"

  require_pattern "^## Evidence$" "$file" "Evidence section"
  require_pattern "^### Commands$" "$file" "Commands subsection"
  require_pattern "^### Results$" "$file" "Results subsection"
  require_pattern "^### Behavior Verification$" "$file" "Behavior Verification subsection"
  require_pattern "^### Risks and Rollback$" "$file" "Risks and Rollback subsection"
  require_pattern "^### Review and Merge Gate Links$" "$file" "Review and Merge Gate Links subsection"

  if search_has_match '^mode:\s*todo_fallback\s*$' "$file"; then
    require_pattern '^topic_slug:\s*.+$' "$file" "topic_slug frontmatter (fallback mode)"
  else
    require_pattern '^change_ids:\s*\[[^]]+\]\s*$' "$file" "change_ids frontmatter (OpenSpec mode)"
  fi

  # Ensure OpenSpec artifact references are resolvable from repository root.
  while IFS= read -r path; do
    if [[ -n "$path" && "$path" =~ ^(openspec|docs)/ ]]; then
      if [[ ! -f "$path" ]]; then
        log "unresolvable artifact path in $file: $path"
        failures=$((failures + 1))
      fi
    fi
  done < <(extract_section "$file" "## OpenSpec Artifacts" | sed -n 's/.*`\([^`]*\)`.*/\1/p')

  # Require at least one GitHub PR link in review section.
  local review_section
  review_section="$(extract_subsection "$file" "### Review and Merge Gate Links")"
  if ! grep -Eq 'https://github\.com/.+/pull/[0-9]+' <<<"$review_section"; then
    log "missing GitHub PR review/merge link in $file"
    failures=$((failures + 1))
  fi
}

feature_docs=()
while IFS= read -r path; do
  feature_docs+=("$path")
done < <(find docs/features -maxdepth 1 -type f -name '*.md' ! -name 'README.md' | sort)

if [[ ${#feature_docs[@]} -eq 0 ]]; then
  log "no active feature aggregation docs found under docs/features/"
fi

for file in "${feature_docs[@]}"; do
  check_feature_doc "$file"
done

if [[ $failures -gt 0 ]]; then
  log "failed with $failures issue(s)"
  exit 1
fi

log "passed"
