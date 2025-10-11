# Vistapool Devcontainer Quickstart

## Prerequisites

- Docker and Docker Compose installed on the host.
- VS Code with the "Dev Containers" extension.
- On macOS/Linux, your user must be able to access the Docker socket.

## How to use

1. Open the repository root in VS Code.
2. When prompted, choose **Reopen in Container** (or run the command manually).
3. Wait until the container initializes. It will automatically run:
   - `pip install` for dev tools (ruff, pytest)
   - `docker compose -f .devcontainer/docker-compose.yml up -d` to start Home Assistant
4. Open http://localhost:8123 in your browser to finish onboarding.
5. Your integration code under `custom_components/vistapool` is mounted into the Home Assistant config as `/config/custom_components/vistapool`.

## Notes

- Logs: `docker logs -f homeassistant`
- Restart HA after code changes that affect component setup: `docker restart homeassistant`
- Linting: `ruff check .`
- Tests: `pytest -q`
