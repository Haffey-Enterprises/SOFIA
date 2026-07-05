#!/usr/bin/env bash
# File: scripts/validate-docs-structure.sh
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-04
# Description: CI conformance gate for project-authored documentation. Collects the
#   governed markdown set (docs/, agent-loop/, scripts/) and enforces authorship
#   headers, filename hygiene, decision-record placement/naming, decision-record
#   metadata + change-log coherence, agent-loop record placement, and (in diff mode
#   only) contract purity — keeping instantiated ticket/ruling identifiers out of
#   normative decision-record bodies. Ticket: RBT-50.
#
# Local invocation is identical to CI, no extra plumbing:
#   bash scripts/validate-docs-structure.sh            # diff vs origin/develop
#   bash scripts/validate-docs-structure.sh --all      # full-corpus structural sweep
#   bash scripts/validate-docs-structure.sh --base main
#
# Compatibility: bash 3.2+ (macOS local + Linux CI).
# Exit taxonomy: 0 = pass; 1 = violations found (RED); 2 = environment / precondition
#   error. AMBER notes are accumulated and printed but never change the exit status.

set -euo pipefail

# Tracker-identifier prefix. Consumed by the contract-purity check's concrete-ID
# anchor so the enforced ticket namespace is declared in exactly one place.
TRACKER_PREFIX="RBT"

# --- Scope / mode --------------------------------------------------------------
# Default is touched-only: diff the working set against BASE_REF and check just what
# changed, matching a remediate-at-touch-time posture. --all runs the STRUCTURAL
# checks over the whole governed set for a periodic maintenance sweep; contract
# purity is touch-time-only by construction and never runs under --all (a full-corpus
# purity pass would fire on bodies written before the rule existed).
MODE="diff"
BASE_REF="origin/develop"

usage() {
    cat <<'USAGE'
usage: validate-docs-structure.sh [--all] [--base <ref>]
  (default)      diff-scoped: structural + contract-purity checks over docs touched since --base
  --all          full-corpus: structural checks over the whole governed set (no contract-purity)
  --base <ref>   diff base for the touched-set collection (default: origin/develop)
  -h | --help    show this help
USAGE
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --all)     MODE="all"; shift ;;
        --base)    [ "$#" -ge 2 ] || { echo "RED (env): --base requires a ref argument" >&2; exit 2; }
                   BASE_REF="$2"; shift 2 ;;
        --base=*)  BASE_REF="${1#--base=}"; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "RED (env): unknown argument '$1' (use --all or --base <ref>; -h for help)" >&2; exit 2 ;;
    esac
done

# --- Repo root + preconditions -------------------------------------------------
# A scanned-0 PASS is the worst failure mode for a gate: it goes green while
# checking nothing. Every precondition below therefore fails LOUD (exit 2) with a
# reason rather than letting collection silently yield an empty or partial set.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)" \
    || { echo "RED (env): cannot resolve script directory" >&2; exit 2; }
REPO_ROOT="$(cd "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd)" \
    || { echo "RED (env): cannot resolve repo root from '$SCRIPT_DIR'" >&2; exit 2; }
cd "$REPO_ROOT" || { echo "RED (env): cannot cd to repo root '$REPO_ROOT'" >&2; exit 2; }

command -v git >/dev/null 2>&1 \
    || { echo "RED (env): git not found on PATH — collection depends on git" >&2; exit 2; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    || { echo "RED (env): not inside a git work tree at '$REPO_ROOT'" >&2; exit 2; }

# In diff mode the base ref MUST resolve; a diff-scoped gate that cannot resolve its
# base must not scan a vacuous-empty set and pass green. CI supplies the base by
# checking out full history (fetch-depth: 0); locally pass --base or fetch the branch.
if [ "$MODE" = "diff" ]; then
    git rev-parse --verify --quiet "${BASE_REF}^{commit}" >/dev/null 2>&1 \
        || { echo "RED (env): diff base '${BASE_REF}' not resolvable. Pass --base <ref>, ensure CI checks out full history (fetch-depth: 0), or use --all. Refusing to scan a vacuous set." >&2; exit 2; }
fi

# --- Accumulators --------------------------------------------------------------
VIOLATIONS=()   # RED — each one fails the gate (exit 1)
AMBER_NOTES=()  # non-blocking — printed, never affects exit status
SCANNED=0

note_violation() { VIOLATIONS+=("$1"); }
note_amber()     { AMBER_NOTES+=("$1"); }

# Extract the value cell of a two-column metadata row: '| **Key** | value |' -> 'value'.
metadata_value() {
    printf '%s' "$1" | awk -F'|' '{ v=$3; gsub(/^[[:space:]]+/,"",v); gsub(/[[:space:]]+$/,"",v); print v }'
}

# --- Exemption: frozen run substrate -------------------------------------------
# agent-loop/runs/*/substrate/** holds pinned, frozen input snapshots captured for a
# run by design — they are not project-authored artifacts and must never be edited to
# satisfy a check. They are exempt from every check EXCEPT filename hygiene (a frozen
# snapshot with a space or odd character in its name is still a real portability bug).
is_substrate() {
    case "$1" in
        agent-loop/runs/*/substrate/*) return 0 ;;
    esac
    return 1
}

# --- Check A: authorship header (scope: docs/** only) --------------------------
# Line 1 must be '# File: <path>' with <path> equal to the actual repo-relative path,
# and '# Author:', '# Created:', '# Description:' must each be present.
# `command grep` bypasses any user grep alias/function.
check_header() {
    local f="$1" first declared
    first="$(command sed -n '1p' "$f")"
    declared=""
    case "$first" in
        "# File:"*) declared="$(printf '%s' "$first" | command sed 's/^# File:[[:space:]]*//; s/[[:space:]]*$//')" ;;
    esac
    if [ -z "$declared" ]; then
        note_violation "[A authorship-header] $f: missing first-line '# File:' header (must be line 1)"
        return
    fi
    if [ "$declared" != "$f" ]; then
        note_violation "[A authorship-header] $f: '# File:' declares '$declared' but the actual path is '$f'"
    fi
    command grep -q '^# Author:'      "$f" || note_violation "[A authorship-header] $f: missing '# Author:' line"
    command grep -q '^# Created:'     "$f" || note_violation "[A authorship-header] $f: missing '# Created:' line"
    command grep -q '^# Description:' "$f" || note_violation "[A authorship-header] $f: missing '# Description:' line"
}

# --- Check B: filename hygiene (scope: every collected *.md, incl. substrate) ---
check_filename_hygiene() {
    local f="$1" base
    base="$(basename "$f")"
    case "$base" in
        *" "*) note_violation "[B filename-hygiene] $f: basename contains a space" ;;
    esac
    if printf '%s' "$base" | LC_ALL=C command grep -q '[^a-zA-Z0-9._-]'; then
        note_violation "[B filename-hygiene] $f: basename has characters outside [a-zA-Z0-9._-]"
    fi
}

# --- Check C: decision-record placement + naming -------------------------------
# Scope: any collected file whose basename starts ADR-/DDR-/SDD- (substrate already
# excluded by the caller). Required home + filename shape come from the
# author-decision-record skill: PREFIX-NNN-slug.md, 3+ digit zero-padded number,
# lowercase-kebab slug, living in docs/adr|ddr|sdd/.
check_doctype_placement() {
    local f="$1" base dir prefix reqdir
    base="$(basename "$f")"
    dir="$(dirname "$f")"
    case "$base" in
        ADR-*) prefix="ADR"; reqdir="docs/adr" ;;
        DDR-*) prefix="DDR"; reqdir="docs/ddr" ;;
        SDD-*) prefix="SDD"; reqdir="docs/sdd" ;;
        *) return ;;
    esac
    if [ "$dir" != "$reqdir" ]; then
        note_violation "[C doctype-placement] $f: ${prefix}-prefixed file must live in ${reqdir}/ (per the author-decision-record skill)"
    fi
    if ! printf '%s' "$base" | LC_ALL=C command grep -Eq "^${prefix}-[0-9]{3,}-[a-z0-9]+(-[a-z0-9]+)*\.md$"; then
        note_violation "[C doctype-placement] $f: filename must match ${prefix}-NNN-slug.md (3+ digit zero-padded number, lowercase-kebab slug; per the author-decision-record skill)"
    fi
}

# --- Check E: metadata table + change-log coherence ----------------------------
# Scope: docs/adr|ddr|sdd/**. Form only, no content semantics:
#   * '| **Version** | X |'  with X = semver (N.N.N)
#   * '| **Status**  | S |'  with S in the accepted lifecycle set
#   * '| **Date**    | D |'  with D = YYYY-MM-DD
#   * at least one Change Log table row whose Version cell equals the metadata Version.
# The Change Log heading matcher tolerates optional leading numbering ('## 8. Change
# Log') because the corpus numbers its section headings.
check_metadata_changelog() {
    local f="$1"
    case "$f" in docs/adr/*|docs/ddr/*|docs/sdd/*) ;; *) return ;; esac

    local vrow ver="" srow st drow dt
    vrow="$(command grep -m1 -E '^\|[[:space:]]*\*\*Version\*\*[[:space:]]*\|' "$f" || true)"
    if [ -z "$vrow" ]; then
        note_violation "[E metadata] $f: missing '| **Version** | X |' metadata row"
    else
        ver="$(metadata_value "$vrow")"
        if ! printf '%s' "$ver" | command grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'; then
            note_violation "[E metadata] $f: Version '$ver' is not semver (N.N.N)"
            ver=""
        fi
    fi

    srow="$(command grep -m1 -E '^\|[[:space:]]*\*\*Status\*\*[[:space:]]*\|' "$f" || true)"
    if [ -z "$srow" ]; then
        note_violation "[E metadata] $f: missing '| **Status** | S |' metadata row"
    else
        st="$(metadata_value "$srow")"
        case "$st" in
            PROPOSED|ACCEPTED|ACCEPTED-WITH-CONDITIONS|SUPERSEDED|REJECTED|DEFERRED) ;;
            *) note_violation "[E metadata] $f: Status '$st' not in {PROPOSED, ACCEPTED, ACCEPTED-WITH-CONDITIONS, SUPERSEDED, REJECTED, DEFERRED}" ;;
        esac
    fi

    drow="$(command grep -m1 -E '^\|[[:space:]]*\*\*Date\*\*[[:space:]]*\|' "$f" || true)"
    if [ -z "$drow" ]; then
        note_violation "[E metadata] $f: missing '| **Date** | D |' metadata row"
    else
        dt="$(metadata_value "$drow")"
        if ! printf '%s' "$dt" | command grep -Eq '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
            note_violation "[E metadata] $f: Date '$dt' is not YYYY-MM-DD"
        fi
    fi

    # Only assert change-log coherence when a well-formed Version was found.
    if [ -n "$ver" ]; then
        local found
        found="$(awk -v want="$ver" '
            /^##[[:space:]]+([0-9]+\.[[:space:]]+)?Change Log([[:space:]]|$)/ { incl=1; next }
            incl && /^##[[:space:]]/ { incl=0 }
            incl && /^\|/ {
                n=split($0, a, "|"); cell=a[2]
                gsub(/^[[:space:]]+/,"",cell); gsub(/[[:space:]]+$/,"",cell)
                if (cell==want) { print "1"; exit }
            }
        ' "$f")" || true
        if [ "$found" != "1" ]; then
            note_violation "[E metadata] $f: no Change Log row whose Version cell equals the metadata Version '$ver'"
        fi
    fi
}

# --- Check F: agent-loop record placement (minimal) ----------------------------
# Scope: collected *.md under agent-loop/ (substrate already excluded by the caller).
# audit.md must be a direct child of a run dir; record.md must be a direct child of a
# triage/ or deliberation/ subdir. Every other agent-loop markdown file is a working
# note and passes here (ungated beyond hygiene, by design).
check_agentloop_placement() {
    local f="$1" base rest
    case "$f" in agent-loop/*) ;; *) return ;; esac
    base="$(basename "$f")"
    if [ "$base" = "audit.md" ]; then
        case "$f" in
            agent-loop/runs/*/audit.md)
                rest="${f#agent-loop/runs/}"; rest="${rest%/audit.md}"
                case "$rest" in
                    ""|*/*) note_violation "[F agent-loop-placement] $f: audit.md must be a direct child of a run dir (agent-loop/runs/<run>/audit.md)" ;;
                esac ;;
            *) note_violation "[F agent-loop-placement] $f: audit.md must live at agent-loop/runs/<run>/audit.md" ;;
        esac
    elif [ "$base" = "record.md" ]; then
        case "$f" in
            agent-loop/triage/*/record.md)
                rest="${f#agent-loop/triage/}"; rest="${rest%/record.md}"
                case "$rest" in ""|*/*) note_violation "[F agent-loop-placement] $f: record.md must be a direct child of a triage subdir (agent-loop/triage/<x>/record.md)" ;; esac ;;
            agent-loop/deliberation/*/record.md)
                rest="${f#agent-loop/deliberation/}"; rest="${rest%/record.md}"
                case "$rest" in ""|*/*) note_violation "[F agent-loop-placement] $f: record.md must be a direct child of a deliberation subdir (agent-loop/deliberation/<x>/record.md)" ;; esac ;;
            *) note_violation "[F agent-loop-placement] $f: record.md must live at agent-loop/triage/<x>/record.md or agent-loop/deliberation/<x>/record.md" ;;
        esac
    fi
}

# --- Check D: contract purity (scope: docs/adr|ddr|sdd/**; DIFF MODE ONLY) ------
# Grandfather-until-touched: bodies authored before this rule are only held to it when
# they are next touched, so the check runs only on the diff set — never under --all.
# Instantiated ticket/ruling identifiers belong on audit surfaces (the Change Log or a
# cross-reference row), not inline in a normative body. Schematic teaching tokens
# (R{N}, B-N) carry a non-digit after the prefix and never match — the digit anchor
# guarantees it.
check_contract_purity() {
    local f="$1" fences body pattern hits line
    case "$f" in docs/adr/*|docs/ddr/*|docs/sdd/*) ;; *) return ;; esac

    # (1) Unbalanced backtick-fence count -> AMBER (the strip below cannot then delimit
    # fenced regions reliably), non-blocking; proceed best-effort.
    fences="$(command grep -cE '^[[:space:]]*```' "$f" 2>/dev/null || true)"
    fences="${fences:-0}"
    if [ $(( fences % 2 )) -ne 0 ]; then
        note_amber "$f: unbalanced code fence ($fences fence line(s)); contract-purity body-strip may be unreliable — manual review advised"
    fi

    # (2) Surface-strip the body in a single POSIX-awk pass: drop fenced code blocks,
    # the Change Log section, and Cross-References/References sections (each heading to
    # the next '## ' or EOF), plus a '| **References** |' metadata row if present.
    # Section matchers tolerate optional leading numbering ('## 8. Change Log') because
    # the corpus numbers its headings; an unnumbered-only matcher would fail to strip
    # those audit surfaces and false-RED their legitimate ticket references.
    body="$(awk '
        /^[[:space:]]*```/ { infence = !infence; next }
        infence { next }
        /^##[[:space:]]+([0-9]+\.[[:space:]]+)?Change Log([[:space:]]|$)/                    { insec=1; next }
        /^##[[:space:]]+([0-9]+\.[[:space:]]+)?(Cross-References|References)([[:space:]]|$)/  { insec=1; next }
        /^##[[:space:]]/ { insec=0 }
        insec { next }
        /^[[:space:]]*\|[[:space:]]*\*\*References\*\*[[:space:]]*\|/ { next }
        { print }
    ' "$f")" || { echo "RED (env): $f: contract-purity body-strip (awk) failed" >&2; exit 2; }

    # (3) Match instantiated identifiers on the surviving body. POSIX-ERE boundaries so
    # the pattern behaves identically under BSD grep (macOS) and GNU grep (CI).
    pattern='(^|[^[:alnum:]_])(R[0-9]+|'"${TRACKER_PREFIX}"'-[0-9]+|[BM]-[0-9]+)([^[:alnum:]_]|$)'
    hits="$(printf '%s\n' "$body" | command grep -E "$pattern" || true)"
    if [ -n "$hits" ]; then
        while IFS= read -r line; do
            [ -n "$line" ] || continue
            note_violation "[D contract-purity] $f: inline operational identifier in normative body (relocate to the Change Log or a cross-reference row): $(printf '%s' "$line" | command sed 's/^[[:space:]]*//')"
        done <<< "$hits"
    fi
}

# --- Collect the governed set --------------------------------------------------
# Membership: markdown under docs/, agent-loop/, scripts/ at any depth. Two populations
# share that rule: diff mode (files touched since BASE_REF) and --all (the whole set).
# DIRECTORY-PREFIX pathspecs only ('docs' 'agent-loop' 'scripts'), never wildcards like
# 'docs/*.md': a wildcard pathspec relies on '*' crossing '/', which is git's default
# but is silently inverted under glob magic (GIT_GLOB_PATHSPECS=1 or a :(glob) prefix),
# dropping every nested file and going vacuously green. A directory-prefix pathspec is a
# leading-directory match, stable across GIT_GLOB_PATHSPECS / GIT_NOGLOB_PATHSPECS /
# GIT_LITERAL_PATHSPECS. NUL-delimited (-z) so odd paths survive; diff uses three-dot
# BASE...HEAD with --diff-filter=ACMR (Added/Copied/Modified/Renamed; deletions can't
# be read, and a rename-with-edit still surfaces the new path for scanning).
collect() {
    if [ "$MODE" = "all" ]; then
        git ls-files -z -- docs agent-loop scripts
    else
        git diff -z --name-only --diff-filter=ACMR "${BASE_REF}...HEAD" -- docs agent-loop scripts
    fi
}

# Capture to a tempfile and check the collector's OWN exit status. A process-
# substitution driver would swallow a git failure into a scanned-0 vacuous green; a
# tempfile lets us fail RED (exit 2) on a collection error instead.
GOVERNED_SET="$(mktemp)" || { echo "RED (env): mktemp failed" >&2; exit 2; }
trap 'rm -f "$GOVERNED_SET"' EXIT
if ! collect > "$GOVERNED_SET"; then
    echo "RED (env): governed-set collection failed (git returned non-zero). Refusing to scan a partial set." >&2
    exit 2
fi

# --- Main loop -----------------------------------------------------------------
while IFS= read -r -d '' f; do
    [ -n "$f" ] || continue
    case "$f" in *.md) ;; *) continue ;; esac
    SCANNED=$(( SCANNED + 1 ))

    # Filename hygiene applies to everything collected, including frozen substrate.
    check_filename_hygiene "$f"

    # Substrate is exempt from every other check.
    if is_substrate "$f"; then
        continue
    fi

    case "$f" in docs/*) check_header "$f" ;; esac
    check_doctype_placement "$f"
    check_metadata_changelog "$f"
    check_agentloop_placement "$f"
    if [ "$MODE" = "diff" ]; then
        check_contract_purity "$f"
    fi
done < "$GOVERNED_SET"

# --- Report --------------------------------------------------------------------
if [ "$MODE" = "all" ]; then
    echo "validate-docs-structure [--all]: scanned ${SCANNED} markdown file(s) (structural checks; contract-purity is diff-mode only)."
else
    echo "validate-docs-structure [diff vs ${BASE_REF}]: scanned ${SCANNED} touched markdown file(s)."
fi

if [ "${#AMBER_NOTES[@]}" -gt 0 ]; then
    echo "AMBER — ${#AMBER_NOTES[@]} non-blocking note(s):"
    for a in "${AMBER_NOTES[@]}"; do
        echo "  - $a"
    done
fi

if [ "${#VIOLATIONS[@]}" -gt 0 ]; then
    echo "FAIL — ${#VIOLATIONS[@]} violation(s):" >&2
    for v in "${VIOLATIONS[@]}"; do
        echo "  - $v" >&2
    done
    exit 1
fi

echo "PASS — no documentation-structure violations."
exit 0
