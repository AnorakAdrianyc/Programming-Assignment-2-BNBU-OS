#!/usr/bin/env bash
set -euo pipefail

CHECK_ONLY=false

usage() {
  cat <<'EOF'
Usage: scripts/setup_env.sh [--check-only]

Installs or validates required dependencies for the modular C OS editor environment:
- gcc
- gdb
- make
- python3
- pip3
- python3 venv support
EOF
}

for arg in "$@"; do
  case "$arg" in
    --check-only)
      CHECK_ONLY=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      usage >&2
      exit 1
      ;;
  esac
done

has_venv_support() {
  local tmp_dir
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "$tmp_dir"' RETURN
  python3 -m venv "$tmp_dir/venv-test" >/dev/null 2>&1
}

collect_missing_tools() {
  local missing=()

  add_missing() {
    local candidate="$1"
    local item
    for item in "${missing[@]:-}"; do
      if [ "$item" = "$candidate" ]; then
        return 0
      fi
    done
    missing+=("$candidate")
  }

  for cmd in gcc gdb make python3 pip3; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      add_missing "$cmd"
    fi
  done

  if command -v python3 >/dev/null 2>&1 && ! has_venv_support; then
    add_missing "python3-venv"
  fi

  if [ "${#missing[@]}" -gt 0 ]; then
    printf '%s\n' "${missing[@]}"
  fi
}

run_with_privilege() {
  if [ "${EUID:-$(id -u)}" -eq 0 ]; then
    "$@"
  elif command -v sudo >/dev/null 2>&1; then
    sudo "$@"
  else
    echo "Error: root privileges are required to install packages (sudo not found)." >&2
    exit 1
  fi
}

detect_package_manager() {
  for pm in apt-get dnf pacman zypper brew; do
    if command -v "$pm" >/dev/null 2>&1; then
      echo "$pm"
      return 0
    fi
  done
  return 1
}

install_dependencies() {
  local pm="$1"
  case "$pm" in
    apt-get)
      run_with_privilege apt-get update
      run_with_privilege apt-get install -y build-essential gdb make python3 python3-venv python3-pip
      ;;
    dnf)
      run_with_privilege dnf install -y gcc gcc-c++ gdb make python3 python3-pip python3-virtualenv
      ;;
    pacman)
      # pacman uses "python" package name for Python 3.
      run_with_privilege pacman -Sy --noconfirm base-devel gdb make python python-pip python-virtualenv
      ;;
    zypper)
      run_with_privilege zypper --non-interactive install gcc gcc-c++ gdb make python3 python3-pip python3-virtualenv
      ;;
    brew)
      brew install gcc gdb make python
      ;;
    *)
      echo "Error: unsupported package manager: $pm" >&2
      return 1
      ;;
  esac
}

missing_tools=()
while IFS= read -r dep; do
  if [ -n "$dep" ]; then
    missing_tools+=("$dep")
  fi
done < <(collect_missing_tools)
if [ "${#missing_tools[@]}" -eq 0 ]; then
  echo "All required dependencies are already installed."
elif [ "$CHECK_ONLY" = true ]; then
  echo "Missing dependencies: ${missing_tools[*]}" >&2
  exit 1
else
  if ! package_manager="$(detect_package_manager)"; then
    echo "Error: no supported package manager found." >&2
    echo "Install dependencies manually: gcc, gdb, make, python3, pip3, python3-venv." >&2
    exit 1
  fi
  echo "Installing dependencies with $package_manager..."
  install_dependencies "$package_manager"
fi

version_tmp="$(mktemp)"
trap 'rm -f "$version_tmp"' EXIT
for cmd in gcc gdb make python3 pip3; do
  if ! "$cmd" --version >"$version_tmp" 2>&1; then
    echo "Failed to verify $cmd after setup." >&2
    cat "$version_tmp" >&2
    exit 1
  fi
  head -n 1 "$version_tmp"
done

if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "Failed to verify python3 venv support after setup." >&2
  exit 1
fi

echo "Modular C OS coding environment dependencies are ready."
