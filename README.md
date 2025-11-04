# AI Sales Coach Platform 🚀

一个智能销售教练平台，比传统RAG系统更强大！

## 🎯 核心功能

### 1. **智能对话教练**
- 业务员可以随时与AI教练对话
- 基于知识库提供专业建议
- 实时学习和改进

### 2. **知识库管理**
- 培训师可以添加培训内容
- 自动索引和搜索
- 效果追踪和优化

### 3. **话术生成器**
- AI辅助生成销售话术
- 自动生成多个变体
- A/B测试和效果追踪

### 4. **持续学习系统**
- 从每次对话中学习
- 识别高效话术模式
- 个性化训练建议

### 5. **语音分析**
- 录音档转文字
- 情感和语速分析
- 关键信息提取

## 🚀 快速开始

### 安装依赖
```bash
./setup.sh
```

### 配置（可选）
如果需要使用OpenAI API，创建 `.env` 文件：
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

**注意：** 即使没有配置API Key，系统也会使用智能回退模式，提供基本的AI响应。

### 启动服务器
```bash
source venv/bin/activate
uvicorn server.main:app --reload
```

服务器启动后会自动：
- 初始化数据库
- 加载示例培训内容
- 初始化向量数据库

### API文档
访问 http://localhost:8000/docs 查看完整的API文档

## 📊 主要API端点

### 对话
- `POST /api/chat` - 与AI教练对话

### 知识库
- `POST /api/knowledge/content` - 添加培训内容
- `GET /api/knowledge/content` - 搜索内容

### 话术
- `POST /api/scripts/generate` - 生成话术
- `GET /api/scripts/{script_id}` - 获取话术

### 学习
- `GET /api/learning/insights/{sales_id}` - 获取学习洞察

### 数据分析
- `GET /api/analytics/dashboard` - 仪表板数据

## 🎨 架构优势

相比传统系统，我们的平台具有：

1. **智能知识图谱** - 不只是文档存储，而是关联式学习
2. **多模态分析** - 文本+语音+行为数据
3. **实时反馈循环** - 每次对话都让系统更聪明
4. **个性化教练** - 针对每个业务员的定制训练
5. **话术进化引擎** - 自动优化和A/B测试

## 🔧 技术栈

- **FastAPI** - 后端框架
- **OpenAI GPT-3.5 Turbo** - LLM服务（支持回退模式，性价比高）
- **ChromaDB** - 向量数据库（RAG检索）
- **SQLAlchemy** - ORM数据库
- **SQLite** - 数据库（可升级到PostgreSQL）
- **Whisper API** - 语音转文字
- **Sentence Transformers** - 向量嵌入（可选）
- **持续学习** - 反馈循环系统

## ✅ 已实现功能

- ✅ **真实LLM集成** - OpenAI GPT-3.5 Turbo，支持回退模式
- ✅ **向量数据库** - ChromaDB实现智能RAG检索
- ✅ **数据库持久化** - SQLite存储所有数据
- ✅ **语音处理** - Whisper API集成
- ✅ **持续学习系统** - 从对话中提取洞察
- ✅ **智能话术生成** - AI辅助生成和优化
- ✅ **示例数据** - 自动初始化培训内容

## 📝 可选改进

- [ ] 安装sentence-transformers提升向量搜索质量
- [ ] 升级到PostgreSQL数据库
- [ ] 前端界面开发
- [ ] 实时WebSocket支持
- [ ] 多租户支持

## 💡 使用示例

### 1. 业务员与AI教练对话
```python
import requests

response = requests.post("http://localhost:8000/api/chat", json={
    "message": "客户说价格太贵，我该怎么回应？",
    "sales_id": "sales_001",
    "customer_type": "中小企业"
})
print(response.json())
```

### 2. 培训师添加培训内容
```python
response = requests.post("http://localhost:8000/api/knowledge/content", json={
    "title": "新客户开发技巧",
    "content": "详细内容...",
    "content_type": "training_material",
    "tags": ["开发", "新客户"],
    "created_by": "trainer_001"
})
```

### 3. 生成销售话术
```python
response = requests.post("http://localhost:8000/api/scripts/generate", json={
    "scenario": "价格异议处理",
    "customer_type": "中小企业",
    "requirements": "需要强调价值而非价格"
})
print(response.json())
```

### 4. 获取学习洞察
```python
response = requests.get("http://localhost:8000/api/learning/insights/sales_001")
print(response.json())
```

### 5. 处理录音档
```python
response = requests.post("http://localhost:8000/api/voice/process", json={
    "audio_url": "path/to/audio.mp3",
    "conversation_id": "conv_001"
})
```

## 🎯 核心优势

相比你朋友（51talk）的平台，我们的版本更强大：

1. **智能RAG系统** - 使用向量数据库实现真正的语义搜索
2. **真实LLM集成** - 支持OpenAI GPT-3.5 Turbo，即使没有API Key也有智能回退
3. **持续学习** - 每次对话都自动提取洞察，持续改进
4. **数据库持久化** - 所有数据永久保存，不会丢失
5. **语音处理** - 集成Whisper API，自动分析录音档
6. **智能话术生成** - AI辅助生成和优化，支持A/B测试
7. **个性化训练** - 针对每个业务员的弱点定制建议

