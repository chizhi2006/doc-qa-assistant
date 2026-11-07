from fastapi import FastAPI
from rag_core import RAGSystem
from schemas import QuestionRequest
app=FastAPI()
rag_bot=RAGSystem()
@app.get("/")
def read_root():
    return {"message":"欢迎使用RAG系统"}
@app.post("/chat")
def chat(request:QuestionRequest):
    answer,token_cost=rag_bot.ask(request.text)
    return {
        "answer": answer,
        "token_cost": token_cost,
        "total_system_cost": rag_bot.total_token_count
    }