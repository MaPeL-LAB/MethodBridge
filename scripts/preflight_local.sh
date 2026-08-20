#!/usr/bin/env bash
set -Eeuo pipefail

on_error() {
  local exit_code="$?"
  local line_number="$1"
  local failed_command="$2"
  trap - ERR
  printf 'ERROR: unexpected failure at line %s: %s\n' "$line_number" "$failed_command" >&2
  printf 'Changes made: none.\n' >&2
  printf 'Next command: bash scripts/preflight_local.sh\n' >&2
  exit "$exit_code"
}

trap 'on_error "$LINENO" "$BASH_COMMAND"' ERR

usage() {
  printf '%s\n' \
    'Usage: bash scripts/preflight_local.sh' \
    '' \
    'Run a read-only, network-free check of the local MethodBridge Python setup' \
    'and the governed local-execution handoff. No arguments are accepted.'
}

fail_closed() {
  local message="$1"
  local remediation="$2"
  local exit_code="${3:-1}"
  printf 'ERROR: %s\n' "$message" >&2
  printf 'Remediation (not run): %s\n' "$remediation" >&2
  printf 'Changes made: none.\n' >&2
  printf 'Next command: %s\n' "$remediation" >&2
  exit "$exit_code"
}

if [[ "$#" -eq 1 && "$1" == "--help" ]]; then
  usage
  printf 'Changes made: none.\n'
  printf 'Next command: bash scripts/preflight_local.sh\n'
  exit 0
fi
if [[ "$#" -ne 0 ]]; then
  usage >&2
  fail_closed \
    "unexpected arguments were supplied" \
    "bash scripts/preflight_local.sh" \
    64
fi

SCRIPT_SOURCE="${BASH_SOURCE[0]}"
case "$SCRIPT_SOURCE" in
  /*) ;;
  *) SCRIPT_SOURCE="${PWD}/${SCRIPT_SOURCE}" ;;
esac
SCRIPT_DIRECTORY_CANDIDATE="${SCRIPT_SOURCE%/*}"
if [[ "$SCRIPT_DIRECTORY_CANDIDATE" == "$SCRIPT_SOURCE" ]]; then
  fail_closed \
    "could not resolve the preflight script directory" \
    "bash scripts/preflight_local.sh"
fi
SCRIPT_DIRECTORY="$(cd "$SCRIPT_DIRECTORY_CANDIDATE" && pwd -P)"
REPOSITORY_ROOT="$(cd "$SCRIPT_DIRECTORY/.." && pwd -P)"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONNOUSERSITE=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
unset PYTHONHOME
unset PYTHONPATH

printf '[1/6] Validating repository and shell context\n'
if [[ ! -f "$REPOSITORY_ROOT/pyproject.toml" || ! -f "$REPOSITORY_ROOT/src/methodbridge/__init__.py" ]]; then
  fail_closed \
    "the script is not inside a MethodBridge source-layout checkout" \
    "cd /path/to/MethodBridge && bash scripts/preflight_local.sh"
fi
if (( BASH_VERSINFO[0] < 3 )); then
  fail_closed \
    "Bash 3 or newer is required; detected ${BASH_VERSION}" \
    "bash scripts/preflight_local.sh"
fi
printf '  Bash: %s\n' "$BASH_VERSION"

if ! GIT_COMMAND="$(
  trap - ERR
  command -v git
)"; then
  fail_closed \
    "git is required for repository identity and handoff provenance checks" \
    "install git through your approved system package process, then rerun bash scripts/preflight_local.sh"
fi
case "$GIT_COMMAND" in
  /*) ;;
  *)
    fail_closed \
      "git did not resolve to an absolute executable path" \
      "remove the git alias or function for this shell, then rerun bash scripts/preflight_local.sh"
    ;;
esac
if ! GIT_ROOT="$(
  trap - ERR
  "$GIT_COMMAND" -C "$REPOSITORY_ROOT" rev-parse --show-toplevel 2>/dev/null
)"; then
  fail_closed \
    "the MethodBridge checkout is not a readable git worktree" \
    "cd /path/to/MethodBridge && bash scripts/preflight_local.sh"
fi
GIT_ROOT="$(cd "$GIT_ROOT" && pwd -P)"
if [[ "$GIT_ROOT" != "$REPOSITORY_ROOT" ]]; then
  fail_closed \
    "repository root validation failed" \
    "cd /path/to/MethodBridge && bash scripts/preflight_local.sh"
fi
GIT_VERSION="$("$GIT_COMMAND" --version)"
printf '  Git: %s\n' "$GIT_VERSION"

printf '[2/6] Selecting the repository interpreter\n'
if command -v python >/dev/null 2>&1; then
  printf '  Unqualified python command: available but intentionally ignored\n'
else
  printf '  Unqualified python command: unavailable; this is not a failure\n'
fi
PYTHON_BIN="$REPOSITORY_ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  printf '%s\n' \
    '  Required setup commands (not run):' \
    '    python3 -m venv .venv' \
    "    .venv/bin/python -m pip install -e '.[dev]'" >&2
  fail_closed \
    "repository interpreter .venv/bin/python is missing or not executable" \
    "python3 -m venv .venv"
fi
if ! PYTHON_VERSION="$(
  trap - ERR
  "$PYTHON_BIN" --version 2>&1
)"; then
  fail_closed \
    "repository interpreter could not report its version" \
    "python3 -m venv .venv"
fi
if ! "$PYTHON_BIN" -s -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 12) else 1)'; then
  fail_closed \
    "MethodBridge requires Python 3.12 or newer; detected ${PYTHON_VERSION}" \
    "recreate .venv with an approved Python 3.12-or-newer interpreter"
fi
printf '  Repository interpreter: .venv/bin/python (%s)\n' "$PYTHON_VERSION"

printf '[3/6] Checking project and development dependencies\n'
if ! "$PYTHON_BIN" -s -m pip --version >/dev/null 2>&1; then
  fail_closed \
    "pip is unavailable in the repository virtual environment" \
    "recreate .venv, then run .venv/bin/python -m pip install -e '.[dev]'"
fi
if ! DEPENDENCY_VERSIONS="$(
  trap - ERR
  "$PYTHON_BIN" -s -c '
from importlib import metadata
from importlib.util import find_spec
import re
import tomllib
from pathlib import Path
import sys

root = Path(sys.argv[1])
project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
if project.get("project", {}).get("requires-python") != ">=3.12":
    raise SystemExit("unexpected project.requires-python contract")

requirements = (
    ("PyYAML", "yaml", (6, 0, 2)),
    ("jsonschema", "jsonschema", (4, 23, 0)),
    ("pytest", "pytest", (8, 3, 0)),
    ("pip", None, (0, 0, 0)),
)

def version_key(value: str) -> tuple[int, int, int]:
    numbers = [int(item) for item in re.findall(r"\d+", value)[:3]]
    return tuple((numbers + [0, 0, 0])[:3])

observed = []
for distribution_name, module_name, minimum in requirements:
    value = metadata.version(distribution_name)
    if version_key(value) < minimum:
        raise SystemExit(f"{distribution_name} {value} is below the required {minimum}")
    if module_name and find_spec(module_name) is None:
        raise SystemExit(f"{module_name} is not importable")
    observed.append(f"{distribution_name}={value}")
for build_tool in ("setuptools", "wheel"):
    try:
        observed.append(f"{build_tool}={metadata.version(build_tool)}")
    except metadata.PackageNotFoundError:
        observed.append(f"{build_tool}=missing")
print(", ".join(observed))
' "$REPOSITORY_ROOT" 2>&1
)"; then
  printf '%s\n' \
    '  The existing environment does not satisfy pyproject.toml.' \
    "  Exact remediation (not run): .venv/bin/python -m pip install -e '.[dev]'" >&2
  fail_closed \
    "required Python project or development dependencies are unavailable" \
    ".venv/bin/python -m pip install -e '.[dev]'"
fi
printf '  Dependencies: %s\n' "$DEPENDENCY_VERSIONS"

printf '[4/6] Validating source-layout and editable-import readiness\n'
if ! PYTHONPATH="$REPOSITORY_ROOT/src" "$PYTHON_BIN" -s -c '
from pathlib import Path
import sys
import methodbridge

root = (Path(sys.argv[1]) / "src" / "methodbridge").resolve()
module_path = Path(methodbridge.__file__).resolve()
raise SystemExit(0 if module_path == root / "__init__.py" else 1)
' "$REPOSITORY_ROOT" >/dev/null 2>&1; then
  fail_closed \
    "the local methodbridge package cannot be imported from the declared src layout" \
    ".venv/bin/python -m pip install -e '.[dev]'"
fi
printf '  Source-layout import: ready\n'

if "$PYTHON_BIN" -s -c '
from pathlib import Path
import sys
import methodbridge

root = (Path(sys.argv[1]) / "src" / "methodbridge").resolve()
module_path = Path(methodbridge.__file__).resolve()
raise SystemExit(0 if module_path == root / "__init__.py" else 1)
' "$REPOSITORY_ROOT" >/dev/null 2>&1; then
  printf '  Editable import without PYTHONPATH: ready\n'
else
  printf '%s\n' \
    '  Editable import without PYTHONPATH: not ready; explicit src mode remains usable' \
    "  Exact remediation (not run): .venv/bin/python -m pip install -e '.[dev]'"
fi

printf '[5/6] Running the minimum governed handoff validation\n'
HANDOFF_VALIDATOR="$REPOSITORY_ROOT/scripts/verify_local_model_handoff.py"
if [[ ! -f "$HANDOFF_VALIDATOR" ]]; then
  fail_closed \
    "the governed local handoff validator is missing" \
    "restore scripts/verify_local_model_handoff.py from the reviewed repository state"
fi
if ! HANDOFF_JSON="$(
  trap - ERR
  PYTHONPATH="$REPOSITORY_ROOT/src" "$PYTHON_BIN" -s "$HANDOFF_VALIDATOR" 2>&1
)"; then
  fail_closed \
    "the governed handoff validator reported an invalid repository or environment state" \
    "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/verify_local_model_handoff.py"
fi
if ! HANDOFF_STATE="$(
  trap - ERR
  printf '%s\n' "$HANDOFF_JSON" | "$PYTHON_BIN" -s -c '
import json
import sys

payload = json.load(sys.stdin)
if payload.get("valid") is not True:
    raise SystemExit("handoff payload is not valid")
if payload.get("local_setup_ready") is not True:
    raise SystemExit("local setup is not ready")
scope = payload.get("authorization_scope")
development_authorized = payload.get("development_r_and_d_authorized")
empirical_authorized = payload.get("empirical_execution_authorized")
downloads_allowed = payload.get("downloads_allowed")
eligibility_gate = payload.get("eligibility_gate")
contest_authorized = payload.get("contest_path_authorized")
if scope != "private_product_r_and_d":
    raise SystemExit("authorization scope is not development-only")
if development_authorized is not True:
    raise SystemExit("development R&D authorization is not recorded")
if empirical_authorized is not True or downloads_allowed is not True:
    raise SystemExit("development acquisition or execution is not authorized")
if eligibility_gate != "unresolved":
    raise SystemExit("contest eligibility gate changed unexpectedly")
if contest_authorized is not False:
    raise SystemExit("contest path must remain unauthorized")
print("true|private_product_r_and_d|true|true|unresolved|false")
' 2>/dev/null
)"; then
  fail_closed \
    "the governed handoff validator returned an incomplete or malformed status" \
    "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/verify_local_model_handoff.py"
fi
LOCAL_SETUP_READY="${HANDOFF_STATE%%|*}"
HANDOFF_REMAINDER="${HANDOFF_STATE#*|}"
AUTHORIZATION_SCOPE="${HANDOFF_REMAINDER%%|*}"
HANDOFF_REMAINDER="${HANDOFF_REMAINDER#*|}"
DEVELOPMENT_R_AND_D_AUTHORIZED="${HANDOFF_REMAINDER%%|*}"
HANDOFF_REMAINDER="${HANDOFF_REMAINDER#*|}"
EMPIRICAL_EXECUTION_AUTHORIZED="${HANDOFF_REMAINDER%%|*}"
HANDOFF_REMAINDER="${HANDOFF_REMAINDER#*|}"
ELIGIBILITY_GATE="${HANDOFF_REMAINDER%%|*}"
CONTEST_PATH_AUTHORIZED="${HANDOFF_REMAINDER#*|}"
if [[ "$LOCAL_SETUP_READY" != "true" ]]; then
  fail_closed \
    "local setup readiness did not pass" \
    "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python scripts/verify_local_model_handoff.py"
fi
printf '  local_setup_ready: %s\n' "$LOCAL_SETUP_READY"
printf '  authorization_scope: %s\n' "$AUTHORIZATION_SCOPE"
printf '  development_r_and_d_authorized: %s\n' "$DEVELOPMENT_R_AND_D_AUTHORIZED"
printf '  empirical_execution_authorized: %s\n' "$EMPIRICAL_EXECUTION_AUTHORIZED"
printf '  eligibility_gate: %s\n' "$ELIGIBILITY_GATE"
printf '  contest_path_authorized: %s\n' "$CONTEST_PATH_AUTHORIZED"

printf '[6/6] Confirming authorization and privacy boundaries\n'
printf '%s\n' \
  '  No model was downloaded or executed by this preflight.' \
  '  EXEC-001 permits only licensed public-no-credential acquisition, Docker simulation, and digest-bound local llama.cpp execution for private product R&D.' \
  '  No finalist, quantization, official profiler claim, public claim, hosting, release, registration, rules acceptance, or submission was authorized.' \
  '  Development R&D authorization is not contest eligibility, release, or submission authorization.'

printf 'Changes made: none.\n'
printf 'Next command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest -q -p no:cacheprovider\n'
