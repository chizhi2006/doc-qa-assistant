import os
import time
from openai import(APITimeoutError, APIConnectionError, RateLimitError,AuthenticationError, BadRequestError, PermissionDeniedError)
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
os.environ["OPENAI_API_KEY"] = "sk-0fc1290a66604007a5c1715d397c0736"  # 
os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com/v1" 
class RAGSystem:
    def __init__(self):
        """类初始化：服务器启动时，加载模型、建库"""
        self.llm=ChatOpenAI(model="deepseek-chat", temperature=0)
        self.total_token_count=0
        loader = TextLoader("note.txt", encoding="utf-8")
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""] # 优先按段落、句号切，最后才硬切
        )
        splits = text_splitter.split_documents(docs)
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
        self.vectorstore = FAISS.from_documents(splits, embeddings)
    def ask(self,question:str):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        related_docs = retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in related_docs])
        prompt = f"请根据以下内容回答问题。\n内容：{context}\n问题：{question}\n如果你在内容中找不到答案，请直接回答不知道。"
        MAXRETRIES=3
        token_cost=0
        answer=""
        for i in range(MAXRETRIES):
            try: 
                resp = self.llm.invoke(prompt)
                answer = resp.content
                usage = resp.response_metadata.get("token_usage", {})
                token_cost = usage.get("total_tokens", 0)
                self.total_token_count += token_cost
                break
            except (APITimeoutError, APIConnectionError, RateLimitError) as e:
                print("限流/网络异常，重试中...")
                if i < MAXRETRIES-1:
                    waittime=2**i
                    print(f"等待{waittime}秒后重试")
                    time.sleep(2**i)
                else:
                    print("三次重试均失败，已触发降级策略,返回原文")
                    answer=context
            except AuthenticationError as e:
                print("key失效，ai暂不可用，返回原文")
                answer=context
                break
            except (BadRequestError, PermissionDeniedError) as e:
                answer="参数或权限错误"
                break
            except Exception as e:
                print(f"未知错误: {e}")
                answer = "发生未知错误。"
                break
        return answer,token_cost
