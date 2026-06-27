# Remote Probe Checklist

Before enabling real submissions, confirm these items on the BLSC environment:

1. Shell access method: browser SSH app, native SSH host, or cloud desktop terminal.
2. Scheduler: Slurm (`sbatch`, `squeue`) or PBS (`qsub`, `qstat`).
3. EPOCH location: module name, compiled binary path, MPI launcher.
4. Project storage: remote work root, scratch path, quota, purge policy.
5. Job limits: maximum nodes, cores per node, walltime, queue names.
6. Data transfer: preferred path for reduced diagnostics and SDF files.

The first real run should be a non-physics smoke test that prints environment variables and exits.

## BLSC M9 Notes

Observed on 2026-06-27:

- Login node: `ln1`.
- User home: `/publicfs10/fs10-m9/home/m9s003861`.
- Scheduler: Slurm, with `sbatch`, `squeue`, and `sinfo` under `/opt/slurm/slurm/bin`.
- Smoke-test job was routed to partition `amd_m9_76`, but explicitly requesting that partition later failed with "invalid partition specified". Leave `#SBATCH -p` unset unless `sinfo` or support confirms a valid submit partition.
- Compute-node smoke test ran on `wqd10nbe11c05`.
- Slurm `mpiexec` failed for an OpenMPI-compiled test program. Use OpenMPI 4.1.1 `mpirun` instead.
- Verified MPI stack: OpenMPI 4.1.1 + AOCC/flang 5.0.0. A 4-rank Fortran MPI hello job completed on `wqd10nbe11c02`.
- EPOCH prompts on stdin for the output directory and then the input deck path. With output directory `Data` and deck name `input.deck`, it looks for `Data/input.deck`, so copy the deck there before launch: `mkdir -p Data && cp input.deck Data/input.deck && printf "Data\ninput.deck\n" | epoch3d`.
- Add `--mca btl ^openib` to OpenMPI `mpirun` on this cluster to avoid OpenFabrics initialization warnings.
- `module list` failed inside the job because `/usr/share/Modules/libexec/modulecmd.tcl` was missing. Avoid depending on environment modules until the cluster module setup is clarified.
- `epoch2d` and `epoch3d` were not in the default `PATH`.
- Storage quota on `publicfs10`: 450 GB soft limit, 500 GB hard limit. Usage was 78.6 GB during the initial probe.
- EPOCH 4.20.1 `epoch3d` compiled successfully under `~/pic/software/epoch_release-4.20.1/epoch3d/bin/epoch3d`.
- Build command used OpenMPI wrapper with `COMPILER=gfortran`, `MPIF90=$OMPI/bin/mpif90`, `ENC=no`, and `DONE_COMMIT=1`.
- Because `$OMPI/bin/mpif90` uses AOCC/flang, EPOCH's gfortran-specific `-ffpe-summary=invalid,zero,overflow` flag had to be removed from `epoch3d/Makefile` before building.
- `~/pic/bin/epoch3d` was copied as the stable executable path.
- EPOCH smoke job `1162368` completed successfully and generated `Data/0000.sdf` and `Data/0001.sdf`.
- SDF Python reader installed successfully after offline-installing `numpy-1.16.6-cp36-cp36m-manylinux1_x86_64.whl`.
- SDF smoke succeeded with `from sdf_helper import sdfr`, reading `~/pic/lgbo/epoch_smoke/Data/0000.sdf` and writing `~/pic/lgbo/epoch_smoke/summary.json`.

Minimal verified flow:

```bash
mkdir -p ~/pic/lgbo/smoke
cd ~/pic/lgbo/smoke
sbatch smoke.slurm
squeue -u "$USER"
```
