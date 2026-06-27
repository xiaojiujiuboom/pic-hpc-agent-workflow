from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class RemoteConfig:
    host: str
    user: str
    remote_root: str

    @classmethod
    def from_env(cls) -> "RemoteConfig":
        host = os.environ.get("BLSC_SSH_HOST", "").strip()
        user = os.environ.get("BLSC_SSH_USER", "").strip()
        remote_root = os.environ.get("BLSC_REMOTE_ROOT", "").strip()
        missing = [name for name, value in {
            "BLSC_SSH_HOST": host,
            "BLSC_SSH_USER": user,
            "BLSC_REMOTE_ROOT": remote_root,
        }.items() if not value]
        if missing:
            raise RuntimeError("Missing remote environment variables: " + ", ".join(missing))
        return cls(host=host, user=user, remote_root=remote_root)


def ssh_target(config: RemoteConfig) -> str:
    return f"{config.user}@{config.host}"


def run_remote(config: RemoteConfig, command: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["ssh", "-o", "BatchMode=yes", ssh_target(config), command],
        check=False,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def probe_commands() -> list[str]:
    return [
        "hostname",
        "pwd",
        "which sbatch || true",
        "which squeue || true",
        "which qsub || true",
        "which qstat || true",
        "module avail epoch 2>&1 | head -80 || true",
        "which epoch3d || which epoch2d || true",
    ]

