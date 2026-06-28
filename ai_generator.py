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

    return f"""你是一位经验丰富的小学语文教师，请根据以下课文资料生成一份结构完整、语言优美的语文笔记。

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

请生成一份格式规范的 Obsidian 语文笔记，使用以下 Callout 语法：

> [!abstract] 标题
> 内容

笔记结构如下（请严格按此顺序和格式）：

### 一、课文基础档案

用表格列出：课题、年级、体裁（根据内容判断是叙事故事/写景散文/说明文）、主要人物/描写对象、核心主旨

### 二、词语积累

分以下子板块（有则写，无则省略）：
- 会写字：列出生字，每个带拼音和组词
- 多音字：列出多音字及不同读音
- 词语解释：列出重点词语及释义
- 近义词 / 反义词

### 三、重点句子赏析

选取文中 2-3 个重点句子，分析其修辞手法、表达效果

### 四、段落结构梳理

用表格列出：段落、内容概括、作用/特点

### 五、课文主题与中心思想

概括课文主旨

### 六、课后思考

列出 2-3 个思考题或拓展问题

---

全文使用 Obsidian Callout 语法 >[...] 包裹每个主要板块。
语气亲切、适合小学生阅读。
标题用 # 一级标题，子标题用 ## 二级标题。
"""


def generate_note(data: dict, api_key: str) -> Optional[str]:
    prompt = _build_prompt(data)

    body = json.dumps({
        "model": "qwen-plus",
        "input": {
            "messages": [
                {"role": "system", "content": "你是一位资深小学语文教师，擅长撰写结构清晰、语言优美的语文笔记。"},
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
