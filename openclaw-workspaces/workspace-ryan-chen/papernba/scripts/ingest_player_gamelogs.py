#!/usr/bin/env python3
"""Runner script for player game log ingestion."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from ingestion.player_gamelogs import ingest, verify

if __name__ == "__main__":
    ingest()
    verify()
