#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SKIP_SHORTCUT=0
if [[ "${1:-}" == "--skip-shortcut" ]]; then
  SKIP_SHORTCUT=1
fi

log() {
  echo "[installer] $*"
}

ensure_command() {
  local cmd="$1"
  local install_cmd="$2"
  local label="$3"

  if command -v "$cmd" >/dev/null 2>&1; then
    return
  fi

  log "Installing $label..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "$install_cmd"
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y "$install_cmd"
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm "$install_cmd"
  else
    log "No supported package manager found for $label. Please install it manually."
    exit 1
  fi
}

ensure_python() {
  if command -v python3 >/dev/null 2>&1; then
    return
  fi
  log "Python 3 is required. Please install it manually and rerun the installer."
  exit 1
}

ensure_runtime() {
  ensure_command git git "git"
  ensure_python
  ensure_command ffmpeg ffmpeg "ffmpeg"
  ensure_command python3 python3 "python3"
}

setup_venv_and_deps() {
  local venv_dir="$REPO_ROOT/.venv"
  if [[ ! -d "$venv_dir" ]]; then
    log "Creating virtual environment..."
    python3 -m venv "$venv_dir"
  fi

  local python_bin="$venv_dir/bin/python"
  "$python_bin" -m pip install --upgrade pip setuptools wheel
  "$python_bin" -m pip install -r "$REPO_ROOT/requirements.txt"

  if [[ ! -f "$REPO_ROOT/models/gfpgan-1024.onnx" ]] || [[ ! -f "$REPO_ROOT/models/inswapper_128_fp16.onnx" ]]; then
    log "Downloading required model files..."
    mkdir -p "$REPO_ROOT/models"
    curl -L "https://huggingface.co/hacksider/deep-live-cam/resolve/main/gfpgan-1024.onnx" -o "$REPO_ROOT/models/gfpgan-1024.onnx"
    curl -L "https://huggingface.co/hacksider/deep-live-cam/resolve/main/inswapper_128_fp16.onnx" -o "$REPO_ROOT/models/inswapper_128_fp16.onnx"
  fi
}

create_shortcut() {
  local desktop_dir="$HOME/Desktop"
  mkdir -p "$desktop_dir"
  "$REPO_ROOT/.venv/bin/python" "$REPO_ROOT/generate_desktop_shortcut.py" --name "Artesys-DLC" --install-dir "$desktop_dir"
  log "Desktop launcher created in $desktop_dir"
}

log "Starting Linux bootstrap installer..."
ensure_runtime
setup_venv_and_deps
if [[ "$SKIP_SHORTCUT" -eq 0 ]]; then
  create_shortcut
fi
log "Installation complete. Run the app with:"
log "  $REPO_ROOT/.venv/bin/python $REPO_ROOT/run.py"
