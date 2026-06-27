# 自动化链路注意事项

这份文档记录第一次真正跑通“本地 agent 自动提交超算任务”的新发现。

验证日期：2026-06-27。

已验证闭环：

```text
本地生成任务包
-> scp 上传到北京超算
-> ssh 远端解压
-> sbatch 提交 EPOCH 3D
-> monitor 查询 Slurm
-> 远端读取 SDF
-> 远端生成密度图
-> scp 拉回小结果
```

## 已跑通的最小任务

配置文件：

```text
configs/smoke_laser_target_3d.json
```

deck 模板：

```text
templates/smoke_laser_target_3d.deck.tpl
```

运行命令：

```bash
python3 scripts/remote_run.py all --config configs/smoke_laser_target_3d.json --wait --interval 15
```

结果：

```text
run_id: a57e418566
job_id: 1169138
state: COMPLETED 0:0
elapsed: 00:00:01
node: wqd10nbe11c03
sdf_count: 2
density key: Derived_Number_Density_electron
density shape: 16 x 12 x 12
local plot: runs/a57e418566/remote_results/plots/density_initial.svg
```

这个任务只是链路验证，不是生产物理结果。

## 已跑通的 LG 输入验证任务

配置文件：

```text
configs/lg_3d_input_check.json
```

LG 模板：

```text
templates/epoch_lg_3d.deck.tpl
```

运行命令：

```bash
python3 scripts/remote_run.py all --config configs/lg_3d_input_check.json --wait --interval 15
```

结果：

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

说明：

```text
这证明当前 LG deck 模板可以被远端 EPOCH 3D 接受并生成 SDF。
但它只是小网格语法验证，不代表生产物理参数已经收敛。
```

## SSH 直连

北京超算 SSH 直连页面给出的用户名形如：

```text
m9s003861@BSCC-M9
```

因为用户名本身包含 `@`，手动 ssh 时要这样写：

```bash
ssh -p 22 'm9s003861@BSCC-M9'@ssh.cn-hongkong-1.paracloud.com hostname
```

本项目 `.env` 写法：

```text
HPCPIC_SSH_HOST=ssh.cn-hongkong-1.paracloud.com
HPCPIC_SSH_PORT=22
HPCPIC_SSH_USER=m9s003861@BSCC-M9
HPCPIC_REMOTE_ROOT=~/pic/hpc/runs
```

注意：

```text
.env 不提交 Git。
.env.example 只放模板。
不要提交密码或私钥。
```

## 远端路径

一开始 `scp` 到：

```text
~/pic/hpc/runs/
```

失败过，因为 `scp` 目标路径里的 `~` 不一定按预期展开。

修复方式：

```text
scripts/remote_run.py 会先 ssh 读取远端 $HOME
再把 ~/pic/hpc/runs 转成绝对路径：
/publicfs10/fs10-m9/home/m9s003861/pic/hpc/runs
```

以后写自动化脚本时，远端路径尽量用绝对路径。

## 远端 Python 版本

北京超算登录环境里：

```text
python3 = Python 3.6.8
```

所以远端工具必须兼容 Python 3.6。

不要在 `remote_tools/*.py` 里使用：

```python
from __future__ import annotations
list[str]
tuple[int, str]
subprocess.run(..., text=True, capture_output=True)
```

兼容写法：

```python
subprocess.run(
    cmd,
    universal_newlines=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
```

本地脚本可以用新 Python；远端脚本要保守。

## 可选文件拉取

有些任务没有：

```text
*.csv
plots/*.png
```

直接 `scp remote/*.csv` 会打印：

```text
No such file or directory
```

这不是任务失败，只是文件不存在。

现在 `scripts/remote_run.py fetch` 已经先远端 `ls` 检查可选文件，存在才拉取。

必拉文件：

```text
status.json
metrics.json
summary.json
job_id.txt
```

可选文件：

```text
*.csv
plots/*.png
plots/*.svg
```

## 远端密度图

为了避免远端安装 matplotlib，本项目的 `remote_tools/analyze_run.py` 直接生成纯 SVG 热图。

当前逻辑：

```text
1. 用 sdf_helper.sdfr 读取最新 SDF
2. 自动寻找 Number_Density / density 相关变量
3. 优先选择 electron 密度
4. 对 3D 数据取 z 方向中间切片
5. 生成 plots/density_initial.svg
```

第一次跑通的变量名：

```text
Derived_Number_Density_electron
```

## EPOCH/SDF 注意事项

EPOCH 仍然按这个方式启动：

```bash
mkdir -p Data
cp input.deck Data/input.deck
printf "Data\ninput.deck\n" | mpirun --mca btl ^openib -np <ntasks> ~/pic/bin/epoch3d
```

原因：

```text
EPOCH 先问输出目录，再问 deck 文件名。
当输出目录是 Data，deck 必须在 Data/input.deck。
```

不要改成：

```bash
epoch3d < input.deck
```

## 结论

目前已经不是“理论可行”，而是实际跑通过：

```text
SSH 直连可用
自动提交可用
自动监控可用
远端 SDF 分析可用
密度图拉回可用
```

后续生产任务只需要替换 deck 和分析指标，不需要重新搭自动化链路。
