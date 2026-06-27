#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from picflow.core import load_config
from scripts.create_run_bundle import create_bundle


DONE_STATES = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "OUT_OF_MEMORY", "NODE_FAIL"}


@dataclass(frozen=True)
class Remote:
    host: str
    port: str
    user: str
    root: str

    @property
    def target(self) -> str:
        return f"{self.user}@{self.host}"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def remote_from_env() -> Remote:
    load_dotenv(ROOT / ".env")
    host = os.environ.get("HPCPIC_SSH_HOST") or os.environ.get("BLSC_SSH_HOST", "")
    port = os.environ.get("HPCPIC_SSH_PORT", "22")
    user = os.environ.get("HPCPIC_SSH_USER") or os.environ.get("BLSC_SSH_USER", "")
    root = os.environ.get("HPCPIC_REMOTE_ROOT") or os.environ.get("BLSC_REMOTE_ROOT", "")
    missing = [
        name
        for name, value in {
            "HPCPIC_SSH_HOST": host,
            "HPCPIC_SSH_USER": user,
            "HPCPIC_REMOTE_ROOT": root,
        }.items()
        if not value
    ]
    if missing:
        raise SystemExit(
            "缺少远程配置：" + ", ".join(missing) + "\n"
            "先执行：cp .env.example .env，然后按你的 SSH 信息填写。"
        )
    return Remote(host=host, port=port, user=user, root=root.rstrip("/"))


def run(cmd: list[str], *, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    shown = " ".join(shlex.quote(part) for part in cmd)
    print(f"$ {shown}")
    proc = subprocess.run(
        cmd,
        text=True,
        check=False,
        capture_output=capture,
    )
    if check and proc.returncode != 0:
        if capture:
            if proc.stdout:
                print(proc.stdout, end="")
            if proc.stderr:
                print(proc.stderr, end="", file=sys.stderr)
        raise SystemExit(proc.returncode)
    return proc


def ssh(remote: Remote, command: str, *, capture: bool = False, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(
        [
            "ssh",
            "-p",
            remote.port,
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=accept-new",
            remote.target,
            command,
        ],
        capture=capture,
        check=check,
    )


def scp_to(remote: Remote, local: Path, remote_dir: str) -> None:
    run([
        "scp",
        "-P",
        remote.port,
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        str(local),
        f"{remote.target}:{remote_dir}/",
    ])


def scp_from(remote: Remote, remote_path: str, local_dir: Path) -> None:
    local_dir.mkdir(parents=True, exist_ok=True)
    run([
        "scp",
        "-P",
        remote.port,
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{remote.target}:{remote_path}",
        str(local_dir) + "/",
    ], check=False)


def remote_run_dir(remote: Remote, run_id: str) -> str:
    return f"{remote.root}/{run_id}"


def action_probe(remote: Remote) -> None:
    ssh(remote, "hostname && pwd && command -v sbatch && command -v python3")


def action_bundle(config_path: str) -> dict[str, str]:
    result = create_bundle(load_config(config_path))
    print(f"run_id={result['run_id']}")
    print(f"bundle={result['bundle']}")
    return result


def action_upload(remote: Remote, bundle: Path, run_id: str) -> None:
    archive_name = bundle.name
    q_root = shlex.quote(remote.root)
    ssh(remote, f"mkdir -p {q_root}")
    scp_to(remote, bundle, remote.root)
    ssh(remote, f"tar -xzf {shlex.quote(remote.root + '/' + archive_name)} -C {q_root}")
    print(f"远端目录：{remote_run_dir(remote, run_id)}")


def action_submit(remote: Remote, run_id: str) -> None:
    q_dir = shlex.quote(remote_run_dir(remote, run_id))
    ssh(remote, f"cd {q_dir} && source tools/hpcpic_env.sh && bash tools/submit_run.sh .")


def action_monitor(remote: Remote, run_id: str, *, wait: bool = False, interval: int = 30) -> None:
    q_dir = shlex.quote(remote_run_dir(remote, run_id))
    while True:
        proc = ssh(remote, f"cd {q_dir} && python3 tools/monitor_run.py .", capture=True)
        text = proc.stdout or ""
        print(text, end="" if text.endswith("\n") else "\n")
        if not wait:
            return
        state = ""
        for line in text.splitlines():
            if '"state":' in line:
                state = line.split(":", 1)[1].strip().strip('",')
                break
        if state in DONE_STATES:
            return
        print(f"状态 {state or 'unknown'}，{interval}s 后继续查...")
        time.sleep(interval)


def action_analyze(remote: Remote, run_id: str) -> None:
    q_dir = shlex.quote(remote_run_dir(remote, run_id))
    ssh(remote, f"cd {q_dir} && source tools/hpcpic_env.sh && python3 tools/analyze_run.py .")


def action_fetch(remote: Remote, run_id: str) -> None:
    local_dir = ROOT / "runs" / run_id / "remote_results"
    remote_dir = remote_run_dir(remote, run_id)
    for name in ["status.json", "metrics.json", "summary.json", "job_id.txt"]:
        scp_from(remote, f"{remote_dir}/{name}", local_dir)
    # 可选结果，不存在也不报错。
    scp_from(remote, f"{remote_dir}/*.csv", local_dir)
    scp_from(remote, f"{remote_dir}/plots/*.png", local_dir / "plots")
    scp_from(remote, f"{remote_dir}/plots/*.svg", local_dir / "plots")
    print(f"小结果已拉回：{local_dir}")


def existing_bundle(run_id: str) -> Path:
    bundle = ROOT / "bundles" / f"{run_id}.tar.gz"
    if not bundle.exists():
        raise SystemExit(f"找不到任务包：{bundle}")
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="自动上传、提交、监控、分析远端 PIC/EPOCH 任务。")
    sub = parser.add_subparsers(dest="command", required=True)

    p_bundle = sub.add_parser("bundle", help="只生成任务包")
    p_bundle.add_argument("--config", default="configs/lg_proton_mvp.json")

    sub.add_parser("probe", help="测试 SSH 连接")

    p_upload = sub.add_parser("upload", help="上传并解压任务包")
    p_upload.add_argument("--run-id", required=True)
    p_upload.add_argument("--bundle")

    p_submit = sub.add_parser("submit", help="远端提交任务")
    p_submit.add_argument("--run-id", required=True)

    p_monitor = sub.add_parser("monitor", help="远端查询任务状态")
    p_monitor.add_argument("--run-id", required=True)
    p_monitor.add_argument("--wait", action="store_true")
    p_monitor.add_argument("--interval", type=int, default=30)

    p_analyze = sub.add_parser("analyze", help="远端分析 SDF")
    p_analyze.add_argument("--run-id", required=True)

    p_fetch = sub.add_parser("fetch", help="拉回小结果")
    p_fetch.add_argument("--run-id", required=True)

    p_all = sub.add_parser("all", help="生成、上传、提交；可选等待完成后分析并拉回")
    p_all.add_argument("--config", default="configs/lg_proton_mvp.json")
    p_all.add_argument("--wait", action="store_true")
    p_all.add_argument("--interval", type=int, default=30)

    args = parser.parse_args()
    if args.command == "bundle":
        action_bundle(args.config)
        return 0

    remote = remote_from_env()
    if args.command == "probe":
        action_probe(remote)
    elif args.command == "upload":
        action_upload(remote, Path(args.bundle) if args.bundle else existing_bundle(args.run_id), args.run_id)
    elif args.command == "submit":
        action_submit(remote, args.run_id)
    elif args.command == "monitor":
        action_monitor(remote, args.run_id, wait=args.wait, interval=args.interval)
    elif args.command == "analyze":
        action_analyze(remote, args.run_id)
    elif args.command == "fetch":
        action_fetch(remote, args.run_id)
    elif args.command == "all":
        result = action_bundle(args.config)
        run_id = result["run_id"]
        action_upload(remote, Path(result["bundle"]), run_id)
        action_submit(remote, run_id)
        if args.wait:
            action_monitor(remote, run_id, wait=True, interval=args.interval)
            action_analyze(remote, run_id)
            action_fetch(remote, run_id)
        else:
            print("已提交。之后查询：")
            print(f"  python3 scripts/remote_run.py monitor --run-id {run_id}")
            print(f"  python3 scripts/remote_run.py analyze --run-id {run_id}")
            print(f"  python3 scripts/remote_run.py fetch --run-id {run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
