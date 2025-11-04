"""
LLM服务 - 支持OpenAI和其他LLM提供商
"""
from typing import List, Dict, Optional
import os
from .config import settings
from .logger import logger

class LLMService:
    def __init__(self):
        self.api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = settings.openai_model
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning("未安装openai包，将使用模拟响应")
    
    def generate_response(
        self, 
        system_prompt: str,
        user_message: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """生成回复"""
        if not self.client:
            return self._fallback_response(user_message, context)
        
        try:
            # 構建消息列表
            # 添加繁體中文要求到system prompt
            enhanced_prompt = system_prompt
            if "繁體中文" not in system_prompt and "繁體" not in system_prompt:
                enhanced_prompt = system_prompt + "\n\n**重要：請務必使用繁體中文回答，不要使用簡體中文。所有回應都必須是繁體中文。**"
            
            messages = [{"role": "system", "content": enhanced_prompt}]
            
            # 添加上下文
            if context:
                messages.append({
                    "role": "system",
                    "content": f"相關知識和培訓內容：\n{context}\n\n注意：請使用繁體中文回答。"
                })
            
            # 添加历史对话
            if conversation_history:
                for msg in conversation_history[-5:]:  # 只保留最近5轮对话
                    messages.append(msg)
            
            # 添加当前问题
            messages.append({"role": "user", "content": user_message})
            
            # 调用API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM调用错误：{e}", exc_info=True)
            return self._fallback_response(user_message, context)
    
    def _fallback_response(self, message: str, context: Optional[str] = None) -> str:
        """回退響應（當沒有API key時）"""
        if "客戶" in message or "如何處理" in message or "客户" in message or "如何处理" in message:
            return """基於我們的最佳實踐，我建議您：

1. **深入了解客戶需求**
   - 透過提問了解客戶的真實痛點
   - 傾聽客戶的關注點和期望

2. **提供針對性解決方案**
   - 將產品特性與客戶需求匹配
   - 強調價值而非功能

3. **建立信任關係**
   - 展示專業性和同理心
   - 提供真實案例和成功故事

可以參考我們的話術庫中的「客戶需求挖掘」部分，那裡有詳細的對話模板。"""
        
        elif "話術" in message or "怎麼說" in message or "话术" in message or "怎么说" in message:
            return """針對您的情況，我推薦以下話術：

**開場白：**
「我理解您的關注點，讓我為您詳細說明一下我們的解決方案如何滿足您的具體需求。」

**價值呈現：**
「根據您剛才提到的[具體需求]，我們的[產品特性]可以幫您[具體價值]，這在我們之前服務的[客戶類型]中取得了很好的效果。」

**異議處理：**
「我完全理解您的顧慮。讓我從另一個角度為您分析一下...」

需要我為您生成更具體的話術嗎？"""
        
        elif "價格" in message or "費用" in message or "价格" in message or "费用" in message:
            return """處理價格異議的建議：

1. **價值導向**
   - 強調ROI和長期價值
   - 對比成本和收益

2. **分階段說明**
   - 解釋價格構成
   - 提供靈活方案

3. **社會證明**
   - 展示其他客戶的滿意度和成果
   - 提供案例研究

可以參考我們的話術庫中的「價格異議處理」模板。"""
        
        else:
            return """這是一個很好的問題。讓我基於我們的培訓材料和最佳實踐為您提供建議。

建議您：
1. 參考我們知識庫中的相關內容
2. 結合實際情況靈活運用
3. 記錄這次對話的結果，以便持續改進

如果您有具體場景，我可以為您生成定制化的話術和SOP流程。"""
    
    def generate_script(
        self,
        scenario: str,
        customer_type: Optional[str] = None,
        requirements: Optional[str] = None,
        base_script: Optional[str] = None
    ) -> str:
        """生成销售话术"""
        if not self.client:
            return self._generate_script_fallback(scenario, customer_type)
        
        try:
            prompt = f"""你是一個專業的銷售話術設計師。請生成一個銷售話術。

場景：{scenario}
客戶類型：{customer_type or '通用'}
特殊要求：{requirements or '無'}

話術應該包含：
1. 開場白（建立信任）
2. 需求挖掘（了解痛點）
3. 價值呈現（解決方案）
4. 異議處理（應對疑慮）
5. 促成成交（行動號召）

請生成一個完整、專業、實用的銷售話術。

**重要：請務必使用繁體中文生成，不要使用簡體中文。**"""
            
            if base_script:
                prompt += f"\n\n參考話術：\n{base_script}\n\n請基於此優化（使用繁體中文）："
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"话术生成错误：{e}", exc_info=True)
            return self._generate_script_fallback(scenario, customer_type)
    
    def _generate_script_fallback(self, scenario: str, customer_type: Optional[str] = None) -> str:
        """回退话术生成"""
        return f"""
【{scenario} - {customer_type or '通用'}銷售話術】

**1. 開場白**
「您好，我是[公司名稱]的[姓名]。我了解到您可能在[場景]方面有需求，讓我為您介紹一下我們的解決方案...」

**2. 需求挖掘**
「為了更好地為您服務，我想了解一下：
- 您目前遇到的主要挑戰是什麼？
- 您期望達到什麼樣的效果？
- 您最關心的是哪方面？」

**3. 價值呈現**
「基於您剛才提到的需求，我們的解決方案可以幫您：
- [具體價值點1]
- [具體價值點2]
- [具體價值點3]

在我們服務的[客戶類型]中，通常能夠[具體成果]...」

**4. 異議處理**
「我理解您的[具體疑慮]。讓我從另一個角度為您分析：
- [應對方案1]
- [應對方案2]」

**5. 促成成交**
「基於我們的討論，我建議我們可以：
1. [下一步行動1]
2. [下一步行動2]

您覺得哪個方案更適合您？」
"""

# 全局LLM服务实例
llm_service = LLMService()

