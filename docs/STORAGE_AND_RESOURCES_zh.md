# SDF 存储与超算资源估算

这份文档记录当前 BLSC M9 资源信息，以及 3D EPOCH SDF 文件大小的粗估方法。

查询日期：2026-06-27。

## 相关配置文件

正式 LG 起点配置：

```text
configs/lg_proton_mvp.json
templates/epoch_lg_3d.deck.tpl
```

小号 LG deck 语法验证配置：

```text
configs/lg_3d_input_check.json
```

该配置已实际跑通：

```text
run_id: 85e14f4c04
job_id: 1169346
state: COMPLETED 0:0
sdf_count: 2
density key: Derived_Number_Density_electron
density shape: 16 x 12 x 12
local plot: runs/85e14f4c04/remote_results/plots/density_initial.svg
```

最小自动化链路验证配置：

```text
configs/smoke_laser_target_3d.json
```

## 当前账号存储配额

`publicfs10` 当前配额：

```text
Soft Limit : 450.0 GB
Hard Limit : 500.0 GB
Usage      : 82.5 GB
Used Rate  : 16.5%
```

也就是说，当前还能用大约：

```text
500 - 82.5 = 417.5 GB
```

注意：这是磁盘空间，不是运行内存。

## M9 节点资源

当前默认可用分区：

```text
partition: amd_m9_768
nodes: 457
cpus per node: 256
memory per node: 768000 MB
state: up
```

Slurm 显示：

```text
DefMemPerCPU = 2700 MB
MaxMemPerCPU = 2764 MB
```

所以满节点 256 CPU 对应可申请内存大约：

```text
256 * 2700 MB = 691200 MB = 675 GB
256 * 2764 MB = 707584 MB = 691 GB
```

账号关联限制里看到：

```text
GrpTRES: cpu=2560
```

粗略理解：

```text
最多同时占用约 2560 CPU
约等于 10 个满节点
```

这不是说单个作业一定能用 10 节点，只是当前账号组 CPU 配额量级。

## SDF 文件大小怎么估算

3D 网格数据最基本公式：

```text
一个 3D 标量变量大小 ≈ nx * ny * nz * 8 bytes
```

如果输出多个场和密度：

```text
一个 SDF 网格部分 ≈ 单变量大小 * 输出变量数
```

常见变量数：

```text
电场 Ex/Ey/Ez: 3
磁场 Bx/By/Bz: 3
电子/碳/质子数密度: 3
其他网格、坐标、元数据: 约 1-3 个变量等效
```

所以如果只输出场和三个物种数密度，保守估计：

```text
每个 SDF ≈ 10 到 14 个 3D 标量变量
```

如果再输出更多诊断、温度、电流、能量密度等，会继续变大。

## 当前 LG MVP 网格估算

当前配置：

```text
nx = 384
ny = 192
nz = 192
cells = 14,155,776
```

单个 3D 标量变量：

```text
14,155,776 * 8 bytes = 108 MiB
```

如果每个 SDF 输出 10 个网格变量：

```text
约 1.05 GiB / SDF
```

如果每个 SDF 输出 14 个网格变量：

```text
约 1.48 GiB / SDF
```

如果每个 SDF 输出 18 个网格变量：

```text
约 1.90 GiB / SDF
```

当前 `lg_proton_mvp.json`：

```text
t_end = 650 fs
dt_snapshot = 25 fs
dump_first = T
dump_last = T
```

快照数量大约：

```text
650 / 25 + 1 = 27 个 SDF
```

所以当前 reduced 输出大致：

```text
1.05 GiB * 27 = 28 GiB
1.48 GiB * 27 = 40 GiB
1.90 GiB * 27 = 51 GiB
```

也就是说，当前 MVP 如果不输出粒子，单个 run 预计几十 GB 量级。

## 更大网格的风险

| 网格 | 单变量大小 | 10变量/SDF | 18变量/SDF | 27个SDF 约 |
|---|---:|---:|---:|---:|
| 384x192x192 | 108 MiB | 1.05 GiB | 1.90 GiB | 28-51 GiB |
| 512x256x256 | 256 MiB | 2.50 GiB | 4.50 GiB | 68-122 GiB |
| 768x384x384 | 864 MiB | 8.44 GiB | 15.19 GiB | 228-410 GiB |
| 1024x512x512 | 2.00 GiB | 20.0 GiB | 36.0 GiB | 540-972 GiB |

结论：

```text
500GB 配额只适合小规模验证或少量 reduced runs。
如果开始做 3D 参数扫描或 BO，建议扩容到至少 2TB。
如果要保存粒子相空间、多轮 BO、多组 LG 参数，建议 5TB 起步更舒服。
```

## 粒子输出是最大风险

当前 LG 模板默认：

```text
particles = never
px = never
py = never
pz = never
particle_weight = never
```

这是故意的。

原因：

```text
粒子输出大小 ≈ 粒子数 * 每粒子输出字段数 * 8 bytes
```

如果输出：

```text
位置 + px/py/pz + weight + id ...
```

每个粒子可能几十 bytes 到上百 bytes。

3D PIC 里粒子数很容易到千万级甚至亿级，所以粒子 dump 会迅速超过网格场数据。

推荐策略：

```text
1. 日常 BO/扫描：不输出全粒子。
2. 只输出网格密度、场、少量派生诊断。
3. 确认最优区域后，再挑少数 run 打开粒子输出。
4. 粒子输出不要每个 snapshot 都开，最好只在末态或少数关键时刻开。
```

## 推荐的输出策略

探索阶段：

```text
dt_snapshot = 50-100 fs
fields = always
density = always + species
particles = never
```

精细验证阶段：

```text
dt_snapshot = 25 fs
fields = always
density = always + species
particles = selected snapshots only
```

论文出图阶段：

```text
只保留精选 run
只回传必要 SDF 或远端直接画图
清理中间大文件
```

## 资源使用建议

当前节点：

```text
1 node = 256 CPU, 约 675-691 GB 可申请内存
账号 CPU 配额 ≈ 2560 CPU
```

建议起步：

```text
小 smoke: 1 核
中等 3D 测试: 1 节点内 32-128 rank
生产 3D: 1-4 节点起步测试
大网格生产: 视内存和排队情况扩到 4-10 节点
```

注意：

```text
不要一开始就跑大网格 + 高频 SDF + 全粒子输出。
先用小网格确认 deck、诊断、自动化链路。
再逐步放大网格和输出。
```
