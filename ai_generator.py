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

    return f"""你是一位特别受小学生欢迎的语文老师，最擅长把课堂变成好玩的冒险！请根据以下课文资料，写一份让小学生们读得津津有味的超有趣语文笔记。

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

请用 Obsidian Callout 语法（>[!xxx]）生成笔记，整体风格要像一场"语文探险之旅"。每个板块用一个 Callout 包裹。

笔记结构如下（请严格按此顺序）：

> [!summary] 📖 课文小档案
> 用表格列出：课题、年级、体裁、主要人物、一句话故事梗概。
> 最后加评分：⭐ 有趣指数、📚 知识指数、😊 难度指数（各 1-5 颗星）

> [!important] 🔤 生字大闯关
> 分三关：
> - 🟢 第一关·我会认：列出会认字，每个带拼音
> - 🟡 第二关·我会写：列出会写字，每个带拼音+组词
> - 🟠 第三关·多音字小剧场：每个多音字举例句区分读音（比如：他好(hào)奇地看着这本书真好看(hǎo)）

> [!info] 🎯 词语游乐园
> 分成几个"游乐项目"（有的项目就写，没有就跳过）：
> - 🎠 词语碰碰车：重点词语解释
> - 🎪 近义词跷跷板：近义词配对
> - 🎡 反义词摩天轮：反义词配对
> - 🎨 好词收藏夹：课文里的精彩词语

> [!warning] 🔍 句子放大镜
> 选 2-3 个最精彩的句子，像侦探一样分析：
> - 🕵️ 用了什么修辞手法？
> - 💡 好在哪里？
> - 🌟 换你会怎么写？

> [!example] 🗺️ 课文地图
> 用简单表格列出：段落、讲了什么、作用
> 最后加一句"路线总结"

> [!success] 🏆 核心宝藏
> 用最简单的话说清课文告诉我们什么道理。加上：
> 💬 一句话总结（10 个字以内）
> 🎯 这篇课文让我们学到了什么

> [!question] 🤔 脑力加油站
> 出 2-3 个有趣的问题考考自己，比如：
> - "如果你是主人公，你会怎么做？"
> - "课文里最打动你的是哪句话？为什么？"

---

总要求：
- 语气像朋友聊天一样亲切，多用"我们"、"你发现了吗"
- 适当加 emoji，让页面色彩丰富、好玩
- 每个板块标题要有趣（参考上面的格式）
- 内容要简单易懂，不写太复杂的长句
- 排版清晰，小学生能自己看懂
- 篇幅适中，不要太长
"""


def generate_note(data: dict, api_key: str) -> Optional[str]:
    prompt = _build_prompt(data)

    body = json.dumps({
        "model": "qwen-plus",
        "input": {
            "messages": [
                {"role": "system", "content": "你是一位最受孩子喜欢的语文老师，总能想出好玩的方式让课文变得有趣易懂。你的笔记色彩丰富、像游戏一样好读。"},
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
