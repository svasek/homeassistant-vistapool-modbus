#!/usr/bin/env bash
set -euo pipefail
# Create HA config dir if missing
mkdir -p .devcontainer/.ha_config

# Copy default configuration only if configuration.yaml does not exist
if [ ! -f .devcontainer/.ha_config/configuration.yaml ]; then
  if [ -f .devcontainer/.ha_config/configuration-default.yaml ]; then
    cp .devcontainer/.ha_config/configuration-default.yaml .devcontainer/.ha_config/configuration.yaml
    echo "[init-ha] Seeded configuration.yaml from configuration-default.yaml"
  else
    echo "[init-ha] WARNING: configuration-default.yaml not found; leaving configuration.yaml absent"
  fi
else
  echo "[init-ha] configuration.yaml already present; not overwriting"
fi
