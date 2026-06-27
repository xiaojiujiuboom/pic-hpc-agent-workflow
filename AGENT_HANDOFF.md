# Agent Handoff

You are continuing a 3D PIC workflow project in `/Users/boom/Documents/3dpic`.

User intent:

- Build a portable agent-assisted workflow for EPOCH 3D PIC campaigns on BLSC.
- Optimize LG beam parameters and target parameters using Bayesian optimization.
- Do not transfer large 3D SDF files to local by default.
- Run heavy analysis remotely and fetch lightweight outputs only.

Current verified remote facts:

- Cluster user: `m9s003861`.
- Login node observed: `ln1`.
- Remote home: `/publicfs10/fs10-m9/home/m9s003861`.
- Stable EPOCH path: `~/pic/bin/epoch3d`.
- Remote run root: `~/pic/lgbo/runs`.
- Scheduler: Slurm.
- Do not explicitly request partition `amd_m9_76`; Slurm routes jobs there automatically.
- OpenMPI launcher works: `/publicfs10/fs10-share/soft/share-soft/openmpi/4.1.1/bin/mpirun`.
- Use `--mca btl ^openib` to avoid OpenFabrics warnings.
- Python SDF reader works with `from sdf_helper import sdfr`.

Verified EPOCH launch shape:

```bash
mkdir -p Data
cp input.deck Data/input.deck
printf "Data\ninput.deck\n" | mpirun --mca btl ^openib -np 1 ~/pic/bin/epoch3d
```

Local scripts:

- `scripts/dry_run.py`: generate local run files and synthetic metrics.
- `scripts/create_run_bundle.py`: package a run and `remote_tools/` for upload.
- `scripts/render_docs.py`: generate `docs/site/index.html`.

Remote tools:

- `remote_tools/lgbo_env.sh`
- `remote_tools/submit_run.sh`
- `remote_tools/monitor_run.py`
- `remote_tools/analyze_run.py`

Next practical work:

1. Use `scripts/create_run_bundle.py` to make a bundle.
2. Upload bundle to `~/pic/lgbo/runs`.
3. Run `bash tools/submit_run.sh .`.
4. Monitor with `python3 tools/monitor_run.py .`.
5. Analyze with `python3 tools/analyze_run.py .`.
6. Extend `analyze_run.py` to compute actual proton/photon metrics from production SDF variables.

