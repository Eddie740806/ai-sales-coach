"""
向量数据库 - 使用ChromaDB实现RAG检索
"""
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from .config import settings
from .logger import logger

class VectorDB:
    def __init__(self):
        self.client = None
        self.collection = None
        self.embedder = None
        
        try:
            # 初始化ChromaDB
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_directory
            )
            
            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name="sales_knowledge",
                metadata={"description": "销售知识和培训内容"}
            )
            
            # 初始化嵌入模型（可选）
            try:
                from sentence_transformers import SentenceTransformer
                self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("向量嵌入模型已加载")
            except ImportError:
                logger.warning("未安装sentence-transformers，将使用ChromaDB的默认嵌入")
                self.embedder = None
            except Exception as e:
                logger.warning(f"无法加载embedding模型：{e}，将使用ChromaDB的默认嵌入")
                self.embedder = None
                
        except Exception as e:
            logger.error(f"向量数据库初始化错误：{e}，将使用内存存储", exc_info=True)
    
    def add_content(self, content_id: str, text: str, metadata: Dict):
        """添加内容到向量数据库"""
        if not self.collection:
            return
        
        try:
            # 如果embedder可用，使用它；否则使用文本本身
            if self.embedder:
                embeddings = self.embedder.encode([text]).tolist()
            else:
                embeddings = None
            
            self.collection.add(
                ids=[content_id],
                documents=[text],
                embeddings=embeddings,
                metadatas=[metadata]
            )
        except Exception as e:
            logger.error(f"添加内容错误：{e}", exc_info=True)
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """搜索相关内容"""
        if not self.collection:
            return []
        
        try:
            # 如果embedder可用，使用它；否则使用文本查询
            if self.embedder:
                query_embedding = self.embedder.encode([query]).tolist()
                results = self.collection.query(
                    query_embeddings=query_embedding,
                    n_results=n_results
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
            
            # 格式化结果
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    metadata = results['metadatas'][0][i] if results['metadatas'] and len(results['metadatas'][0]) > i else {}
                    formatted_results.append({
                        'id': metadata.get('id', ''),  # 确保包含id
                        'content': results['documents'][0][i],
                        'metadata': metadata,
                        'distance': results['distances'][0][i] if results.get('distances') and len(results['distances'][0]) > i else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"搜索错误：{e}", exc_info=True)
            return []
    
    def delete_content(self, content_id: str):
        """删除内容"""
        if not self.collection:
            return
        
        try:
            self.collection.delete(ids=[content_id])
        except Exception as e:
            logger.error(f"删除内容错误：{e}", exc_info=True)

# 全局向量数据库实例
vector_db = VectorDB()

