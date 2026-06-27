# LGBO 3D PIC 超算工作流

这是一个给 3D EPOCH PIC 任务用的“本地 agent + 远端超算”控制流程。

项目目标：

- 在北京超级云计算中心运行耗时的 3D EPOCH 模拟。
- 大的 `.sdf` 文件留在超算，不默认传回本地。
- 在超算上做轻量分析，生成小结果文件。
- 本地或 agent 只读取 `metrics.json`、`summary.json`、CSV 和 PNG，用于贝叶斯优化、画图和记录。

当前第一阶段目标是：

```text
LG 光束自由度 + 靶参数 -> 3D EPOCH -> 远端分析 -> 本地贝叶斯优化
```

面向的物理问题包括质子/光子诊断与优化。

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
~/pic/lgbo/runs/
```

## 超算傻瓜模式

在超算终端执行：

```bash
mkdir -p ~/pic/lgbo/runs
cd ~/pic/lgbo/runs
tar -xzf <run_id>.tar.gz
cd <run_id>
source tools/lgbo_env.sh
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

只把这些小文件传回本地：

```text
status.json
metrics.json
summary.json
plots/*.png
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

- 把 `templates/epoch_lg_3d.deck.tpl` 换成真正的 LG 生产 deck。
- 在 `remote_tools/analyze_run.py` 里加入真实质子/光子物理指标。
- 把 `metrics.json` 接到贝叶斯优化循环。
