"""GitHub Actions workflow runner - handles crawl + generate + save"""
import sys, json, os

from crawler import HanchachaCrawler
from ai_generator import generate_note

def main():
    topic = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
    api_key = sys.argv[3] if len(sys.argv) > 3 else None

    hc = HanchachaCrawler(timeout=30)
    if url:
        data = hc.crawl(url)
    else:
        data = hc.search_by_name(topic)

    if not data:
        print("FAILED: 未找到课文")
        sys.exit(1)

    print(f'OK: {data["title"]} ({data.get("grade", "")})')

    note = generate_note(data, api_key)
    if not note:
        print("FAILED: AI 生成失败")
        sys.exit(1)

    print(f"OK: 生成 {len(note)} 字符")

    safe_name = topic.replace("/", "_").replace("\\", "_").replace(":", "_")
    out_dir = "笔记"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{safe_name}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(note)
    print(f"OK: 笔记已保存到 {out_path}")

if __name__ == "__main__":
    main()
