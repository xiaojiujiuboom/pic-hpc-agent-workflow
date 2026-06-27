# Agent 交接说明

你正在接手这个项目：

```text
/Users/boom/Documents/3dpic
```

项目目的：

- 为北京超级云计算中心上的 EPOCH 3D PIC 任务建立可迁移工作流。
- 用贝叶斯优化扫描 LG 光束参数和靶参数。
- 大型 3D SDF 文件默认不传回本地。
- 重分析尽量放在超算端，本地只拿小结果文件。

用户偏好：

- 主要使用中文。
- 说明要“傻瓜模式”，越具体越好。
- 不要只讲原则，要给可以复制粘贴的命令。
- 面向对象可能是完全从 0 开始的新用户。

## 已验证的远端环境

- 超算账号：`m9s003861`
- 观察到的登录节点：`ln1`
- 远端 home：`/publicfs10/fs10-m9/home/m9s003861`
- 稳定 EPOCH 路径：`~/pic/bin/epoch3d`
- 远端运行根目录：`~/pic/lgbo/runs`
- 调度系统：Slurm
- 不要显式写 `#SBATCH -p amd_m9_76`。Slurm 会自动路由到该分区，但手动指定曾经失败。
- 可用 MPI 启动器：`/publicfs10/fs10-share/soft/share-soft/openmpi/4.1.1/bin/mpirun`
- 使用 `--mca btl ^openib` 避免 OpenFabrics 警告。
- Python SDF 读取已验证：`from sdf_helper import sdfr`

## EPOCH 正确启动形状

```bash
mkdir -p Data
cp input.deck Data/input.deck
printf "Data\ninput.deck\n" | mpirun --mca btl ^openib -np 1 ~/pic/bin/epoch3d
```

原因：

```text
EPOCH 先读输出目录，再读 deck 文件名。
输出目录是 Data 时，deck 必须在 Data/input.deck。
```

## 本地脚本

- `scripts/dry_run.py`：生成本地测试运行目录和假指标。
- `scripts/create_run_bundle.py`：打包运行目录和 `remote_tools/`，用于上传超算。
- `scripts/render_docs.py`：生成 `docs/index.html` 网页说明书。

## 远端工具

- `remote_tools/lgbo_env.sh`
- `remote_tools/submit_run.sh`
- `remote_tools/monitor_run.py`
- `remote_tools/analyze_run.py`

## 新任务的最短流程

1. 本地运行 `scripts/create_run_bundle.py` 生成任务包。
2. 上传 `bundles/<run_id>.tar.gz` 到 `~/pic/lgbo/runs`。
3. 远端解压并进入 `<run_id>` 目录。
4. 运行 `bash tools/submit_run.sh .`。
5. 运行 `python3 tools/monitor_run.py .` 监控。
6. 任务完成后运行 `python3 tools/analyze_run.py .`。
7. 只回传 `metrics.json`、`summary.json`、CSV、PNG。

## 后续重点

下一步不是再搭环境，而是补物理内容：

- 替换真正的 LG 生产 deck。
- 扩展 `analyze_run.py`，从生产 SDF 中计算质子/光子指标。
- 接入贝叶斯优化，让每一轮自动生成下一个参数点。
