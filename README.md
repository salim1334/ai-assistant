# BDFG — your business assistant

BDFG creates a **personal assistant** on your computer. It learns your business and suggests the next step. You do not need to be a programmer.

## What you need

- A computer (Linux, macOS, or Windows)
- [Python 3.10 or newer](https://www.python.org/downloads/)
- An internet connection the first time (to install packages and optionally download a small helper model)
- [Ollama](https://ollama.com) — free software so the assistant can talk on this computer without a paid cloud key

## Setup (about 10–15 minutes the first time)

### 1. Unpack this folder

Unzip the file you received. Open a terminal (Command Prompt or PowerShell on Windows, Terminal on Mac/Linux) and go into the folder:

```bash
cd enhanced_bdfg_framework
```

### 2. Create a fresh Python environment (recommended)

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install BDFG

```bash
pip install -e .
```

### 4. Install Ollama (once per computer)

- Visit [https://ollama.com](https://ollama.com) and install, **or**
- When the BDFG browser page opens, use **Install Ollama** if it asks you to.

### 5. Start BDFG

```bash
bdfg start
```

A browser page opens. The first launch:

1. Checks your computer
2. Picks a **small** helper model that fits (never a huge model on first run)
3. Downloads that helper only if it is not already installed
4. Asks one setup question at a time (business name, what you do, one goal, language)
5. Asks you to confirm, then **Start my assistant**

A cloud API key (OpenAI, Anthropic, or Gemini) is **optional**. You can add one later under “Use a cloud key”.

## After setup

- Talk in plain language.
- Check **What I remember** and the suggested next moves.
- Later launches skip the model download.
- To stop: close the browser tab and stop the terminal with `Ctrl+C`.

## If something goes wrong

| Problem | What to try |
|---------|-------------|
| `bdfg: command not found` | Activate the venv again, then `pip install -e .` |
| Browser does not open | Open [http://127.0.0.1:8765](http://127.0.0.1:8765) (or the URL printed in the terminal) |
| Ollama missing | Install from [ollama.com](https://ollama.com), then press Continue in the app |
| Model download stuck | Keep the terminal open; a small model can take several minutes on a slow connection |
| Port already in use | Close any other `bdfg start` window, or restart the computer |

## For developers (optional)

```bash
bdfg implement alarm-crm --output ./generated/alarm_crm
bdfg implement generic --output ./generated/shop --name "Lemma Cafe"
bdfg chat --root ./generated/alarm_crm --once "which sub-cities are dark?"
python -m enhanced_bdfg version
pytest
```

Heavy analytics libraries: `pip install -e ".[analytics]"`.

v1 does **not** include live Telebirr/Chapa, native retailer apps, or AWS hosting.

## License

MIT — see LICENSE.

## Support

If setup fails, send a screenshot of the terminal and the browser page to the person who shared this package with you.
