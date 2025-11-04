# 🚀 快速安装 ngrok - 让朋友远程访问

## 最简单的方法（推荐）

### 步骤 1：下载 ngrok

1. **打开浏览器访问**：https://ngrok.com/download
2. **选择 macOS** 版本
3. **下载 ZIP 文件**

### 步骤 2：安装

**方法A：拖放到终端（最简单）**
1. 解压下载的 ZIP 文件
2. 打开终端
3. 将 `ngrok` 文件拖到终端窗口
4. 按回车，会显示 ngrok 的版本信息

**方法B：移动到系统目录**
```bash
# 1. 解压文件后，打开终端
# 2. 进入下载的文件夹（通常在 Downloads）
cd ~/Downloads

# 3. 移动到系统目录（需要密码）
sudo mv ngrok /usr/local/bin/

# 4. 验证安装
ngrok version
```

### 步骤 3：启动隧道

**在终端运行：**
```bash
ngrok http 8000
```

**你会看到：**
```
ngrok                                                          

Session Status                online
Account                       (Plan: Free)
Version                       3.x.x
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

### 步骤 4：分享 URL

**复制 `Forwarding` 后面的 URL**（例如：`https://abc123.ngrok.io`）

**直接把这个 URL 发给朋友**，他们就可以访问你的平台了！

---

## 🎯 完整操作流程

1. ✅ **确保服务器在运行**
   ```bash
   # 应该已经在运行了，检查一下
   curl http://localhost:8000/health
   ```

2. ✅ **安装 ngrok**（按上面的步骤）

3. ✅ **启动 ngrok**
   ```bash
   ngrok http 8000
   ```

4. ✅ **复制 URL 给朋友**
   - 例如：`https://abc123.ngrok.io`

5. ✅ **朋友访问**
   - 朋友打开浏览器
   - 输入你给的 URL
   - 就可以看到你的平台了！

---

## 💡 提示

- **免费版限制**：每次启动 ngrok，URL 会变化
- **注册账号**（可选）：可以免费注册 ngrok 账号，获得固定域名
- **保持运行**：ngrok 和服务器都要保持运行，朋友才能访问

---

## ⚠️ 如果遇到问题

1. **端口被占用**：确保 8000 端口没有被其他程序使用
2. **防火墙**：macOS 可能会询问是否允许网络访问，选择"允许"
3. **URL 无法访问**：检查服务器是否在运行

---

## 🎉 完成！

安装完成后，运行 `ngrok http 8000`，然后把 URL 发给朋友就可以了！

