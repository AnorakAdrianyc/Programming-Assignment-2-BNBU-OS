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
  python3 -m venv "$tmp_dir/venv-test" >/dev/null 2>&1
  local status=$?
  rm -rf "$tmp_dir"
  return "$status"
}

collect_missing_tools() {
  local missing=()
  for cmd in gcc gdb make python3 pip3; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
      missing+=("$cmd")
    fi
  done

  if ! command -v python3 >/dev/null 2>&1 || ! has_venv_support; then
    missing+=("python3-venv")
  fi

  printf '%s\n' "${missing[@]}"
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

mapfile -t missing_before < <(collect_missing_tools)
if [ "${#missing_before[@]}" -eq 0 ]; then
  echo "All required dependencies are already installed."
elif [ "$CHECK_ONLY" = true ]; then
  echo "Missing dependencies: ${missing_before[*]}" >&2
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

for cmd in gcc gdb make python3 pip3; do
  "$cmd" --version | head -n 1
done
python3 -m venv --help >/dev/null

echo "Modular C OS coding environment dependencies are ready."
