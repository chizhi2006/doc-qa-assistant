import gradio as gr
import requests

# FastAPI 服务器的地址
API_URL = "http://127.0.0.1:8000/chat"

def chat_with_rag(message, history):
    """这个函数负责把前端网页的提问发给后端 FastAPI"""
    # 1. 把用户的问题打包成 JSON
    payload = {"text": message}
    
    try:
        # 2. 用 requests 发送 POST 请求给你的 FastAPI
        response = requests.post(API_URL, json=payload)
        response.raise_for_status() # 如果请求失败会报错
        
        # 3. 解析后端返回的 JSON 字典
        data = response.json()
        answer = data.get("answer", "未获取到回答")
        cost = data.get("token_cost", 0)
        total = data.get("total_system_cost", 0)
        
        # 4. 拼接最终显示在网页上的字
        final_output = f"{answer}\n\n---\n💰 本次消耗: {cost} Tokens | 📈 累计: {total} Tokens"
        return final_output
        
    except Exception as e:
        return f"连接后端失败，请检查服务器是否开启。错误：{e}"

# === 用 Gradio 画网页 ===
# 这就是一个极简的 ChatGPT 界面
demo = gr.ChatInterface(
    fn=chat_with_rag,
    title="📚 专属文档问答助手 (RAG)",
    description="基于 DeepSeek 与 LangChain 构建，支持中文语义检索与 Token 监控。"
)

if __name__ == "__main__":
    # 启动网页
    demo.launch()