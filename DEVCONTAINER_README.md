# Vistapool Devcontainer Quickstart

## Prerequisites

- Docker installed on the host.
- VS Code with the "Dev Containers" extension.
- On macOS/Linux, your user must be able to access the Docker socket.

## How to use

1. Open the repository root in VS Code.
2. When prompted, choose **Reopen in Container** (or run the command manually).
3. Wait until the container initializes. It will automatically:
   - Build a custom Docker image with Home Assistant Core and development tools
   - Run `.devcontainer/init-ha.sh` to set up the environment
   - Mount your code to `/workspace` and `/config/custom_components/vistapool`
4. Open http://localhost:8123 in your browser to access Home Assistant.
5. Your integration code under `custom_components/vistapool` is automatically available in HA.

## Development workflow

- **Workspace**: Your code is available at `/workspace` inside the container
- **Code formatting**: Black formatter runs automatically on save
- **Type checking**: Pylance with Home Assistant libraries configured
- **Testing**: Run `pytest tests/` with coverage reporting

## Useful commands

- **Tests with coverage**: `pytest tests/ --cov=custom_components/vistapool --cov-report=term-missing -q`
- **Linting**: Use Black formatter (auto-formats on save) or `ruff check .` if available
- **Home Assistant logs**: Check VS Code terminal or HA web interface
- **Restart HA**: Restart the devcontainer when making structural changes

## Notes

- Home Assistant runs directly inside the devcontainer (no separate Docker container)
- Port 8123 is automatically forwarded and opens in browser
- All dependencies and dev tools are pre-installed in the container image
