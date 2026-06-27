# 傻瓜模式用户指南

如果你是完全从 0 开始，先看：

```text
docs/ZERO_START_zh.md
```

这个项目的目的：

- 超算上跑 3D EPOCH。
- 本地或 agent 负责生成参数、监控任务、看结果、做贝叶斯优化。
- 大的 `.sdf` 文件不传回本地。
- 超算上先分析，生成小的 `metrics.json`、`summary.json`、CSV、PNG。

## 一句话流程

```text
本地生成任务包 -> 上传超算 -> sbatch -> 等完成 -> 远端分析 SDF -> 本地拉小结果
```

## 本地生成任务包

```bash
python3 scripts/create_run_bundle.py --config configs/lg_proton_mvp.json
```

看到类似：

```text
bundle=/Users/boom/Documents/3dpic/bundles/5ce3c0c603.tar.gz
```

把这个 tar.gz 上传到超算。

## 超算上运行

```bash
mkdir -p ~/pic/lgbo/runs
cd ~/pic/lgbo/runs
tar -xzf 5ce3c0c603.tar.gz
cd 5ce3c0c603
source tools/lgbo_env.sh
bash tools/submit_run.sh .
```

## 查任务

```bash
python3 tools/monitor_run.py .
cat status.json
```

## 分析结果

```bash
python3 tools/analyze_run.py .
cat metrics.json
cat summary.json | head -80
```

## 回传哪些文件

只回传这些：

```text
status.json
metrics.json
summary.json
*.csv
*.png
```

不要默认回传：

```text
Data/*.sdf
```

除非是最终论文图需要的少数精选帧。
