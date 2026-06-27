# LGBO 3D PIC Control Plane

This project packages a workflow for 3D EPOCH PIC campaigns on a remote supercomputer.

Goal:

- Use EPOCH on the cluster for expensive 3D runs.
- Keep large `.sdf` files on the cluster.
- Run lightweight analysis on the cluster.
- Fetch only `metrics.json`, `summary.json`, CSV, and PNG files for local Bayesian optimization and plotting.

The first target campaign is LG beam + target Bayesian optimization for proton/photon diagnostics.

中文零基础手册见 [docs/ZERO_START_zh.md](docs/ZERO_START_zh.md)。
如果你是第一次接触这个项目，从那里开始，不要从源码开始猜。

## What Is Already Verified

On BLSC M9:

- Slurm submission works.
- OpenMPI 4.1.1 + AOCC/flang 5.0.0 works with `mpirun`.
- EPOCH 4.20.1 `epoch3d` compiles and runs.
- EPOCH smoke run generates SDF files.
- Python SDF reader works with `from sdf_helper import sdfr`.
- A remote `summary.json` can be generated from `Data/0000.sdf`.

Detailed cluster notes are in [docs/remote_probe.md](docs/remote_probe.md).

## Local Quick Start

If this is a fresh computer, install Git and Python first. The full beginner flow is in
[docs/ZERO_START_zh.md](docs/ZERO_START_zh.md).

Create a local dry-run:

```bash
python3 scripts/dry_run.py --config configs/lg_proton_mvp.json
```

Create a portable run bundle:

```bash
python3 scripts/create_run_bundle.py --config configs/lg_proton_mvp.json
```

This writes:

```text
bundles/<run_id>.tar.gz
```

Upload that tarball to the cluster, then install it under:

```text
~/pic/lgbo/runs/
```

## Remote Foolproof Steps

On the cluster:

```bash
mkdir -p ~/pic/lgbo/runs
cd ~/pic/lgbo/runs
tar -xzf <run_id>.tar.gz
cd <run_id>
source tools/lgbo_env.sh
bash tools/submit_run.sh .
```

Check status:

```bash
python3 tools/monitor_run.py .
cat status.json
```

After the job completes:

```bash
python3 tools/analyze_run.py .
cat metrics.json
cat summary.json | head -80
```

Fetch only small files back to local:

```text
status.json
metrics.json
summary.json
plots/*.png
*.csv
```

Do not fetch full 3D SDF files by default.

## Remote Directory Convention

```text
~/pic/
  bin/
    epoch3d
  software/
    epoch_release-4.20.1/
  lgbo/
    runs/
      <run_id>/
        config.json
        input.deck
        submit.slurm
        job_id.txt
        status.json
        metrics.json
        summary.json
        Data/
        tools/
```

## Important Cluster Details

Use this launch pattern:

```bash
mkdir -p Data
cp input.deck Data/input.deck
printf "Data\ninput.deck\n" | mpirun --mca btl ^openib -np <ntasks> ~/pic/bin/epoch3d
```

Reason: EPOCH asks first for the output directory and then for the deck filename. With output directory `Data`, the deck must exist as `Data/input.deck`.

## Static Guide

Generate a self-contained HTML guide:

```bash
python3 scripts/render_docs.py
```

Open:

```text
docs/index.html
```

To put the guide on GitHub Pages or another Git host, follow
[docs/GITHUB_PAGES_zh.md](docs/GITHUB_PAGES_zh.md).
