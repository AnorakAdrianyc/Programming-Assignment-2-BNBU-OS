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
- `scripts/check_c_syntax.sh` - checks C syntax on Ubuntu with `gcc -fsyntax-only`
- `.github/workflows/copilot-setup-steps.yml` - preinstalls Ubuntu tools in Copilot cloud agent

## Run locally

```bash
chmod +x scripts/setup_ubuntu_env.sh scripts/run_editor.sh scripts/check_c_syntax.sh
./scripts/setup_ubuntu_env.sh
python3 bridge/bridge_server.py
./scripts/run_editor.sh
```

## Check C syntax (Ubuntu Linux)

```bash
./scripts/check_c_syntax.sh path/to/file.c
./scripts/check_c_syntax.sh src/a.c src/b.c
```

Then open `http://127.0.0.1:8080`.
The editor calls `http://127.0.0.1:8000/bridge` for Python-backed analysis (with JS fallback).

## Use the modular editor environment

1. Start both services:
   - Bridge server: `python3 bridge/bridge_server.py`
   - Editor server: `./scripts/run_editor.sh`
2. Open `http://127.0.0.1:8080`.
3. In **C Editor (OS-focused)**, add or edit lines in this format:
   - `enqueue_process("P1", 3, 0);`
4. Click **Analyze with Python Bridge** to send parsed processes to `POST /bridge`.
   - If the bridge is unavailable, the editor automatically falls back to local JS FCFS computation.
5. Or click **Analyze Locally (JS)** to run FCFS directly in the browser.
6. Read results in:
   - **Python Bridge** output panel (JSON response)
   - **Process & Timeline Visualization** section (canvas timeline + metrics table)
7. Use **Frontend Editors (HTML / CSS / JS)** panes to prototype visualization markup/styles/scripts while testing scheduling inputs.
