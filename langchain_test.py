import os

# ==========================================
# 【模块 1：核心模型接口 (Chat Models)】
# 作用：用类似 OpenAI 的标准格式去调用 DeepSeek。
# 文档定位：Docs -> Integrations -> Chat Models -> OpenAI
# ==========================================
from langchain_openai import ChatOpenAI

# ==========================================
# 【模块 2：文档加载器 (Document Loaders)】
# 作用：把各种格式的文件（txt, pdf, word）统一读成 LangChain 的 Document 对象。
# 文档定位：Docs -> Components -> Document loaders
# ==========================================
from langchain_community.document_loaders import TextLoader

# ==========================================
# 【模块 3：文本切分器 (Text Splitters)】
# 作用：替代手写的 range 硬切，实现按语义/标点智能切分。
# 文档定位：Docs -> Components -> Text splitters
# ==========================================
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ==========================================
# 【模块 4：向量存储与嵌入 (Vector Stores & Embeddings)】
# 作用：FAISS 负责存向量，HuggingFace 负责把文字变成向量。
# 文档定位：Docs -> Integrations -> Vector Stores -> FAISS
#          Docs -> Integrations -> Embeddings -> HuggingFace
# ==========================================
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# ---------------- 主程序开始 ----------------

# 设置环境变量（告诉 OpenAI 库把请求发给 DeepSeek）
os.environ["OPENAI_API_KEY"] = ""  # 
os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com/v1" 

# 1. 加载文档 (调用 Document Loader)
print("正在加载文档...")
loader = TextLoader("note.txt", encoding="utf-8")
docs = loader.load()

# 2. 智能切分 (调用 Text Splitter)
# chunk_size=500 是块最大长度，chunk_overlap=50 是重叠字数（解决断句问题）
print("正在进行语义切分...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？", " ", ""] # 优先按段落、句号切，最后才硬切
)
splits = text_splitter.split_documents(docs)
print(f"切分完成，共切分为 {len(splits)} 块。")

# 3. 初始化 Embedding 模型并存入 FAISS (调用 Embeddings 和 Vector Store)
# 注意：这里用的是开源模型，第一次运行会自动去 HuggingFace 下载（大概几百兆）
print("正在加载向量模型并构建向量库（初次运行需下载模型，请耐心等待）...")
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

# 把切好的块（splits）和嵌入模型（embeddings）塞进 FAISS
vectorstore = FAISS.from_documents(splits, embeddings)

# 4. 用户提问与检索 (调用 Retriever)
question = input("\n请输入要查询的信息：")

# 把向量库变成检索器，设置每次捞取最相关的 3 个块（Top-K=3）
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
related_docs = retriever.invoke(question)

print("\n检索到的相关片段（你看，它把不同段落都找出来了）：")
for i, doc in enumerate(related_docs):
    # doc.page_content 就是文本内容
    print(f"--- 第 {i+1} 段 ---")
    print(doc.page_content[:100] + "...\n")

# 5. 拼装 Prompt 并请求大模型 (调用 Chat Models)
context = "\n\n".join([doc.page_content for doc in related_docs])
prompt = f"请根据以下内容回答问题。\n内容：{context}\n问题：{question}\n如果你在内容中找不到答案，请直接回答不知道。"

print("正在请求大模型...")
llm = ChatOpenAI(model="deepseek-chat", temperature=0)
answer = llm.invoke(prompt) # invoke 就是发送请求的意思

print("模型回答：")
print(answer.content)