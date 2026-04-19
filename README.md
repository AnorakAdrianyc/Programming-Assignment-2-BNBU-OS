# Programming-Assignment-2-BNBU-OS

A modular, bare-bones Ubuntu-oriented coding environment for OS-focused C development with:

- C editor workspace for scheduling/process code
- Python bridge (`bridge/bridge_server.py`) for analysis integration
- HTML/CSS/JS frontend editor panes and visualization elements

## Structure

- `editor/` - minimal web editor UI (`index.html`, `style.css`, `app.js`)
- `bridge/` - Python HTTP bridge endpoint for scheduling timeline data
- `scripts/setup_ubuntu_env.sh` - installs Ubuntu dependencies for C + Python workflow
- `scripts/run_editor.sh` - runs the editor server (use bridge server separately)
- `.github/workflows/copilot-setup-steps.yml` - preinstalls Ubuntu tools in Copilot cloud agent

## Run locally

```bash
chmod +x scripts/setup_ubuntu_env.sh scripts/run_editor.sh
./scripts/setup_ubuntu_env.sh
python3 bridge/bridge_server.py
./scripts/run_editor.sh
```

Then open `http://127.0.0.1:8080`.
The editor calls `http://127.0.0.1:8000/bridge` for Python-backed analysis (with JS fallback).
