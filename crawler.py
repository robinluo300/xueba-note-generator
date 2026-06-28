"""
汉查查爬虫 — 从 hanchacha.com 提取语文课文数据
"""

import re
from typing import Optional

import cloudscraper
from bs4 import BeautifulSoup

GRADE_MAP = {
    "yishang": "一年级上", "yixia": "一年级下",
    "ershang": "二年级上", "erxia": "二年级下",
    "sanshang": "三年级上", "sanxia": "三年级下",
    "sishang": "四年级上", "sixia": "四年级下",
    "wushang": "五年级上", "wuxia": "五年级下",
    "liushang": "六年级上", "liuxia": "六年级下",
}


class HanchachaCrawler:
    def __init__(self, timeout=15):
        self.timeout = timeout
        self.scraper = cloudscraper.create_scraper()

    def _fetch(self, url: str) -> Optional[str]:
        try:
            resp = self.scraper.get(url, timeout=self.timeout)
            resp.encoding = "utf-8"
            return resp.text if resp.status_code == 200 else None
        except Exception:
            return None

    def _extract_lesson_text(self, soup: BeautifulSoup) -> str:
        h2 = soup.find("h2", class_="h2")
        if h2 and "课文原文" in h2.get_text():
            nrtxt = h2.find_next_sibling("div", class_="nrtxt")
            if nrtxt:
                parts = []
                for p in nrtxt.find_all("p"):
                    t = p.get_text(strip=True)
                    if t:
                        if p.find("strong") and len(t) < 20:
                            continue
                        parts.append(t)
                return "\n\n".join(parts) if parts else ""
        return ""

    def _extract_knowledge_points(self, soup: BeautifulSoup) -> dict:
        content_div = soup.find("div", class_="n-xiazai")
        if not content_div:
            content_div = soup.find("div", class_="bg")

        sections = {}
        current_section = None
        current_lines = []

        for child in content_div.children if content_div else []:
            if child.name != "p":
                continue
            strong = child.find("strong")
            if strong:
                if current_section and current_lines:
                    sections[current_section] = current_lines
                current_section = strong.get_text(strip=True)
                current_lines = []
            elif current_section:
                text = child.get_text(strip=True)
                if text and "相关资料" not in text:
                    current_lines.append(text)

        if current_section and current_lines:
            sections[current_section] = current_lines

        return sections

    def _parse_zhishidian(self, url: str) -> Optional[dict]:
        html = self._fetch(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        sections = self._extract_knowledge_points(soup)

        result = {
            "shengzi": [],
            "summary": "",
            "words": [],
            "jinyi": [],
            "fanyi": [],
            "sentences": [],
            "questions": [],
            "duoyinzi": [],
        }

        for section_name, lines in sections.items():
            if section_name in ("我会写", "我会认"):
                for line in lines:
                    m = re.match(r"(\w+)\s+(\w+)\s+\((.+?)\)", line)
                    if m:
                        result["shengzi"].append({
                            "char": m.group(1),
                            "pinyin": m.group(2),
                            "examples": m.group(3),
                        })

            elif section_name == "多音字":
                for line in lines:
                    m = re.match(r"(\w+)\s+(.*)", line)
                    if m:
                        entry = {"char": m.group(1)}
                        readings = re.findall(r"(\w+)\((.+?)\)", m.group(2))
                        for pinyin, word in readings:
                            entry[pinyin] = word
                        result["duoyinzi"].append(entry)

            elif section_name == "理解词语":
                for line in lines:
                    if "：" in line:
                        word, defn = line.split("：", 1)
                        result["words"].append({
                            "word": word.strip(),
                            "definition": defn.strip(),
                        })

            elif section_name == "近义词":
                for line in lines:
                    pairs = re.findall(r"([\u4e00-\u9fff]+)——([\u4e00-\u9fff]+)", line)
                    for orig, syn in pairs:
                        result["jinyi"].append({"word": orig, "synonym": syn})

            elif section_name == "反义词":
                for line in lines:
                    pairs = re.findall(r"([\u4e00-\u9fff]+)——([\u4e00-\u9fff]+)", line)
                    for orig, ant in pairs:
                        result["fanyi"].append({"word": orig, "antonym": ant})

            elif section_name == "句子解析":
                for line in lines:
                    result["sentences"].append(line)

            elif section_name == "问题归纳":
                for line in lines:
                    result["questions"].append(line)

            elif section_name == "课文主题":
                if lines:
                    result["summary"] = " ".join(lines)

        return result

    def crawl(self, url: str) -> Optional[dict]:
        if "hanchacha.com" not in url:
            return None

        html = self._fetch(url.split("?")[0])
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else ""
        title = title.replace("《", "").replace("》", "").replace("课文", "").strip()

        lesson_text = self._extract_lesson_text(soup)

        grade = ""
        for a in soup.find_all("a"):
            t = a.get_text(strip=True)
            if "年级" in t and "语文" in t:
                grade = t
                break
        if not grade:
            for code, name in GRADE_MAP.items():
                if code in url:
                    grade = name
                    break

        characters = []
        for m in re.finditer(r"([\u4e00-\u9fff]{2,5}(?:妈妈|爸爸|阿姨|叔叔|爷爷|奶奶|哥哥|姐姐|弟弟|妹妹))", lesson_text):
            n = m.group(1)
            if n not in characters:
                characters.append(n)

        data = {
            "title": title,
            "text": lesson_text,
            "grade": grade,
            "source": f"hanchacha.com",
            "url": url,
            "characters": characters,
            "shengzi": [],
            "summary": "",
            "words": [],
            "jinyi": [],
            "fanyi": [],
            "sentences": [],
            "questions": [],
            "duoyinzi": [],
        }

        for a in soup.find_all("a"):
            text = a.get_text(strip=True)
            href = a.get("href", "")
            if "课文知识点" in text and href:
                if href.startswith("/"):
                    href = "https://hanchacha.com" + href
                kp = self._parse_zhishidian(href)
                if kp:
                    data.update(kp)
                break

        return data

    def search_by_name(self, topic: str) -> Optional[dict]:
        for code in ["yishang", "yixia", "ershang", "erxia",
                      "sanshang", "sanxia", "sishang", "sixia",
                      "wushang", "wuxia", "liushang", "liuxia"]:
            num = list(GRADE_MAP.keys()).index(code) + 1
            toc_url = f"https://hanchacha.com/yuwen/keben-{num:02d}/"
            html = self._fetch(toc_url)
            if not html:
                continue
            s = BeautifulSoup(html, "html.parser")
            for a in s.find_all("a"):
                t = a.get_text(strip=True)
                href = a.get("href", "")
                if topic in t and href.endswith(".html"):
                    if href.startswith("/"):
                        href = "https://hanchacha.com" + href
                    return self.crawl(href)
        return None
