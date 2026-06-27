#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


def now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def block_summary(obj):
    data = getattr(obj, "data", None)
    dims = getattr(obj, "dims", None)
    shape = None
    if data is not None and hasattr(data, "shape"):
        shape = list(data.shape)
    elif dims is not None:
        try:
            shape = list(dims)
        except TypeError:
            shape = str(dims)
    return {
        "name": getattr(obj, "name", ""),
        "units": getattr(obj, "units", ""),
        "dims": list(dims) if isinstance(dims, tuple) else dims,
        "shape": shape,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: analyze_run.py RUN_DIR", file=sys.stderr)
        return 2

    run_dir = Path(sys.argv[1]).expanduser().resolve()
    data_dir = run_dir / "Data"
    sdf_files = sorted(data_dir.glob("*.sdf"))

    summary = {
        "run_dir": str(run_dir),
        "data_dir": str(data_dir),
        "analyzed_at": now(),
        "sdf_count": len(sdf_files),
        "sdf_files": [p.name for p in sdf_files],
    }

    metrics = {
        "run_dir": str(run_dir),
        "analyzed_at": summary["analyzed_at"],
        "sdf_count": len(sdf_files),
    }

    if not sdf_files:
        summary["error"] = "no SDF files found"
        metrics["analysis_status"] = "no_sdf"
    else:
        from sdf_helper import sdfr

        latest = sdf_files[-1]
        data = sdfr(str(latest))
        keys = [k for k in data.__dict__.keys() if not k.startswith("_")]
        summary["latest_sdf"] = latest.name
        summary["keys"] = keys
        summary["blocks"] = {
            key: block_summary(value)
            for key, value in data.__dict__.items()
            if not key.startswith("_") and hasattr(value, "__dict__")
        }
        metrics["analysis_status"] = "ok"
        metrics["latest_sdf"] = latest.name
        metrics["available_key_count"] = len(keys)
        metrics["has_particles"] = any("Particles" in key or "Particle" in key for key in keys)
        metrics["has_fields"] = any("Electric_Field" in key or "Magnetic_Field" in key for key in keys)

    with open(run_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    with open(run_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

