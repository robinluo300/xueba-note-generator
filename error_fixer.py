"""
数学错题本 — 通义千问分析错因，生成结构化 Obsidian 错题笔记
"""

import json
import os
import re
import sys
from datetime import date

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import urllib.request
import urllib.error

QWEN_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"


def _build_prompt(question: str, wrong_answer: str, correct_answer: str, grade: str) -> str:
    return f"""你是一位小学数学教师，请根据以下错题信息，生成一份结构清晰的错题分析笔记。

## 错题信息

年级：{grade}
题目：{question}
错误答案：{wrong_answer}
正确答案：{correct_answer}

---
## 要求

用 Obsidian Callout 语法（>[!xxx]）生成笔记。每个板块用一个 Callout 包裹。

笔记结构如下（严格按此顺序）：

> [!danger] 题型识别
> 判断这是什么类型的题（如：口算题、竖式计算、应用题、单位换算、几何图形等）

> [!failure] 我的错误
> 写清楚：题目是什么、学生的答案是什么、正确答案是什么

> [!warning] 错因分析
> 分析错误原因（如：粗心算错、概念不清、审题漏条件等）

> [!success] 正确解法
> 分步骤讲解正确答案的解题过程

> [!tip] 记忆方法
> 给一个简单好记的方法或口诀

> [!quote] 易错提醒
> 这类题容易在哪里出错

> [!example] 巩固练习
> 出 2 道同类题目

---
总要求：
- 语言简洁清楚
- 不用 emoji，不用装饰
- 语气平和，指出错误但不批评
- 内容准确，步骤清晰
- 标题用 # 一级标题
"""


def generate_error_note(question: str, wrong_answer: str, correct_answer: str, api_key: str, grade: str = "二年级") -> str:
    prompt = _build_prompt(question, wrong_answer, correct_answer, grade)

    body = json.dumps({
        "model": "qwen-plus",
        "input": {
            "messages": [
                {"role": "system", "content": "你是一位小学数学教师，擅长分析错题，讲解清晰，语气平和。"},
                {"role": "user", "content": prompt},
            ]
        },
        "parameters": {
            "result_format": "message",
            "temperature": 0.8,
            "max_tokens": 4096,
            "top_p": 0.9,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        QWEN_ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return f"HTTP 错误 {e.code}: {e.read().decode('utf-8', errors='replace')}"
    except Exception as e:
        return f"请求失败: {e}"

    try:
        output = result["output"]["choices"][0]["message"]["content"]
        return output
    except (KeyError, IndexError):
        return f"解析响应失败: {json.dumps(result, ensure_ascii=False, indent=2)}"


def _build_ocr_prompt(ocr_text: str, grade: str) -> str:
    return f"""你是一位小学数学教师。下面是一张学生数学错题照片识别出来的文字，请你：

1. 判断题目是什么
2. 判断学生做错的地方在哪里
3. 分析错误原因
4. 给出正确的解法

然后生成一份完整的错题分析笔记。

## 照片识别文字

年级：{grade}
识别结果：
{ocr_text}

---
## 要求

用 Obsidian Callout 语法（>[!xxx]）生成笔记。每个板块用一个 Callout 包裹。

笔记结构如下（严格按此顺序）：

> [!danger] 题型识别
> 判断这是什么类型的题（如：口算题、竖式计算、应用题、单位换算、几何图形等）

> [!failure] 我的错误
> 写清楚：题目的原题是什么、学生写成了什么、正确答案是什么

> [!warning] 错因分析
> 分析错误原因（如：粗心算错、概念不清、审题漏条件等）

> [!success] 正确解法
> 分步骤讲解正确答案的解题过程

> [!tip] 记忆方法
> 给一个简单好记的方法或口诀

> [!quote] 易错提醒
> 这类题容易在哪里出错

> [!example] 巩固练习
> 出 2 道同类题目

---
总要求：
- 语言简洁清楚
- 不用 emoji，不用装饰
- 语气平和，指出错误但不批评
- 内容准确，步骤清晰
- 标题用 # 一级标题
"""


def generate_error_note_from_ocr(ocr_text: str, api_key: str, grade: str = "二年级") -> str:
    prompt = _build_ocr_prompt(ocr_text, grade)

    body = json.dumps({
        "model": "qwen-plus",
        "input": {
            "messages": [
                {"role": "system", "content": "你是一位小学数学教师，擅长分析错题，讲解清晰，语气平和。"},
                {"role": "user", "content": prompt},
            ]
        },
        "parameters": {
            "result_format": "message",
            "temperature": 0.8,
            "max_tokens": 4096,
            "top_p": 0.9,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        QWEN_ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return f"HTTP 错误 {e.code}: {e.read().decode('utf-8', errors='replace')}"
    except Exception as e:
        return f"请求失败: {e}"

    try:
        output = result["output"]["choices"][0]["message"]["content"]
        return output
    except (KeyError, IndexError):
        return f"解析响应失败: {json.dumps(result, ensure_ascii=False, indent=2)}"


def _get_title_from_ocr(ocr_text: str) -> str:
    lines = [l.strip() for l in ocr_text.split("\n") if l.strip()]
    for line in lines:
        clean = line.strip("•·●◦ ")
        if clean and len(clean) > 2:
            return clean[:30]
    return lines[0][:30] if lines else "错题"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="数学错题本")
    parser.add_argument("input", nargs="?", help="题目内容（手动模式）")
    parser.add_argument("--wrong", help="错误答案（手动模式）")
    parser.add_argument("--correct", help="正确答案（手动模式）")
    parser.add_argument("--ocr-text", help="OCR 识别文字（拍照模式，AI 自动分析）")
    parser.add_argument("--key", default=None, help="通义千问 API Key")
    parser.add_argument("--grade", default="二年级", help="年级")
    parser.add_argument("--output", default=None, help="输出目录")
    args = parser.parse_args()

    api_key = args.key or os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 请通过 --key 或环境变量 DASHSCOPE_API_KEY 提供 API Key")
        sys.exit(1)

    save_dir = args.output or os.path.expanduser("~/Desktop/我的笔记/错题")
    save_dir = os.path.normpath(save_dir)
    os.makedirs(save_dir, exist_ok=True)

    # ---- 拍照模式 ----
    if args.ocr_text:
        print("📸 正在分析错题照片…")
        note = generate_error_note_from_ocr(args.ocr_text, api_key, args.grade)
        title = _get_title_from_ocr(args.ocr_text)
    # ---- 手动模式 ----
    elif args.input:
        if not args.wrong or not args.correct:
            print("❌ 手动模式需要 --wrong 和 --correct")
            sys.exit(1)
        print("📝 正在分析错题…")
        note = generate_error_note(args.input, args.wrong, args.correct, api_key, args.grade)
        title = args.input[:30]
    else:
        parser.print_help()
        sys.exit(1)

    if not note or note.startswith("HTTP") or note.startswith("请求失败") or note.startswith("解析响应"):
        print(f"❌ 生成失败: {note}")
        sys.exit(1)

    title_slug = re.sub(r'[\\/:*?"<>|]', "_", title).strip()
    date_str = date.today().isoformat()
    filepath = os.path.join(save_dir, f"{date_str} {title_slug}.md")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(note)

    print(f"💾 已保存: {filepath}")
    print(f"📋 共 {len(note)} 字符")


if __name__ == "__main__":
    main()
