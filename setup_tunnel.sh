#!/bin/bash
# 内网穿透设置脚本

echo "🌐 设置内网穿透，让朋友可以通过互联网访问..."
echo ""

# 检查选项
echo "请选择内网穿透方式："
echo "1. ngrok（推荐，最简单）"
echo "2. localtunnel（需要Node.js）"
echo "3. Cloudflare Tunnel（免费，但配置复杂）"
echo ""
read -p "请输入选项 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "📦 安装 ngrok..."
        echo ""
        echo "方法1: 使用 Homebrew（如果已安装）"
        echo "  brew install ngrok"
        echo ""
        echo "方法2: 手动下载"
        echo "  1. 访问 https://ngrok.com/download"
        echo "  2. 下载 macOS 版本"
        echo "  3. 解压到 /usr/local/bin 或添加到 PATH"
        echo ""
        echo "安装完成后，运行："
        echo "  ngrok http 8000"
        echo ""
        echo "然后分享 ngrok 提供的 URL 给朋友"
        ;;
    2)
        if command -v node &> /dev/null; then
            echo ""
            echo "📦 安装 localtunnel..."
            npm install -g localtunnel
            echo ""
            echo "✅ 安装完成！"
            echo ""
            echo "启动隧道："
            echo "  lt --port 8000"
            echo ""
            echo "然后分享 localtunnel 提供的 URL 给朋友"
        else
            echo "❌ 需要先安装 Node.js"
            echo "访问 https://nodejs.org 下载安装"
        fi
        ;;
    3)
        echo ""
        echo "Cloudflare Tunnel 配置较复杂"
        echo "建议使用 ngrok 或 localtunnel"
        ;;
    *)
        echo "无效选项"
        ;;
esac

