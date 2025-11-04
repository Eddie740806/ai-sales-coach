# 🚀 快速分享指南 - 让朋友远程访问

## 最简单的方法：使用 ngrok

### 步骤 1：安装 ngrok

**方法A：直接下载（推荐）**
1. 访问：https://ngrok.com/download
2. 选择 **macOS** 版本下载
3. 解压文件
4. 将 `ngrok` 文件移动到 `/usr/local/bin/`：
   ```bash
   sudo mv ngrok /usr/local/bin/
   ```
5. 或者添加到 PATH（在 `~/.zshrc` 中添加路径）

**方法B：使用 Homebrew（如果已安装）**
```bash
brew install ngrok
```

### 步骤 2：启动 ngrok

打开新的终端窗口，运行：
```bash
ngrok http 8000
```

你会看到类似这样的输出：
```
Session Status                online
Account                       (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
```

### 步骤 3：分享 URL

**复制 `Forwarding` 后面的 URL**（例如：`https://abc123.ngrok.io`）

**直接分享这个 URL 给朋友**，他们就可以访问你的平台了！

---

## 方法 2：使用 localtunnel（如果已安装 Node.js）

### 步骤 1：安装
```bash
npm install -g localtunnel
```

### 步骤 2：启动
```bash
lt --port 8000
```

### 步骤 3：分享 URL
会显示类似：`https://xxx.loca.lt`，分享给朋友即可。

---

## ⚠️ 重要提醒

1. **服务器必须保持运行**
   - 保持你的服务器在运行（`uvicorn server.main:app --reload --host 0.0.0.0 --port 8000`）

2. **ngrok 会话**
   - 免费版 ngrok URL 每次启动都会变化
   - 如果想固定 URL，需要注册 ngrok 账号（免费）

3. **安全注意**
   - 这是临时演示，不要用于生产环境
   - 分享 URL 时注意安全

---

## 🎯 完整流程

1. ✅ 确保服务器在运行
2. ✅ 安装并启动 ngrok
3. ✅ 复制 ngrok 提供的 URL
4. ✅ 分享 URL 给朋友
5. ✅ 朋友打开浏览器访问即可！

---

## 📝 测试

启动 ngrok 后，你可以：
- 访问 ngrok 的 Web Interface（通常是 `http://127.0.0.1:4040`）查看请求
- 测试分享的 URL 是否正常

---

## 💡 提示

- **免费 ngrok 限制**：URL 每次启动会变化，会话时间有限
- **注册 ngrok**：可以免费注册账号，获得固定域名和更长会话时间
- **其他选项**：如果不想用 ngrok，可以考虑部署到云服务（如 Railway、Render）

