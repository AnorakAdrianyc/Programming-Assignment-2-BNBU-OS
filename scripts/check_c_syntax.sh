#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <file1.c> [file2.c ...]" >&2
  exit 1
fi

for file in "$@"; do
  if [ ! -f "$file" ]; then
    echo "Error: file not found: $file. Please verify the file path exists." >&2
    exit 1
  fi

  if [[ "$file" != *.c ]]; then
    echo "Error: expected a .c file: $file" >&2
    exit 1
  fi

  gcc -fsyntax-only -Wall -Wextra -pedantic "$file"
  echo "Syntax OK: $file"
done
