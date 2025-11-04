"""
初始化示例数据
"""
from .models import TrainingContent, ContentType
from .knowledge_base import knowledge_base
from .logger import logger
from datetime import datetime

def init_sample_data():
    """初始化示例培训内容"""
    
    sample_contents = [
        TrainingContent(
            title="客户需求挖掘技巧",
            content="""客户需求挖掘是销售成功的关键。以下是几个重要技巧：

1. **开放式提问**
   - "您目前遇到的主要挑战是什么？"
   - "您期望达到什么样的效果？"

2. **倾听技巧**
   - 保持眼神接触
   - 不要打断客户
   - 记录关键信息

3. **深入挖掘**
   - 问"为什么"了解根本原因
   - 问"如果...会怎样"探索可能性

4. **确认理解**
   - "让我确认一下，您的意思是..."
   - "所以您最关心的是..." """,
            content_type=ContentType.TRAINING_MATERIAL,
            tags=["需求挖掘", "提问技巧", "沟通"],
            created_by="system",
            created_at=datetime.now()
        ),
        TrainingContent(
            title="价格异议处理话术",
            content="""当客户说"价格太贵"时，可以这样回应：

1. **理解并共情**
   "我完全理解您的关注点。价格确实是重要的考虑因素。"

2. **价值转移**
   "让我们从另一个角度看看。这个解决方案可以帮您节省多少时间和成本？"

3. **分阶段说明**
   "我们可以分阶段实施，这样您可以先看到效果再决定是否继续。"

4. **社会证明**
   "我们之前服务的[客户类型]也遇到过类似情况，他们最终发现投资回报率超过300%。"

5. **灵活方案**
   "我们可以根据您的预算调整方案，找到最适合的版本。" """,
            content_type=ContentType.SALES_SCRIPT,
            tags=["价格异议", "话术", "异议处理"],
            created_by="system",
            created_at=datetime.now()
        ),
        TrainingContent(
            title="建立信任关系的最佳实践",
            content="""信任是销售的基础。建立信任的方法：

1. **专业展示**
   - 深入了解产品和服务
   - 分享专业见解
   - 提供有价值的建议

2. **诚实透明**
   - 不夸大产品功能
   - 承认产品的局限性
   - 提供真实案例

3. **持续跟进**
   - 及时回复客户问题
   - 主动提供帮助
   - 记住客户偏好

4. **个人连接**
   - 了解客户的个人背景
   - 记住重要日期
   - 分享适当的故事""",
            content_type=ContentType.BEST_PRACTICE,
            tags=["信任", "关系建立", "最佳实践"],
            created_by="system",
            created_at=datetime.now()
        ),
        TrainingContent(
            title="成交促成技巧",
            content="""促成成交的时机和技巧：

1. **识别成交信号**
   - 客户开始询问细节
   - 客户讨论实施时间
   - 客户询问付款方式

2. **试探性成交**
   - "您觉得这个方案怎么样？"
   - "如果我们能满足您的需求，您是否愿意开始？"

3. **假设性成交**
   - "我们下周一开始实施，可以吗？"
   - "您希望我们什么时候开始？"

4. **选择性成交**
   - "您希望选择A方案还是B方案？"
   - "您更倾向于月度付款还是年度付款？"

5. **紧迫感创造**
   - "本月我们有特别优惠"
   - "名额有限，建议尽快决定" """,
            content_type=ContentType.TRAINING_MATERIAL,
            tags=["成交", "销售技巧", "促成"],
            created_by="system",
            created_at=datetime.now()
        ),
        TrainingContent(
            title="中小企业客户沟通策略",
            content="""中小企业客户的特点和沟通策略：

**客户特点：**
- 决策者通常是老板本人
- 预算有限，价格敏感
- 重视实用性而非品牌
- 需要快速见效

**沟通策略：**
1. 强调ROI和成本节约
2. 提供灵活的付款方案
3. 展示快速实施的案例
4. 强调实用性和易用性
5. 提供免费试用或演示

**话术要点：**
- "帮您节省成本"而非"提升效率"
- "快速见效"而非"长期价值"
- "简单易用"而非"功能强大" """,
            content_type=ContentType.BEST_PRACTICE,
            tags=["中小企业", "客户类型", "沟通策略"],
            created_by="system",
            created_at=datetime.now()
        )
    ]
    
    logger.info("正在初始化示例数据...")
    for content in sample_contents:
        try:
            content_id = knowledge_base.add_content(content)
            logger.info(f"已添加：{content.title} (ID: {content_id})")
        except Exception as e:
            logger.error(f"添加失败：{content.title} - {e}", exc_info=True)
    
    logger.info("示例数据初始化完成！")

if __name__ == "__main__":
    init_sample_data()

