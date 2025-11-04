#!/bin/bash

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ 设置完成！"
echo "运行服务器: source venv/bin/activate && uvicorn server.main:app --reload"

