#!/bin/bash
#SBATCH -J {{job_name}}
#SBATCH -N {{nodes}}
#SBATCH -n {{ntasks}}
#SBATCH -t {{time}}
#SBATCH -o slurm.%j.out
#SBATCH -e slurm.%j.err

set -euo pipefail

OMPI={{ompi_root}}
AOCC={{aocc_root}}
HDF5={{hdf5_root}}
export PATH=$OMPI/bin:$AOCC/bin:$HDF5/bin:$PATH
export LD_LIBRARY_PATH=$OMPI/lib:$AOCC/lib:$AOCC/lib64:$HDF5/lib:${LD_LIBRARY_PATH:-}

echo "=== JOB ==="
date
hostname
whoami
pwd

echo "=== SLURM ==="
echo "SLURM_JOB_ID=${SLURM_JOB_ID:-}"
echo "SLURM_JOB_NODELIST=${SLURM_JOB_NODELIST:-}"
echo "SLURM_NTASKS=${SLURM_NTASKS:-}"

echo "=== RUN ==="
mkdir -p Data
cp input.deck Data/input.deck
printf "Data\ninput.deck\n" | {{launcher}} --mca btl ^openib -np {{ntasks}} {{epoch_binary}}

echo "=== DONE ==="
date
