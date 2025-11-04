# 🚀 部署指南 - 给朋友访问

## 当前状态

✅ 服务器已在运行  
✅ 监听地址：`0.0.0.0:8000`（可外部访问）  
✅ 前端界面已配置  
✅ 认证系统已启用

## 📱 访问方式

### 方式1：同一局域网访问（推荐）

1. **获取你的IP地址**
   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Windows
   ipconfig
   ```

2. **朋友访问地址**
   ```
   http://你的IP地址:8000
   ```
   例如：`http://192.168.1.100:8000`

3. **确保防火墙允许**
   - macOS：系统偏好设置 → 安全性与隐私 → 防火墙
   - 确保允许 Python 或 Terminal 的网络访问

### 方式2：使用 ngrok（内网穿透）

1. **安装 ngrok**
   ```bash
   # macOS
   brew install ngrok
   
   # 或从 https://ngrok.com/download 下载
   ```

2. **启动隧道**
   ```bash
   ngrok http 8000
   ```

3. **分享 ngrok 提供的 URL**
   ```
   例如：https://abc123.ngrok.io
   ```

### 方式3：部署到云服务器

- **Vercel**（前端）
- **Railway** / **Render**（全栈）
- **AWS / GCP / Azure**（自托管）

## 🔒 安全注意事项

1. **开发环境**：当前设置为开发模式，允许所有来源访问
2. **生产环境**：建议设置 `ENV=production` 并配置具体的 CORS 来源

## 📝 快速测试

1. **本地测试**
   ```
   http://localhost:8000
   ```

2. **API 文档**
   ```
   http://localhost:8000/docs
   ```

3. **健康检查**
   ```
   http://localhost:8000/health
   ```

## 🎯 使用说明

1. **首次访问**：需要注册账号
2. **功能测试**：
   - 对话教练
   - 知识库搜索
   - 话术生成
   - 数据分析

## ⚠️ 注意事项

- 服务器关闭后朋友无法访问
- 需要保持服务器运行
- 建议使用 ngrok 或部署到云服务器以便长期访问

