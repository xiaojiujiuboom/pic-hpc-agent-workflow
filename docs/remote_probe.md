# 北京超算远端环境记录

这份文档记录我们已经在 BLSC M9 上验证过的事情。

以后如果换账号、换分区、换超算，需要重新做类似检查。

## 上机前要确认什么

在真正提交 EPOCH 任务前，先确认：

1. 用什么方式登录：网页终端、客户端 SSH、还是本机 SSH。
2. 调度系统是什么：Slurm 还是 PBS。
3. EPOCH 在哪里：已有模块、已有二进制，还是需要自己编译。
4. MPI 怎么跑：`mpirun`、`mpiexec`、`srun` 哪个能用。
5. 项目目录放哪里：home、scratch、publicfs，是否有清理策略。
6. 存储配额是多少。
7. 最大节点数、核数、作业数、最长时间是多少。
8. 大文件如何处理：是否只传小结果，不传完整 SDF。

## BLSC M9 已验证信息

观察日期：2026-06-27。

- 登录节点：`ln1`
- 用户 home：`/publicfs10/fs10-m9/home/m9s003861`
- 调度系统：Slurm
- `sbatch`、`squeue`、`sinfo` 位于 `/opt/slurm/slurm/bin`
- 冒烟测试任务曾被路由到 `amd_m9_76`
- 但手动写 `#SBATCH -p amd_m9_76` 失败，提示分区无效
- 结论：当前模板不要写 `#SBATCH -p`
- 计算节点示例：`wqd10nbe11c02`、`wqd10nbe11c04`、`wqd10nbe11c05`

## MPI

Slurm 自带的：

```text
/opt/slurm/slurm/bin/mpiexec
```

对 OpenMPI 编译出来的测试程序不合适。

已验证可用的是：

```text
/publicfs10/fs10-share/soft/share-soft/openmpi/4.1.1/bin/mpirun
```

配套环境：

```bash
OMPI=/publicfs10/fs10-share/soft/share-soft/openmpi/4.1.1
AOCC=/publicfs10/fs10-share/soft/share-soft/aocc/5.0.0
HDF5=/publicfs10/fs10-share/soft/share-soft/hdf5/hdf5-1.14.0-aocc
export PATH=$OMPI/bin:$AOCC/bin:$HDF5/bin:$PATH
export LD_LIBRARY_PATH=$OMPI/lib:$AOCC/lib:$AOCC/lib64:$HDF5/lib:${LD_LIBRARY_PATH:-}
```

运行时建议加：

```bash
--mca btl ^openib
```

这样可以避免 OpenFabrics 初始化警告。

## HDF5

已找到并使用：

```text
/publicfs10/fs10-share/soft/share-soft/hdf5/hdf5-1.14.0-aocc
```

该 HDF5 是 parallel HDF5。

## EPOCH 编译记录

EPOCH 版本：

```text
4.20.1
```

源码目录：

```text
~/pic/software/epoch_release-4.20.1
```

稳定二进制路径：

```text
~/pic/bin/epoch3d
```

编译时使用：

```bash
OMPI=/publicfs10/fs10-share/soft/share-soft/openmpi/4.1.1
AOCC=/publicfs10/fs10-share/soft/share-soft/aocc/5.0.0
export PATH=$OMPI/bin:$AOCC/bin:$PATH
export LD_LIBRARY_PATH=$OMPI/lib:$AOCC/lib:$AOCC/lib64:${LD_LIBRARY_PATH:-}

cd ~/pic/software/epoch_release-4.20.1/epoch3d
perl -pi -e 's/ -ffpe-summary=invalid,zero,overflow//g' Makefile
make COMPILER=gfortran MPIF90=$OMPI/bin/mpif90 ENC=no DONE_COMMIT=1 -j 2
mkdir -p ~/pic/bin
cp bin/epoch3d ~/pic/bin/epoch3d
```

为什么要删 `-ffpe-summary=invalid,zero,overflow`：

```text
虽然 Makefile 走 COMPILER=gfortran 分支，但实际 mpif90 后端是 AOCC/flang。
flang 不认识 gfortran 的 -ffpe-summary 参数。
```

## EPOCH 运行方式

正确形状：

```bash
mkdir -p Data
cp input.deck Data/input.deck
printf "Data\ninput.deck\n" | mpirun --mca btl ^openib -np 1 ~/pic/bin/epoch3d
```

不要直接：

```bash
epoch3d < input.deck
```

原因：

```text
EPOCH 不是直接把 stdin 当 deck。
它先问输出目录，再问 deck 文件名。
```

已成功冒烟测试：

```text
作业号：1162368
状态：COMPLETED 0:0
输出：Data/0000.sdf, Data/0001.sdf
```

## Python SDF reader

远端 Python：

```text
Python 3.6.8
```

可用 numpy wheel：

```text
numpy-1.16.6-cp36-cp36m-manylinux1_x86_64.whl
```

安装成功后，SDF reader 验证：

```bash
python3 - <<'EOF'
import sdf
from sdf_helper import sdfr
print("sdf ok")
print("sdfr ok")
EOF
```

已验证可以读取：

```text
~/pic/lgbo/epoch_smoke/Data/0000.sdf
```

并生成：

```text
~/pic/lgbo/epoch_smoke/summary.json
```

## 存储配额

`publicfs10` 配额记录：

```text
Soft Limit : 450.0 GB
Hard Limit : 500.0 GB
Usage      : 78.6 GB
```

结论：

```text
3D SDF 不要默认下载到本地。
先在远端分析，再只传小结果。
```
