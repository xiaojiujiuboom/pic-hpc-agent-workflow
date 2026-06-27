#!/bin/bash
# 在 BLSC M9 上编译/运行 EPOCH 前 source 这个文件。

export HPCPIC_ROOT="${HPCPIC_ROOT:-$HOME/pic/hpc}"
export HPCPIC_BIN="${HPCPIC_BIN:-$HOME/pic/bin}"
export HPCPIC_EPOCH3D="${HPCPIC_EPOCH3D:-$HPCPIC_BIN/epoch3d}"

# 兼容旧变量名。早期文档使用过 LGBO_*，保留它们避免旧脚本失效。
export LGBO_ROOT="${LGBO_ROOT:-$HPCPIC_ROOT}"
export LGBO_BIN="${LGBO_BIN:-$HPCPIC_BIN}"
export LGBO_EPOCH3D="${LGBO_EPOCH3D:-$HPCPIC_EPOCH3D}"

export OMPI="${OMPI:-/publicfs10/fs10-share/soft/share-soft/openmpi/4.1.1}"
export AOCC="${AOCC:-/publicfs10/fs10-share/soft/share-soft/aocc/5.0.0}"
export HDF5="${HDF5:-/publicfs10/fs10-share/soft/share-soft/hdf5/hdf5-1.14.0-aocc}"

export PATH="$OMPI/bin:$AOCC/bin:$HDF5/bin:$PATH"
export LD_LIBRARY_PATH="$OMPI/lib:$AOCC/lib:$AOCC/lib64:$HDF5/lib:${LD_LIBRARY_PATH:-}"
