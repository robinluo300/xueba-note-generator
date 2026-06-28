"""
本地运行入口 — 测试 AI 笔记生成
用法：python3 run.py "小蝌蚪找妈妈" [--url https://...] [--key sk-xxx]

省略 --key 时会从环境变量 DASHSCOPE_API_KEY 读取
"""

import argparse
import os
import re
import sys
from datetime import date

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from crawler import HanchachaCrawler
from ai_generator import generate_note


def main():
    parser = argparse.ArgumentParser(description="学霸笔记生成器 - 本地运行")
    parser.add_argument("topic", help="课文名称")
    parser.add_argument("--url", default=None, help="汉查查 URL（可选）")
    parser.add_argument("--key", default=None, help="通义千问 API Key")
    parser.add_argument("--output", "-o", default=None, help="输出目录")
    args = parser.parse_args()

    api_key = args.key or os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 请通过 --key 或环境变量 DASHSCOPE_API_KEY 提供 API Key")
        sys.exit(1)

    hc = HanchachaCrawler(timeout=30)
    if args.url:
        data = hc.crawl(args.url)
    else:
        data = hc.search_by_name(args.topic)

    if not data:
        print("❌ 未找到课文")
        sys.exit(1)

    print(f"✅ 已获取: {data['title']} ({data.get('grade', '')})")
    print(f"📝 正在调用 AI 生成笔记…")

    note = generate_note(data, api_key)
    if not note or note.startswith("HTTP") or note.startswith("请求失败") or note.startswith("解析响应"):
        print(f"❌ AI 生成失败: {note}")
        sys.exit(1)

    save_dir = args.output or os.path.join(_HERE, "..", "电子笔记", "学霸笔记")
    save_dir = os.path.normpath(save_dir)
    os.makedirs(save_dir, exist_ok=True)

    safe_name = re.sub(r'[\\/:*?"<>|]', "_", args.topic).strip()
    filepath = os.path.join(save_dir, f"{safe_name}.md")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(note)

    print(f"💾 已保存: {filepath}")
    print(f"📋 共 {len(note)} 字符")


if __name__ == "__main__":
    main()
