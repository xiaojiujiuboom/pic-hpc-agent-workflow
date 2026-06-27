# 远端工具说明

这个目录里的脚本是在超算上用的。

最常见情况：这些脚本已经被打进任务包里，远端目录长这样：

```text
<run_id>/
  config.json
  input.deck
  submit.slurm
  tools/
    lgbo_env.sh
    submit_run.sh
    monitor_run.py
    analyze_run.py
```

## 提交任务

在超算上进入任务目录：

```bash
cd ~/pic/lgbo/runs/<run_id>
bash tools/submit_run.sh .
```

成功后会生成：

```text
job_id.txt
status.json
```

## 监控任务

```bash
python3 tools/monitor_run.py .
cat status.json
```

常见状态：

```text
PENDING：排队中
RUNNING：正在运行
COMPLETED：已完成
FAILED：失败
```

## 分析 SDF

任务完成后：

```bash
python3 tools/analyze_run.py .
cat metrics.json
cat summary.json | head -80
```

## 数据传输原则

大的 SDF 留在超算：

```text
Data/*.sdf
```

本地只拿小结果：

```text
status.json
metrics.json
summary.json
CSV
PNG
```

## 如果脚本不是随任务包上传的

也可以单独把 `remote_tools/` 复制到超算：

```bash
mkdir -p ~/pic/lgbo/tools
cp remote_tools/* ~/pic/lgbo/tools/
```

然后这样用：

```bash
source ~/pic/lgbo/tools/lgbo_env.sh
bash ~/pic/lgbo/tools/submit_run.sh ~/pic/lgbo/runs/000001
python3 ~/pic/lgbo/tools/monitor_run.py ~/pic/lgbo/runs/000001
python3 ~/pic/lgbo/tools/analyze_run.py ~/pic/lgbo/runs/000001
```
