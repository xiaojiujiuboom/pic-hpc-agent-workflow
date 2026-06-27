# 把说明书放到 GitHub Pages

用途：让其他人不用翻聊天记录，直接打开网页照着做。

## 本地生成网页

在本地项目目录运行：

```bash
cd /Users/boom/Documents/3dpic
python3 scripts/render_docs.py
```

生成的网页在：

```text
/Users/boom/Documents/3dpic/docs/index.html
```

直接双击这个文件也能看。

## 推到 GitHub

第一次建仓库时：

```bash
cd /Users/boom/Documents/3dpic
git init
git add .
git commit -m "Add LGBO PIC workflow guide"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<你的仓库名>.git
git push -u origin main
```

如果仓库已经存在，只用：

```bash
cd /Users/boom/Documents/3dpic
git add .
git commit -m "Update LGBO PIC workflow guide"
git push
```

本项目当前建议仓库名：

```text
lgbo-3d-pic-control-plane
```

不要把这些目录强行传到 GitHub：

```text
downloads/
vendor/
runs/
bundles/
```

这些是本地下载包、EPOCH 源码、运行结果、临时任务包，不是说明书和工具本体。

## 开 GitHub Pages

在 GitHub 网页里点：

```text
Settings -> Pages -> Build and deployment
```

然后选：

```text
Source: Deploy from a branch
Branch: main
Folder: /docs
Save
```

等一两分钟，GitHub 会给你一个网址。以后只要重新运行
`python3 scripts/render_docs.py`，再 `git add . && git commit && git push`，
网页就会更新。

## 给别人看的最短说明

把这个网址发给对方，并告诉他：

```text
先看 docs/ZERO_START_zh.md，再看 README。
真正上传到超算的是 bundles/<run_id>.tar.gz。
大 SDF 文件不要往本地传，只传 metrics.json、summary.json、图片和 CSV。
```
