#!/usr/bin/env python3

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def run(cmd):
    proc = subprocess.run(
        cmd,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def main():
    if len(sys.argv) != 2:
        print("usage: monitor_run.py RUN_DIR", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1]).expanduser().resolve()
    job_file = run_dir / "job_id.txt"
    if not job_file.exists():
        print(f"missing {job_file}", file=sys.stderr)
        return 2

    job_id = job_file.read_text().strip()
    code, out, err = run([
        "sacct",
        "-j",
        job_id,
        "--format=JobID,JobName,Partition,State,ExitCode,Elapsed,NodeList",
        "--parsable2",
        "--noheader",
    ])

    status = {
        "job_id": job_id,
        "updated_at": now(),
        "sacct_returncode": code,
        "sacct_stdout": out.strip().splitlines(),
        "sacct_stderr": err.strip(),
    }

    if out.strip():
        first = out.strip().splitlines()[0].split("|")
        if len(first) >= 5:
            status.update({
                "state": first[3],
                "exit_code": first[4],
                "elapsed": first[5] if len(first) > 5 else "",
                "node_list": first[6] if len(first) > 6 else "",
            })
    else:
        q_code, q_out, q_err = run(["squeue", "-j", job_id, "-h", "-o", "%T|%M|%R"])
        status.update({
            "squeue_returncode": q_code,
            "squeue_stdout": q_out.strip(),
            "squeue_stderr": q_err.strip(),
        })
        if q_out.strip():
            parts = q_out.strip().split("|")
            status["state"] = parts[0]

    with open(run_dir / "status.json", "w") as f:
        json.dump(status, f, indent=2)

    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
