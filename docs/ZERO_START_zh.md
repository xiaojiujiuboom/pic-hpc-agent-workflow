# 从 0 开始：给完全新手的操作手册

这份手册假设你电脑上什么都没有，也不知道 EPOCH、Slurm、SDF 是什么。
你只需要会复制命令、粘贴命令、看文件有没有生成。

## 这个项目是干什么的

我们要做的是：

```text
本地电脑/agent 负责生成任务包、监控、整理结果、决定下一步
北京超级云计算中心负责真正跑 PIC 程序，比如 EPOCH 3D
大的 3D SDF 数据留在超算
本地只拿回小文件：metrics.json、summary.json、CSV、PNG
```

这样做的原因：

```text
3D PIC 数据太大，不能每次都拖回本地
超算更适合跑 EPOCH/PIC 和读 SDF
本地更适合做参数决策、画图、整理报告
贝叶斯优化只是其中一种用法，不是唯一用法
```

## 你最终要得到什么

本地会生成一个压缩包：

```text
bundles/<run_id>.tar.gz
```

这个压缩包传到超算后，可以直接：

```bash
bash tools/submit_run.sh .
python3 tools/monitor_run.py .
python3 tools/analyze_run.py .
```

## 第 1 步：本地安装基础工具

### macOS

先安装 Homebrew。打开终端，粘贴官网命令：

```text
https://brew.sh/
```

然后安装 Git 和 Python：

```bash
brew install git python
```

检查是否成功：

```bash
git --version
python3 --version
```

能看到版本号就行。

### Windows

安装这三个东西：

```text
1. Git for Windows: https://git-scm.com/download/win
2. Python 3: https://www.python.org/downloads/windows/
3. 北京超算客户端或网页终端: https://cloud.blsc.cn/
```

安装 Python 时，一定勾选：

```text
Add python.exe to PATH
```

然后打开 PowerShell，检查：

```powershell
git --version
python --version
```

如果 Windows 上 `python3` 不存在，就把后面所有 `python3` 换成 `python`。

## 第 2 步：下载这个项目

如果已经放到 GitHub，直接 clone：

```bash
git clone https://github.com/xiaojiujiuboom/pic-hpc-agent-workflow.git
cd pic-hpc-agent-workflow
```

如果还没有 GitHub，也可以让别人把整个文件夹压缩发给你，然后解压，进入这个目录。

检查文件是否齐：

```bash
ls
```

你应该看到：

```text
README.md
configs
templates
scripts
remote_tools
docs
```

## 第 3 步：本地生成一个任务包

运行：

```bash
python3 scripts/create_run_bundle.py --config configs/lg_proton_mvp.json
```

Windows 如果没有 `python3`，运行：

```powershell
python scripts/create_run_bundle.py --config configs/lg_proton_mvp.json
```

成功后会看到类似：

```text
run_id=5ce3c0c603
bundle=/你的路径/bundles/5ce3c0c603.tar.gz
```

记住这个 `.tar.gz` 文件，它就是要上传到超算的任务包。

## 第 4 步：登录北京超算

打开北京超算：

```text
https://cloud.blsc.cn/
```

进入终端后，先确认自己在登录节点：

```bash
whoami
hostname
pwd
```

然后准备目录：

```bash
mkdir -p ~/pic/hpc/runs
cd ~/pic/hpc/runs
```

## 第 5 步：上传任务包

用北京超算客户端里的“极速传输/快传”，把本地这个文件上传到远端：

```text
本地：bundles/<run_id>.tar.gz
远端：~/pic/hpc/runs/
```

上传完成后，在超算终端确认：

```bash
cd ~/pic/hpc/runs
ls -lh
```

你应该看到：

```text
<run_id>.tar.gz
```

## 第 6 步：解压任务包

把 `<run_id>` 换成你真实看到的名字，例如 `5ce3c0c603`：

```bash
cd ~/pic/hpc/runs
tar -xzf <run_id>.tar.gz
cd <run_id>
ls
```

你应该看到：

```text
config.json
input.deck
submit.slurm
tools
```

## 第 7 步：提交任务

运行：

```bash
source tools/hpcpic_env.sh
bash tools/submit_run.sh .
```

成功时会看到类似：

```text
Submitted batch job 1234567
```

并且当前目录会多一个：

```text
job_id.txt
```

## 第 8 步：查看任务状态

运行：

```bash
python3 tools/monitor_run.py .
cat status.json
```

常见状态：

```text
PENDING：排队中
RUNNING：正在跑
COMPLETED：跑完了
FAILED：失败了
```

也可以直接看队列：

```bash
squeue -u "$USER"
```

## 第 9 步：分析结果

任务完成后运行：

```bash
python3 tools/analyze_run.py .
cat metrics.json
cat summary.json | head -80
```

成功后会有：

```text
metrics.json
summary.json
```

这两个就是本地 agent、贝叶斯优化程序、参数扫描程序或画图脚本要读的小结果文件。

## 第 10 步：只下载小结果

下载这些：

```text
status.json
metrics.json
summary.json
*.csv
*.png
```

不要默认下载这些：

```text
Data/*.sdf
```

原因很简单：3D SDF 会非常大，传回来很慢，也会占满本地硬盘。

## 如果报错怎么办

### 找不到 EPOCH

看这个文件是否存在：

```bash
ls -lh ~/pic/bin/epoch3d
```

如果没有，说明这个超算账号还没装 EPOCH，需要先按 `docs/remote_probe.md`
里的记录安装一次。

### 找不到 sdf 或 sdf_helper

测试：

```bash
python3 - <<'EOF'
import sdf
from sdf_helper import sdfr
print("sdf ok")
print("sdfr ok")
EOF
```

如果失败，说明这个超算账号还没装 SDF Python reader。

### 任务失败

先看三个文件：

```bash
cat job_id.txt
cat status.json
cat *.err
cat *.out | tail -120
```

把这几段发给维护这个项目的 agent，就能继续定位。

## 最重要的原则

```text
本地只负责生成任务包和看小结果。
超算负责跑 EPOCH 和读 SDF。
不要把 3D 大数据搬回本地。
```
