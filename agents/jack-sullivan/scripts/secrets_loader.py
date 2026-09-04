#!/usr/bin/env python3
"""Load shared secrets from /root/agents/.env into os.environ.

Cron jobs already `source .env`, so vars are usually present. This loader
makes direct/interactive runs work too, without hardcoding secrets in source.
Import at the top of any script that needs EMAIL_PASSWORD / QUO_TOKEN, etc.
"""
import os
from pathlib import Path

ENV_PATH = Path("/root/agents/.env")


def load_env(path: Path = ENV_PATH) -> None:
    """Populate os.environ from a shell-style .env (only keys not already set)."""
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = line[len("export "):] if line.startswith("export ") else line
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        # Do not overwrite values already exported by the cron shell.
        if key and key not in os.environ:
            os.environ[key] = val


def require(key: str) -> str:
    """Return a required secret, raising a clear error if it is missing."""
    load_env()
    val = os.environ.get(key)
    if not val:
        raise RuntimeError(
            f"Missing required secret '{key}'. Add it to {ENV_PATH} "
            f"(export {key}=...) — do not hardcode it in source."
        )
    return val


# Load on import so module-level `os.environ[...]` reads succeed.
load_env()
