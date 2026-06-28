#!/bin/bash

# 开机自启 — 后台启动错题监控（无终端窗口）
nohup bash "/Users/book/Desktop/我的笔记/学霸笔记生成器/watch_photos.sh" > /tmp/xueba-watcher.log 2>&1 &
