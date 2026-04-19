# Programming-Assignment-2-BNBU-OS

A modular, bare-bones coding environment for OS-focused C development with cross-device dependency setup and Ubuntu Linux C syntax validation support:

- C editor workspace for scheduling/process code
- Python bridge (`bridge/bridge_server.py`) for analysis integration
- HTML/CSS/JS frontend editor panes and visualization elements

## Structure

- `editor/` - minimal web editor UI (`index.html`, `style.css`, `app.js`)
- `bridge/` - Python HTTP bridge endpoint for scheduling timeline data
- `scripts/setup_env.sh` - installs dependencies for C + Python workflow across supported package managers
- `scripts/setup_ubuntu_env.sh` - compatibility wrapper that calls `scripts/setup_env.sh`
- `scripts/run_editor.sh` - runs the editor server (use bridge server separately)
- `scripts/check_c_syntax.sh` - checks C syntax on Ubuntu with `gcc -fsyntax-only`
- `.github/workflows/copilot-setup-steps.yml` - preinstalls Ubuntu tools in Copilot cloud agent
- `requirements.txt` - Python packages for the bridge server (`requests` for HTTP, including Ollama API calls)

## Python dependencies (bridge)

Create and use a virtual environment (`.venv` in this repo folder, or in a parent workspace folder), then install the bridge requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

On Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Update an existing venv

After pulling changes or editing `requirements.txt`, refresh packages (with the venv activated):

```bash
pip install --upgrade -r requirements.txt
```

Windows (PowerShell), using the venv’s interpreter without activating:

```powershell
& .\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
```

If `.venv` sits next to this repo (one level up), from the repo root use:

```powershell
& ..\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
```

If `requirements.txt` is not the current directory, pass its full path.

## Run locally

**Linux / macOS**

```bash
chmod +x scripts/setup_env.sh scripts/setup_ubuntu_env.sh scripts/run_editor.sh scripts/check_c_syntax.sh
./scripts/setup_env.sh
source .venv/bin/activate   # if using a venv
pip install -r requirements.txt
python3 bridge/bridge_server.py
./scripts/run_editor.sh
```

With both processes running, open [http://127.0.0.1:8080](http://127.0.0.1:8080) for the UI. The editor calls [http://127.0.0.1:8000/bridge](http://127.0.0.1:8000/bridge) for Python-backed analysis (with a JS fallback if the bridge is down).

**Windows (PowerShell)** — from the repo root, with a venv that has `requirements.txt` installed:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned  # if Activate.ps1 is blocked
& .\.venv\Scripts\python.exe .\bridge\bridge_server.py
```

In a second terminal, serve the editor (same as `scripts/run_editor.sh`):

```powershell
cd editor
python -m http.server 8080
```

Then open [http://127.0.0.1:8080](http://127.0.0.1:8080); the bridge listens on [http://127.0.0.1:8000](http://127.0.0.1:8000) (see Linux/macOS steps above for the same layout).

### Modular dependency setup (cross-device)

`scripts/setup_env.sh` auto-detects and uses one of these package managers:

- `apt-get` (Debian/Ubuntu)
- `dnf` (Fedora/RHEL)
- `pacman` (Arch Linux)
- `zypper` (openSUSE)
- `brew` (macOS/Linuxbrew)

Required tools are consistent on all supported systems:

- `gcc`
- `gdb`
- `make`
- `python3`
- `pip3`
- Python `venv` support

Check-only mode (no install):

```bash
./scripts/setup_env.sh --check-only
```

## Check C syntax (Ubuntu Linux)

```bash
./scripts/check_c_syntax.sh path/to/file.c
./scripts/check_c_syntax.sh src/a.c src/b.c
```

## Use the modular editor environment

1. Start both services:
   - Bridge server: `python3 bridge/bridge_server.py` (from the repo root, with the venv active if you use one)
   - Editor server: `./scripts/run_editor.sh`, or on Windows: `cd editor` then `python -m http.server 8080`
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

### Optional: Ollama (local LLM)

Endpoints such as `GET /cursor/ollama/models` and `POST /cursor/ollama/generate` expect [Ollama](https://ollama.com/) running at `http://localhost:11434` (default). Install Ollama separately and pull a model; otherwise those routes will fail while FCFS and C validation endpoints still work.
