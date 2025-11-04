#!/bin/bash
# 推送代码到 GitHub 的脚本

echo "🚀 推送代码到 GitHub"
echo ""

# 检查是否已有 remote
if git remote -v | grep -q "origin"; then
    echo "⚠️  检测到已有 remote，先删除..."
    git remote remove origin
fi

# 获取 GitHub 用户名
echo "请输入你的 GitHub 用户名："
read GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ 用户名不能为空"
    exit 1
fi

echo ""
echo "📦 正在连接 GitHub 仓库..."
git remote add origin "https://github.com/${GITHUB_USERNAME}/ai-sales-coach.git"

echo ""
echo "📤 正在推送代码..."
git branch -M main
git push -u origin main

echo ""
echo "✅ 完成！"
echo ""
echo "如果提示输入密码，请使用 GitHub Personal Access Token"
echo "获取方式：GitHub → Settings → Developer settings → Personal access tokens"

