# Remote Tools

Copy this directory to the cluster, for example:

```bash
mkdir -p ~/pic/lgbo/tools
cp remote_tools/* ~/pic/lgbo/tools/
```

Typical remote use:

```bash
source ~/pic/lgbo/tools/lgbo_env.sh
bash ~/pic/lgbo/tools/submit_run.sh ~/pic/lgbo/runs/000001
python3 ~/pic/lgbo/tools/monitor_run.py ~/pic/lgbo/runs/000001
python3 ~/pic/lgbo/tools/analyze_run.py ~/pic/lgbo/runs/000001
```

Large SDF files stay on the cluster. Fetch only `status.json`, `metrics.json`, `summary.json`, CSV, and PNG files.

