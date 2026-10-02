#!/usr/bin/env bash
# Lyra installer — Linux first (Arch / CachyOS / Debian / Fedora), portable.
#
# What it does, in order, and nothing more:
#   1. checks Python 3.10+;
#   2. installs Lyra into an isolated venv (~/.local/share/lyra/venv);
#   3. puts a `lyra` launcher in ~/.local/bin;
#   4. optionally installs Ollama and pulls the model it recommends;
#   5. optionally installs a systemd user service;
#   6. runs `lyra --doctor` so you see exactly what is ready.
#
# It never sends data anywhere and never installs anything silently.
#
# Usage:
#   ./install.sh            # interactive
#   ./install.sh --yes      # accept all defaults (for scripts)
#   ./install.sh --no-ollama --no-service

set -u

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${LYRA_DATA_DIR:-$HOME/.local/share/lyra}"
VENV_DIR="$DATA_DIR/venv"
BIN_DIR="$HOME/.local/bin"
ASSUME_YES=0
WANT_OLLAMA=1
WANT_SERVICE=1

for arg in "$@"; do
  case "$arg" in
    --yes|-y) ASSUME_YES=1 ;;
    --no-ollama) WANT_OLLAMA=0 ;;
    --no-service) WANT_SERVICE=0 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
  esac
done

say()  { printf '%s\n' "$*"; }
ok()   { printf '  [ok] %s\n' "$*"; }
warn() { printf '  [!!] %s\n' "$*"; }
die()  { printf '  [xx] %s\n' "$*" >&2; exit 1; }

ask() {
  # ask "question" -> returns 0 for yes, 1 for no
  [ "$ASSUME_YES" -eq 1 ] && return 0
  printf '%s [Y/n] ' "$1"
  read -r answer
  case "${answer:-y}" in [nN]*) return 1 ;; *) return 0 ;; esac
}

say "Lyra installer"
say "=============="

# 1. Python ---------------------------------------------------------------
PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then
      PYTHON="$candidate"; break
    fi
  fi
done
[ -n "$PYTHON" ] || die "Python 3.10+ is required. Install it and run this script again."
ok "Python found: $("$PYTHON" --version)"

# 2. Virtualenv + install -------------------------------------------------
say "-> Installing Lyra into $VENV_DIR"
"$PYTHON" -m venv "$VENV_DIR" || die "could not create the virtual environment"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet "$REPO_DIR" || die "pip install failed"
ok "Lyra installed"

# 3. Launcher -------------------------------------------------------------
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/lyra" <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/lyra" "\$@"
EOF
chmod +x "$BIN_DIR/lyra"
ok "Launcher: $BIN_DIR/lyra"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) warn "$BIN_DIR is not in PATH. Add it: export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
esac

# 4. Ollama (optional, local model) --------------------------------------
if [ "$WANT_OLLAMA" -eq 1 ] && ! command -v ollama >/dev/null 2>&1; then
  if ask "Ollama is not installed. Install it now for a local model?"; then
    if command -v pacman >/dev/null 2>&1; then
      sudo pacman -S --noconfirm ollama
    elif command -v apt >/dev/null 2>&1; then
      curl -fsSL https://ollama.com/install.sh | sh
    elif command -v dnf >/dev/null 2>&1; then
      curl -fsSL https://ollama.com/install.sh | sh
    else
      warn "Unknown package manager. Install Ollama from https://ollama.com"
    fi
  fi
fi

if command -v ollama >/dev/null 2>&1; then
  if ! curl -s --max-time 2 http://localhost:11434/api/tags >/dev/null 2>&1; then
    warn "Ollama is installed but not running. Start it with: ollama serve"
  fi
  MODEL="$("$VENV_DIR/bin/python" - <<'PY'
from lyra_app.core.lyra_factory import suggest_model
print(suggest_model())
PY
)"
  case "$MODEL" in
    cloud:*) warn "This machine is better served by a cloud model ($MODEL)." ;;
    *) if ask "Pull the recommended local model '$MODEL'?"; then
         # Lyra offers the pull; it never installs a model on its own (REQ-009).
         "$VENV_DIR/bin/python" - "$MODEL" <<'PY' || warn "Model pull failed. You can retry later with: lyra, then /model pull"
  import sys
  from lyra_app.core import model_pull
  result = model_pull.pull(sys.argv[1])
  print(("  [ok] " if result.ok else "  [!!] ") + result.detail)
  raise SystemExit(0 if result.ok else 1)
PY
       fi ;;
  esac
fi

# 5. systemd user service (optional) -------------------------------------
if [ "$WANT_SERVICE" -eq 1 ] && command -v systemctl >/dev/null 2>&1; then
  if ask "Install a systemd user service to start the Lyra GUI at login?"; then
    SERVICE_DIR="$HOME/.config/systemd/user"
    mkdir -p "$SERVICE_DIR"
    cat > "$SERVICE_DIR/lyra.service" <<EOF
[Unit]
Description=Lyra local AI companion (web GUI)
After=network.target

[Service]
ExecStart=$BIN_DIR/lyra --gui --port 8000
Restart=on-failure
RestartSec=3

[Install]
WantedBy=default.target
EOF
    systemctl --user daemon-reload 2>/dev/null || true
    ok "Service written to $SERVICE_DIR/lyra.service"
    say "     Enable it with: systemctl --user enable --now lyra.service"
  fi
fi

# 6. Report ---------------------------------------------------------------
say ""
say "-> Environment check"
"$BIN_DIR/lyra" --doctor || true
say ""
say "Done. Start with:  lyra        (terminal)   or   lyra --gui   (browser)"
