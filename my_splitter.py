import time
from my_utils import advanced_splitter
# === 主程序 ===
with open("note.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = advanced_splitter(text)
print(f"切块完成，共切出 {len(chunks)} 块。\n")

question = input("请输入要查询的信息：")
related = ""

# 修复 Bug：中文不能按空格分，且应该收集所有相关的块
clean_q = question.replace("？", "").replace("。", "").replace(" ", "")
for chunk in chunks:
    # 用问题里的前4个字做模糊匹配（简陋版中文匹配）
    if clean_q[:4] in chunk:
        related += chunk + "\n"

if related == "":
    related = chunks[0]
    print("未匹配到，使用默认第一块。")
else:
    print("成功检索到相关块！")

print("\n=== 正在发送给大模型的参考资料 ===")
print(related)
print("==================================\n")

from openai import OpenAI
client = OpenAI(api_key="", base_url="https://api.deepseek.com")

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

print("\n模型回答：")
print(answer)