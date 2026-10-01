"""Step 6: the CLI. CLI -> repo -> provider -> print -> log."""
import asyncio

import typer

from .db import log_run, recent_runs
from .providers import PROVIDERS
from .repo import NotAGitRepo, read_repo

app = typer.Typer(help="Adaptive model router (Phase 1: deterministic core)")


@app.callback()
def main():
    """Adaptive model router."""
    # This callback keeps `ask` a real subcommand (Typer collapses
    # single-command apps otherwise).


@app.command()
def ask(
    task: str = typer.Argument(..., help="What you want the model to do"),
    provider: str = typer.Option(
        "ollama", help="Hardcoded for now (Phase 2 replaces this with a router): "
                       + " | ".join(PROVIDERS)),
):
    """Send TASK plus the current git diff to a single hardcoded model."""
    if provider not in PROVIDERS:
        typer.echo(f"Unknown provider '{provider}'. Choose from: {', '.join(PROVIDERS)}", err=True)
        raise typer.Exit(2)

    try:
        info = read_repo(".")
    except NotAGitRepo as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(2)

    model = PROVIDERS[provider]()
    context = (
        f"Repo: {info['root']}\n\n"
        f"Current git diff:\n{info['diff'] or '(no changes)'}"
    )

    record = dict(
        repo=info["root"], commit_sha=info["commit_sha"],
        provider=model.name, model=model.model, prompt=task,
        output=None, tokens_in=0, tokens_out=0, latency_ms=0,
        success=0, error=None,
    )
    exit_code = 0
    try:
        result = asyncio.run(model.generate(task, context))
        record.update(
            output=result.text, tokens_in=result.tokens_in,
            tokens_out=result.tokens_out, latency_ms=result.latency_ms,
            success=1,
        )
        typer.echo(result.text)
    except Exception as e:  # log failures too: Phase 5 learns from them
        record["error"] = f"{type(e).__name__}: {e}"
        typer.echo(f"Error: {record['error']}", err=True)
        exit_code = 1
    finally:
        log_run(**record)

    if exit_code:
        raise typer.Exit(exit_code)


@app.command()
def runs(n: int = typer.Option(10, help="How many recent runs to show")):
    """Show the last N logged runs."""
    rows = recent_runs(n)
    if not rows:
        typer.echo("No runs logged yet.")
        return
    typer.echo("id | created_at | provider | model | tok_in | tok_out | ms | ok")
    for row in rows:
        typer.echo(" | ".join(str(c) for c in row))
