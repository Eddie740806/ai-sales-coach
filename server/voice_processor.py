"""
语音处理模块
处理录音档，转文字并分析
"""
from typing import Optional, Dict, List
from .models import VoiceAnalysis
import json

class VoiceProcessor:
    def __init__(self):
        # 这里应该集成实际的语音识别服务（如 Whisper, Azure Speech等）
        pass
    
    def process_audio(self, audio_url: str, conversation_id: str) -> VoiceAnalysis:
        """处理音频文件"""
        # 1. 转文字（应该调用实际的语音识别API）
        transcription = self._transcribe(audio_url)
        
        # 2. 情感分析
        sentiment = self._analyze_sentiment(transcription)
        
        # 3. 提取关键信息
        key_phrases = self._extract_key_phrases(transcription)
        
        # 4. 分析说话模式
        speaking_rate = self._analyze_speaking_rate(audio_url)
        
        return VoiceAnalysis(
            conversation_id=conversation_id,
            audio_url=audio_url,
            transcription=transcription,
            sentiment=sentiment,
            key_phrases=key_phrases,
            speaking_rate=speaking_rate
        )
    
    def _transcribe(self, audio_url: str) -> str:
        """转文字 - 使用Whisper API"""
        try:
            from openai import OpenAI
            import os
            from .config import settings
            
            api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "未配置OpenAI API Key，无法转录音频"
            
            client = OpenAI(api_key=api_key)
            
            # 如果是URL，下载文件；如果是本地路径，直接使用
            if audio_url.startswith("http"):
                import requests
                response = requests.get(audio_url)
                audio_file = response.content
            else:
                with open(audio_url, "rb") as f:
                    audio_file = f.read()
            
            # 调用Whisper API
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
            return transcription.text
            
        except ImportError:
            return "未安装openai包，无法转录音频"
        except Exception as e:
            return f"转录错误：{str(e)}"
    
    def _analyze_sentiment(self, text: str) -> str:
        """情感分析 - 使用简单的关键词匹配（可扩展为NLP库）"""
        # 正面词汇
        positive_words = ["好", "满意", "感谢", "很棒", "优秀", "完美", "赞", "喜欢", "支持"]
        # 负面词汇
        negative_words = ["不好", "失望", "差", "糟糕", "不满意", "反对", "拒绝", "讨厌"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count and positive_count > 0:
            return "positive"
        elif negative_count > positive_count and negative_count > 0:
            return "negative"
        else:
            return "neutral"
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """提取关键短语 - 基于关键词匹配"""
        # 定义关键短语模式
        key_patterns = {
            "价格相关": ["价格", "费用", "成本", "报价", "预算"],
            "需求挖掘": ["需求", "需要", "想要", "期望", "目标"],
            "异议处理": ["担心", "顾虑", "问题", "疑问", "怀疑"],
            "成交促成": ["决定", "购买", "签约", "合作", "同意"],
            "产品介绍": ["功能", "特性", "优势", "特点", "产品"],
            "服务支持": ["服务", "支持", "售后", "维护", "保障"]
        }
        
        phrases = []
        text_lower = text.lower()
        for phrase, keywords in key_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                phrases.append(phrase)
        
        return phrases[:5]  # 最多返回5个关键短语
    
    def _analyze_speaking_rate(self, audio_url: str) -> float:
        """分析语速 - 基于转录文本长度估算"""
        # 简化实现：基于转录文本长度和假设的音频时长估算
        # 实际应该使用音频处理库（如librosa）分析真实语速
        try:
            # 尝试读取转录文本长度
            transcription = self._transcribe(audio_url)
            if isinstance(transcription, str) and len(transcription) > 0:
                # 假设平均音频时长为文本长度/100秒（简化估算）
                # 实际应该从音频文件获取真实时长
                estimated_duration = len(transcription) / 100.0  # 简化估算
                if estimated_duration > 0:
                    words_per_minute = (len(transcription) / estimated_duration) * 60
                    return round(words_per_minute, 2)
        except Exception:
            pass
        
        # 默认返回中等语速
        return 150.0  # 每分钟字数

# 全局语音处理器实例
voice_processor = VoiceProcessor()

