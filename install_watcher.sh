#!/bin/bash

echo "📦 安装错题监控…"

# 清理旧的冲突服务
launchctl unload ~/Library/LaunchAgents/com.xueba.error-watcher.plist 2>/dev/null
rm -f ~/Library/LaunchAgents/com.xueba.error-watcher.plist
rm -f ~/Library/LaunchAgents/watch_photos.sh ~/Library/LaunchAgents/xueba-watcher.sh
crontab -l 2>/dev/null | grep -v watch_photos | crontab - 2>/dev/null
rm -f /tmp/.xueba-watcher.lock

# 杀死旧进程
ps aux | grep watch_photos | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null

# 启动监控
nohup bash "/Users/book/Desktop/我的笔记/学霸笔记生成器/watch_photos.sh" > /tmp/xueba-watcher.log 2>&1 &
PID=$!

echo "✅ 已启动 (PID: $PID)"
echo ""
echo "📁 微信照片存到: ~/Desktop/错题拍照/"
echo "📋 查看日志: tail -f /tmp/xueba-watcher.log"
echo ""
echo "💡 设置为开机自启："
echo "   系统设置 → 通用 → 登录项 → 添加 startup.command"
echo ""
echo "❌ 停止: kill $PID"
