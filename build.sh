#!/usr/bin/env bash
set -euo pipefail

# Simple build script for this project
# - Installs dependencies using Poetry
# - No external variables or scripts required

if ! command -v poetry >/dev/null 2>&1; then
  echo "Error: Poetry is not installed. Please install it from https://python-poetry.org/docs/#installation" >&2
  exit 1
fi

echo "Installing dependencies with Poetry..."
poetry install

echo "Build completed successfully."
