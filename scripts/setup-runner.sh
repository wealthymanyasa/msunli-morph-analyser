#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Self-hosted GitHub Actions runner setup for msunli-morph-analyser (dev)
# Run this on the dev server (10.52.0.12) as a user with sudo privileges.
#
# Usage:
#   1. Get a runner registration token from:
#      GitHub → Settings → Actions → Runners → "New self-hosted runner"
#   2. Export it:  export RUNNER_TOKEN="<token>"
#   3. Run:        sudo bash setup-runner.sh
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

RUNNER_NAME="msunli-morph-runner-dev"
RUNNER_DIR="/opt/actions-runner"
RUNNER_LABELS="self-hosted,linux,x64,dev"
GITHUB_REPO="wealthymanyasa/msunli-morph-analyser"

# ── Preflight checks ────────────────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
  echo "ERROR: This script must be run as root (sudo)." >&2
  exit 1
fi

if [[ -z "${RUNNER_TOKEN:-}" ]]; then
  echo "ERROR: RUNNER_TOKEN environment variable is not set." >&2
  echo "Get a token from GitHub → Settings → Actions → Runners → New self-hosted runner" >&2
  exit 1
fi

# ── Install dependencies ────────────────────────────────────────────────────
echo ">>> Installing dependencies..."
apt-get update -qq
apt-get install -y -qq curl tar libicu-dev >/dev/null

# ── Create a dedicated service user ─────────────────────────────────────────
if ! id -u github-runner &>/dev/null; then
  echo ">>> Creating 'github-runner' system user..."
  useradd --system --no-log-init --create-home --shell /bin/bash github-runner
fi

# ── Download and configure the runner ────────────────────────────────────────
echo ">>> Setting up runner in ${RUNNER_DIR}..."
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

# Download latest runner
LATEST_VERSION=$(curl -s https://api.github.com/repos/actions/runner/releases/latest \
  | grep '"tag_name"' | sed -E 's/.*"v([^"]+)".*/\1/')
echo "    Downloading runner v${LATEST_VERSION}..."
curl -sL "https://github.com/actions/runner/releases/download/v${LATEST_VERSION}/actions-runner-linux-x64-${LATEST_VERSION}.tar.gz" \
  | tar xz --strip-components=1
chown -R github-runner:github-runner "$RUNNER_DIR"

# ── Configure ────────────────────────────────────────────────────────────────
echo ">>> Configuring runner '${RUNNER_NAME}' for ${GITHUB_REPO}..."
sudo -u github-runner ./config.sh \
  --url "https://github.com/${GITHUB_REPO}" \
  --token "$RUNNER_TOKEN" \
  --name "$RUNNER_NAME" \
  --labels "$RUNNER_LABELS" \
  --work "_work" \
  --replace \
  --unattended

# ── Install as systemd service ──────────────────────────────────────────────
echo ">>> Installing systemd service..."
./svc.sh install github-runner
./svc.sh start

echo ""
echo "✅ Runner '${RUNNER_NAME}' is installed and running."
echo "   Check status:  systemctl status actions.runner.*.service"
echo "   View logs:     journalctl -u actions.runner.* -f"
echo "   Stop:          cd ${RUNNER_DIR} && sudo ./svc.sh stop"
echo "   Remove:        cd ${RUNNER_DIR} && sudo ./svc.sh uninstall && sudo ./config.sh remove"
