# PIC 超算 Agent 工作流

这是一个通用的“本地 agent + 远端超算”控制流程，用来管理 3D/2D PIC 数值模拟任务。

核心思想：

```text
超算只是计算工具。
本地电脑或 agent 负责生成任务、提交任务、监控任务、分析结果、决定下一步。
```

当前已经接入并验证的是 EPOCH 3D，但这个仓库的设计不只服务 EPOCH，也不只服务贝叶斯优化。以后可以扩展到：

- EPOCH 2D/3D 批量参数扫描。
- LG 光束、普通高斯光、双色光、偏振组合等不同激光方案。
- 质子、电子、光子、辐射、场结构等不同诊断目标。
- 贝叶斯优化、网格扫描、主动学习、遗传算法或人工指定参数组。
- 远端自动画图、自动提取指标、自动生成小报告。

目前仓库里自带的 `configs/lg_proton_mvp.json` 是一个示例：

```text
LG 光束自由度 + 靶参数 -> 3D EPOCH -> 远端分析 -> 本地/agent 迭代
```

如果你是第一次接触这个项目，先看：

[docs/ZERO_START_zh.md](docs/ZERO_START_zh.md)

不要从源码开始猜。

## 已经验证过什么

在北京超算 BLSC M9 上已经验证：

- Slurm 可以提交任务。
- OpenMPI 4.1.1 + AOCC/flang 5.0.0 可以运行 MPI 程序。
- EPOCH 4.20.1 的 `epoch3d` 已经编译成功。
- EPOCH 3D 冒烟测试可以生成 SDF 文件。
- Python 可以用 `from sdf_helper import sdfr` 读取 SDF。
- 可以从远端 `Data/0000.sdf` 生成 `summary.json`。

更细的超算环境记录见：

[docs/remote_probe.md](docs/remote_probe.md)

自动提交、远端分析和拉回结果的注意事项见：

[docs/AUTOMATION_NOTES_zh.md](docs/AUTOMATION_NOTES_zh.md)

## 给新 agent 怎么用

以后迁移给其他 agent 时，最简单就是把这个仓库链接发给它，并要求它先读：

```text
README.md
AGENT_HANDOFF.md
docs/ZERO_START_zh.md
docs/remote_probe.md
```

它就能知道：

- 项目目的是什么。
- 北京超算上已经验证了哪些坑。
- EPOCH 应该怎么启动。
- 大 SDF 为什么不传回本地。
- 新任务包应该怎么生成、上传、提交、监控、分析。

## 本地快速开始

如果是一台全新的电脑，先安装 Git 和 Python。完整步骤见：

[docs/ZERO_START_zh.md](docs/ZERO_START_zh.md)

本地生成一次测试运行目录：

```bash
python3 scripts/dry_run.py --config configs/lg_proton_mvp.json
```

本地生成一个可以上传到超算的任务包：

```bash
python3 scripts/create_run_bundle.py --config configs/lg_proton_mvp.json
```

生成文件类似：

```text
bundles/<run_id>.tar.gz
```

把这个 `.tar.gz` 上传到超算，然后放到：

```text
~/pic/hpc/runs/
```

## 超算傻瓜模式

在超算终端执行：

```bash
mkdir -p ~/pic/hpc/runs
cd ~/pic/hpc/runs
tar -xzf <run_id>.tar.gz
cd <run_id>
source tools/hpcpic_env.sh
bash tools/submit_run.sh .
```

查看任务状态：

```bash
python3 tools/monitor_run.py .
cat status.json
```

任务完成后分析：

```bash
python3 tools/analyze_run.py .
cat metrics.json
cat summary.json | head -80
```

## 本地自动模式

如果已经配置好 SSH 直连，就不需要再手动复制命令。

先准备本地 `.env`：

```bash
cp .env.example .env
```

把里面的 SSH 信息填成北京超算页面给你的值，例如：

```text
HPCPIC_SSH_HOST=ssh.cn-hongkong-1.paracloud.com
HPCPIC_SSH_PORT=22
HPCPIC_SSH_USER=你的超算账号@BSCC-M9
HPCPIC_REMOTE_ROOT=~/pic/hpc/runs
```

测试连接：

```bash
python3 scripts/remote_run.py probe
```

生成任务包、上传、解压、提交：

```bash
python3 scripts/remote_run.py all --config configs/lg_proton_mvp.json
```

如果想提交后一直等到结束，并自动分析、拉回小结果：

```bash
python3 scripts/remote_run.py all --config configs/lg_proton_mvp.json --wait --interval 60
```

最小 3D 激光打靶验证任务：

```bash
python3 scripts/remote_run.py all --config configs/smoke_laser_target_3d.json --wait --interval 15
```

这个任务只用于验证链路：

```text
本地生成 -> 上传超算 -> sbatch -> EPOCH 3D -> SDF -> 远端密度图 -> 拉回小结果
```

成功后本地会出现：

```text
runs/<run_id>/remote_results/metrics.json
runs/<run_id>/remote_results/summary.json
runs/<run_id>/remote_results/plots/density_initial.svg
```

如果已经有 `run_id`，也可以分步执行：

```bash
python3 scripts/remote_run.py monitor --run-id <run_id>
python3 scripts/remote_run.py analyze --run-id <run_id>
python3 scripts/remote_run.py fetch --run-id <run_id>
```

只把这些小文件传回本地：

```text
status.json
metrics.json
summary.json
plots/*.png
plots/*.svg
*.csv
```

不要默认传回完整 3D SDF：

```text
Data/*.sdf
```

## 远端目录约定

```text
~/pic/
  bin/
    epoch3d
  software/
    epoch_release-4.20.1/
  hpc/
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

## 重要的 EPOCH 启动方式

在这个超算环境里，EPOCH 运行时会先问输出目录，再问输入 deck 文件名。

所以正确启动形状是：

```bash
mkdir -p Data
cp input.deck Data/input.deck
printf "Data\ninput.deck\n" | mpirun --mca btl ^openib -np <ntasks> ~/pic/bin/epoch3d
```

原因：

```text
输出目录输入 Data
deck 文件名输入 input.deck
EPOCH 实际会找 Data/input.deck
```

不要直接写：

```bash
epoch3d < input.deck
```

这样 EPOCH 会把 deck 第一行当成输出目录，导致找错文件。

## 生成网页版说明书

生成自包含 HTML：

```bash
python3 scripts/render_docs.py
```

打开：

```text
docs/index.html
```

把说明书放到 GitHub Pages 的方法见：

[docs/GITHUB_PAGES_zh.md](docs/GITHUB_PAGES_zh.md)

## 当前状态

这还是一个 MVP 工作流骨架。

已经完成：

- 本地生成任务包。
- 上传后远端提交。
- 远端监控 Slurm 状态。
- 远端读取 SDF 并生成小结果 JSON。
- 中文零基础说明书。
- GitHub Pages 网页说明书。

下一步应该做：

- 把示例 deck 换成真正的生产 deck。
- 在 `remote_tools/analyze_run.py` 里加入真实物理指标。
- 根据任务类型接入贝叶斯优化、参数扫描或其他 agent 决策逻辑。
