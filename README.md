# Kriva

Kriva is a local-first model router for software-engineering tasks. The current
implementation is the Phase 1 deterministic core: it reads the current Git
repository and diff, sends them with a task to one explicitly selected model,
prints the response, and records the attempt in a local SQLite database.

It does not yet classify tasks, choose a model automatically, edit files, or run
tests. Those capabilities belong to later roadmap phases.

## Requirements

- Python 3.10 or newer
- Git
- For the default local provider: [Ollama](https://ollama.com/) and the
  `qwen2.5-coder:7b` model
- Or an API key for one of the supported cloud providers

## Install

From the repository root, create and activate a virtual environment, then
install the project in editable mode:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

The install creates the `router` command.

## Configure providers

Ollama is the default and requires no cloud API key:

```powershell
ollama pull qwen2.5-coder:7b
```

Cloud providers read their keys from environment variables. You can set one in
PowerShell for the current session:

```powershell
$env:ANTHROPIC_API_KEY = "your-key"
$env:GROQ_API_KEY = "your-key"
$env:NVIDIA_API_KEY = "your-key"
```

Alternatively, put the variables you use in a `.env` file at the Kriva
repository root. The existing `src\.env` location is also supported. Kriva
loads these files from its own installation source, even when you run the CLI
from another repository. `.env` files are ignored by Git; do not commit API
keys.

| CLI provider | Environment variable | Default model |
| --- | --- | --- |
| `ollama` | — | `qwen2.5-coder:7b` |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-haiku-4-5-20251001` |
| `groq` | `GROQ_API_KEY` | `qwen/qwen3.8-27b` |
| `nvidia` | `NVIDIA_API_KEY` | `nvidia/nemotron-3-ultra-550b-a55b` |

The NVIDIA provider uses NVIDIA's OpenAI-compatible chat-completions endpoint.
Cloud requests send the task and the current Git diff to the selected provider;
avoid using it on repositories whose contents you cannot send to that service.

## Use

Run commands from inside a Git working tree:

```powershell
router ask "Explain the current changes"
router ask "Explain the current changes" --provider nvidia
router ask --help
router runs
router runs --n 20
```

`ask` reads the repository root, current commit SHA, and `git diff HEAD`. The
diff is capped at 8,000 characters. The selected provider receives the task
and that context, and the response is printed to the terminal. Provider
selection is manual in Phase 1; `--provider` does not perform adaptive routing.

## Run history

Runs are stored locally in SQLite at:

```text
%USERPROFILE%\.router\runs.db
```

Set `ROUTER_DB` to use another database path. Each run records the repository,
commit SHA, provider/model, task, model output, token counts, latency, whether
the model call completed, and any error. A successful log entry means the
model responded; it is not a test or correctness verdict.

The `router runs` command shows the most recent records. For example, the
database can also be queried with Python's SQLite tools or any SQLite client.

## Development and tests

Run the unit tests from the repository root:

```powershell
python -m unittest discover -s tests -v
```
