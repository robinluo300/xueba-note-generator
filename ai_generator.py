"""
通义千问 AI 生成器 — 调用 DashScope API 生成语文笔记
"""

import json
from typing import Optional
import urllib.request
import urllib.error


QWEN_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"


def _build_prompt(data: dict) -> str:
    text = data.get("text", "")
    summary = data.get("summary", "")
    characters = data.get("characters", [])
    shengzi = data.get("shengzi", [])
    words = data.get("words", [])
    jinyi = data.get("jinyi", [])
    fanyi = data.get("fanyi", [])
    sentences = data.get("sentences", [])
    questions = data.get("questions", [])
    duoyinzi = data.get("duoyinzi", [])
    grade = data.get("grade", "未知")
    title = data.get("title", "")

    sz_text = "\n".join(f"- {s['char']}（{s['pinyin']}）{s['examples']}" for s in shengzi[:25])
    dy_text = ""
    for dy in duoyinzi:
        readings = [f"{k}（{v}）" for k, v in dy.items() if k != "char"]
        dy_text += f"- {dy['char']}：" + "、".join(readings) + "\n"
    wd_text = "\n".join(f"- {w['word']}：{w['definition']}" for w in words)
    jy_text = "、".join(f"{j['word']}→{j['synonym']}" for j in jinyi)
    fy_text = "、".join(f"{f['word']}→{f['antonym']}" for f in fanyi)
    st_text = "\n".join(f"- {s}" for s in sentences[:6])
    qs_text = "\n".join(f"- {q}" for q in questions[:4])
    ch_text = "、".join(characters[:6])

    return f"""你是一位小学语文教师，请根据以下课文资料生成一份结构清晰、内容完整的语文笔记。

## 课文资料

课文名：{title}
年级：{grade}
课文原文：
{text}

课文主题：
{summary}

主要人物：{ch_text}

生字表：
{sz_text}

多音字：
{dy_text}

词语解释：
{wd_text}

近义词：{jy_text}

反义词：{fy_text}

句子解析：
{st_text}

问题归纳：
{qs_text}

---
## 要求

请用 Obsidian Callout 语法（>[!xxx]）生成笔记。每个板块用一个 Callout 包裹。

笔记结构如下（严格按此顺序）：

> [!summary] 课文小档案
> 用表格列出：课题、年级、体裁、主要人物、一句话故事梗概

> [!important] 生字
> - 会认字：列出会认字，每个带拼音
> - 会写字：列出会写字，每个带拼音和组词
> - 多音字：列出多音字的不同读音，举例句区分

> [!info] 词语
> - 重点词语解释
> - 近义词 / 反义词
> - 课文精彩词语

> [!warning] 句子赏析
> 选 2-3 个精彩句子，分析修辞手法和表达效果

> [!example] 段落结构
> 用表格列出：段落、内容概括、作用

> [!success] 课文主题
> 用简洁语言概括课文告诉我们什么道理

> [!question] 思考题
> 出 2-3 个思考题

---
总要求：
- 语言简洁清楚，适合小学生阅读
- 不用 emoji，不用花哨装饰
- 内容准确，不写复杂长句
- 排版整齐，重点突出
"""


def generate_note(data: dict, api_key: str) -> Optional[str]:
    prompt = _build_prompt(data)

    body = json.dumps({
        "model": "qwen-plus",
        "input": {
            "messages": [
                {"role": "system", "content": "你是一位小学语文教师，擅长撰写结构清晰、语言简洁的语文笔记。"},
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
    except (KeyError, IndexError) as e:
        return f"解析响应失败: {json.dumps(result, ensure_ascii=False, indent=2)}"
