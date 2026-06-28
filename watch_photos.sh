#!/bin/bash

# 学霸错题 — 照片监控自动处理
# 只允许一个实例
LOCK_FILE="/tmp/.xueba-watcher.lock"
[ -f "$LOCK_FILE" ] && ps -p "$(cat "$LOCK_FILE")" >/dev/null 2>&1 && exit 0
echo $$ > "$LOCK_FILE"

WATCH_DIR="$HOME/Desktop/错题拍照"
PROJECT_DIR="/Users/book/Desktop/我的笔记/学霸笔记生成器"
KEY_FILE="$HOME/.xueba-api-key"
GRADE_FILE="$HOME/.xueba-grade"
PROCESSED_FILE="/tmp/.xueba_processed.txt"

mkdir -p "$WATCH_DIR"

api_key=$(cat "$KEY_FILE" 2>/dev/null)
if [ -z "$api_key" ]; then
    echo "❌ 缺少 API Key，请先双击 一键生成学霸笔记.command"
    exit 1
fi
grade=$(cat "$GRADE_FILE" 2>/dev/null || echo "二年级")

cd "$PROJECT_DIR" || exit 1

if [ ! -f ocr_helper ]; then
    swiftc -o ocr_helper ocr_helper.swift 2>/dev/null
fi

touch "$PROCESSED_FILE"

process_image() {
    local img="$1"
    grep -qxF "$img" "$PROCESSED_FILE" 2>/dev/null && return
    echo "[$(date +%H:%M:%S)] 📸 $(basename "$img")"
    ocr_text=$(./ocr_helper "$img" 2>/dev/null)
    if [ -z "$ocr_text" ]; then
        echo "[$(date +%H:%M:%S)] ⚠️  OCR 无结果，跳过"
        echo "$img" >> "$PROCESSED_FILE"
        return
    fi
    echo "[$(date +%H:%M:%S)] 🤖 AI 分析中…"
    output=$(python3 error_fixer.py --ocr-text "$ocr_text" --key "$api_key" --grade "$grade" 2>&1)
    if echo "$output" | grep -q "已保存"; then
        filepath=$(echo "$output" | grep "已保存" | sed 's/.*已保存: //')
        echo "[$(date +%H:%M:%S)] ✅ $filepath"
        open "$filepath"
    else
        echo "[$(date +%H:%M:%S)] ❌ $output"
    fi
    echo "$img" >> "$PROCESSED_FILE"
}

echo "🔍 监控中: $WATCH_DIR (按 Ctrl+C 停止)"

while true; do
    for ext in jpg jpeg png heic webp; do
        for img in "$WATCH_DIR"/*.$ext; do
            [ -f "$img" ] && process_image "$img"
        done
    done
    sleep 3
done
