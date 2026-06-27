#!/bin/bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "usage: submit_run.sh RUN_DIR" >&2
  exit 2
fi

RUN_DIR="$1"
cd "$RUN_DIR"

if [ ! -f input.deck ]; then
  echo "missing input.deck in $RUN_DIR" >&2
  exit 2
fi

if [ ! -f submit.slurm ]; then
  echo "missing submit.slurm in $RUN_DIR" >&2
  exit 2
fi

mkdir -p Data logs
cp input.deck Data/input.deck

OUT="$(sbatch submit.slurm)"
echo "$OUT"
JOB_ID="$(printf "%s\n" "$OUT" | awk '/Submitted batch job/{print $4}')"

if [ -z "$JOB_ID" ]; then
  echo "could not parse sbatch job id" >&2
  exit 1
fi

printf "%s\n" "$JOB_ID" > job_id.txt
python3 - "$JOB_ID" <<'PY'
import json
import sys
from datetime import datetime

job_id = sys.argv[1]
status = {
    "job_id": job_id,
    "state": "SUBMITTED",
    "updated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
}
with open("status.json", "w") as f:
    json.dump(status, f, indent=2)
PY

