#!/usr/bin/env python3
from pathlib import Path
import argparse
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from picflow.core import CampaignConfig, load_config, run_dry


def create_bundle(config: CampaignConfig) -> dict[str, str]:
    result = run_dry(config)
    run_dir = Path(result["run_dir"])
    bundle_root = ROOT / "bundles"
    bundle_root.mkdir(exist_ok=True)
    bundle_dir = bundle_root / result["run_id"]

    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    shutil.copytree(
        run_dir,
        bundle_dir,
        ignore=shutil.ignore_patterns("plots", "metrics.json", "__pycache__", "*.pyc"),
    )
    shutil.copytree(
        ROOT / "remote_tools",
        bundle_dir / "tools",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    archive = bundle_root / f"{result['run_id']}.tar.gz"
    if archive.exists():
        archive.unlink()
    subprocess.run(
        ["tar", "-czf", str(archive), "-C", str(bundle_root), result["run_id"]],
        check=True,
    )

    return {
        "run_id": result["run_id"],
        "run_dir": str(run_dir),
        "bundle": str(archive),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a portable run bundle for BLSC.")
    parser.add_argument("--config", default="configs/lg_proton_mvp.json")
    args = parser.parse_args()

    result = create_bundle(load_config(args.config))
    archive = Path(result["bundle"])

    print(f"run_id={result['run_id']}")
    print(f"run_dir={result['run_dir']}")
    print(f"bundle={archive}")
    print()
    print("Remote install:")
    print("  mkdir -p ~/pic/hpc/runs")
    print(f"  tar -xzf {archive.name} -C ~/pic/hpc/runs")
    print(f"  cd ~/pic/hpc/runs/{result['run_id']}")
    print("  bash tools/submit_run.sh .")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
