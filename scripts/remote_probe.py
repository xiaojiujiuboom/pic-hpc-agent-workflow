#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from picflow.remote import RemoteConfig, probe_commands, run_remote


def main() -> int:
    config = RemoteConfig.from_env()
    for command in probe_commands():
        print(f"\n$ {command}")
        result = run_remote(config, command)
        print(result.stdout.rstrip())
        if result.stderr.strip():
            print(result.stderr.rstrip(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

