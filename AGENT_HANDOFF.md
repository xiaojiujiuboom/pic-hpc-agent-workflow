# Agent 交接说明

你正在接手这个项目：

```text
/Users/boom/Documents/3dpic
```

项目定位：

```text
这是一个通用 PIC 超算 Agent 工作流。
超算只是计算后端，本地/agent 负责组织任务、监控、分析和迭代。
```

当前示例是 LG 光束 + 靶参数 + EPOCH 3D，但项目不要被理解成只服务贝叶斯优化。它也可以服务普通参数扫描、批量作业、远端画图、自动报告、不同激光构型和不同粒子/辐射诊断。

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
- 远端运行根目录：`~/pic/hpc/runs`
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
- `scripts/remote_run.py`：本地自动上传、提交、监控、远端分析、拉回小结果。
- `scripts/render_docs.py`：生成 `docs/index.html` 网页说明书。

自动化链路新注意事项集中写在：

```text
docs/AUTOMATION_NOTES_zh.md
```

SDF 存储和 M9 节点资源估算集中写在：

```text
docs/STORAGE_AND_RESOURCES_zh.md
```

## 远端工具

- `remote_tools/hpcpic_env.sh`：新通用环境入口。
- `remote_tools/lgbo_env.sh`：旧名字兼容入口，会转到 `hpcpic_env.sh`。
- `remote_tools/submit_run.sh`
- `remote_tools/monitor_run.py`
- `remote_tools/analyze_run.py`

## 新任务的最短流程

如果 SSH 直连已配置好，优先用：

```bash
python3 scripts/remote_run.py all --config configs/lg_proton_mvp.json
```

如果要等待任务结束后自动分析和拉回小结果：

```bash
python3 scripts/remote_run.py all --config configs/lg_proton_mvp.json --wait --interval 60
```

已跑通的最小 3D 激光打靶验证：

```bash
python3 scripts/remote_run.py all --config configs/smoke_laser_target_3d.json --wait --interval 15
```

LG 输入 deck 语法验证用：

```bash
python3 scripts/remote_run.py all --config configs/lg_3d_input_check.json --wait --interval 15
```

LG 输入 deck 已验证记录：

```text
run_id: 85e14f4c04
job_id: 1169346
state: COMPLETED 0:0
node: wqd10nbe11c03
sdf_count: 2
density key: Derived_Number_Density_electron
density shape: 16 x 12 x 12
local plot: runs/85e14f4c04/remote_results/plots/density_initial.svg
```

记录：

```text
run_id: a57e418566
job_id: 1169138
state: COMPLETED 0:0
elapsed: 00:00:01
density key: Derived_Number_Density_electron
density shape: 16 x 12 x 12
local plot: runs/a57e418566/remote_results/plots/density_initial.svg
```

这次验证踩出的关键坑：

```text
1. scp 不要直接依赖远端 ~ 展开，脚本需要先解析 $HOME。
2. 远端 python3 是 3.6.8，remote_tools 不要用 Python 3.9+ 类型写法。
3. *.csv / plots/*.png 可能不存在，fetch 要当作可选文件处理。
4. 远端不依赖 matplotlib，密度图用纯 SVG 生成。
```

手动分步流程：

1. 本地运行 `scripts/create_run_bundle.py` 生成任务包。
2. 上传 `bundles/<run_id>.tar.gz` 到 `~/pic/hpc/runs`。
3. 远端解压并进入 `<run_id>` 目录。
4. 运行 `source tools/hpcpic_env.sh`。
5. 运行 `bash tools/submit_run.sh .`。
6. 运行 `python3 tools/monitor_run.py .` 监控。
7. 任务完成后运行 `python3 tools/analyze_run.py .`。
8. 只回传 `metrics.json`、`summary.json`、CSV、PNG。

## 后续重点

下一步不是再搭环境，而是补具体任务：

- 替换真正的生产 deck。
- 扩展 `analyze_run.py`，从生产 SDF 中计算目标物理指标。
- 根据具体研究任务接入贝叶斯优化、参数扫描或其他 agent 决策逻辑。
