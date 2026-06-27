#!/bin/bash
# Source this file on the BLSC M9 cluster before compiling/running EPOCH.

export LGBO_ROOT="${LGBO_ROOT:-$HOME/pic/lgbo}"
export LGBO_BIN="${LGBO_BIN:-$HOME/pic/bin}"
export LGBO_EPOCH3D="${LGBO_EPOCH3D:-$LGBO_BIN/epoch3d}"

export OMPI="${OMPI:-/publicfs10/fs10-share/soft/share-soft/openmpi/4.1.1}"
export AOCC="${AOCC:-/publicfs10/fs10-share/soft/share-soft/aocc/5.0.0}"
export HDF5="${HDF5:-/publicfs10/fs10-share/soft/share-soft/hdf5/hdf5-1.14.0-aocc}"

export PATH="$OMPI/bin:$AOCC/bin:$HDF5/bin:$PATH"
export LD_LIBRARY_PATH="$OMPI/lib:$AOCC/lib:$AOCC/lib64:$HDF5/lib:${LD_LIBRARY_PATH:-}"

