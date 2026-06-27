#!/usr/bin/env python3
from pathlib import Path
import html


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
REMOTE = ROOT / "docs" / "remote_probe.md"
USER_GUIDE = ROOT / "docs" / "USER_GUIDE_zh.md"
ZERO_START = ROOT / "docs" / "ZERO_START_zh.md"
PAGES = ROOT / "docs" / "GITHUB_PAGES_zh.md"
OUT = ROOT / "docs" / "index.html"


def section(title: str, text: str) -> str:
    escaped = html.escape(text)
    return f"<section><h2>{html.escape(title)}</h2><pre>{escaped}</pre></section>"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    readme = README.read_text()
    remote = REMOTE.read_text()
    user_guide = USER_GUIDE.read_text()
    zero_start = ZERO_START.read_text()
    pages = PAGES.read_text()
    body = "\n".join([
        section("项目说明", readme),
        section("从 0 开始", zero_start),
        section("傻瓜模式用户指南", user_guide),
        section("北京超算环境记录", remote),
        section("GitHub Pages 部署", pages),
    ])
    OUT.write_text(f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LGBO 3D PIC 超算工作流</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; line-height: 1.55; color: #172033; background: #f6f8fb; }}
    header {{ padding: 40px 24px 28px; background: #102a43; color: white; }}
    header h1 {{ margin: 0 0 10px; font-size: 34px; }}
    header p {{ margin: 0; max-width: 900px; color: #d9e2ec; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 24px; }}
    section {{ background: white; border: 1px solid #d9e2ec; border-radius: 8px; padding: 20px; margin: 18px 0; }}
    h2 {{ margin-top: 0; }}
    pre {{ white-space: pre-wrap; word-break: break-word; background: #0b1220; color: #e6edf3; padding: 16px; border-radius: 6px; overflow: auto; }}
  </style>
</head>
<body>
  <header>
    <h1>LGBO 3D PIC 超算工作流</h1>
    <p>远端超算运行 EPOCH 3D，本地/agent 监控、分析和贝叶斯优化。大 SDF 留在超算，只回传 metrics、CSV 和图片。</p>
  </header>
  <main>
    {body}
  </main>
</body>
</html>
""")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
