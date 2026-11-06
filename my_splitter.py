import time

from openai import(APITimeoutError, APIConnectionError, RateLimitError,
    AuthenticationError, BadRequestError, PermissionDeniedError)

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

from openai import OpenAI
client = OpenAI(api_key="sk-0fc1290a66604007a5c1715d397c0736", base_url="https://api.deepseek.com")

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
    except (APITimeoutError, APIConnectionError, RateLimitError) as e:
        print("限流/网络异常，重试中...")
        if i < MAXRETRIES-1:
            waittime=2**i
            print(f"等待{waittime}秒后重试")
            time.sleep(2**i)
        else:
            print("三次重试均失败，已触发降级策略,返回原文")
            answer=related
    except AuthenticationError as e:
        print("key失效，ai暂不可用，返回原文")
        answer=related
        break
    except (BadRequestError, PermissionDeniedError) as e:
        answer="参数或权限错误"
        break
    except Exception as e:
        print(f"未知错误: {e}")
        answer = "发生未知错误。"
        break
print("\n模型回答：")
print(answer)