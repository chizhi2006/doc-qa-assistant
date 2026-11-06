import time
# 1. 读文件
with open("note.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 2. 切块
chunks = []
# TODO: 把 text 每 500 字切一块，放进 chunks
for i in range(0,len(text),500):
    temp=text[i:i+500]
    chunks.append(temp)
    print(f"第{i}块长度：{len(temp)}")
# 3. 找相关块
question = input("请输入要查询的信息：")
related = ""
# TODO: 遍历 chunks，找包含问题关键词的那块
for chunk in chunks:
    for word in question.split():
        if word in chunk:
            related = chunk
            break
    if related != "":
        break
if related=="":
   related=chunks[0]

# 4. 拼 prompt 调模型
from openai import OpenAI
client = OpenAI(
    api_key="",
    base_url="https://api.deepseek.com"
)
prompt = f"请根据以下内容回答问题。\n内容:{related}\n问题:{question}"
print("正在请求模型...")
MAXRETRIES=3
for i in range(MAXRETRIES):
    try: 
        resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role":"user","content":prompt}],
        timeout=10
        )
        answer = resp.choices[0].message.content
        break
    except Exception as e:
        print(f"第{i+1}次尝试失败，错误原因：{e}")
        if i < MAXRETRIES-1:
            print("等待两秒后重试")
            time.sleep(2)
        else:
            answer="三次重试均失败，已触发降级策略"
print(answer)
# 5. 加重试

# 6. 打印 token（你会）