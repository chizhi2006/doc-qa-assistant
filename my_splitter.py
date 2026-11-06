import time

def advanced_splitter(text, chunk_size=500, overlap=50):
    separators = ["\n\n", "。", ""]
    chunks = []
    
    # 切分工具
    def split_text(text, separator):
        if separator == "":
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        else:
            parts = text.split(separator)
            return [p + separator for p in parts if p]
            
    # 核心流水线
    paragraphs = split_text(text, separators[0])
    
    for para in paragraphs:
        # 如果段落本身不长，直接作为一个完整的块处理
        if len(para) <= chunk_size:
            # 处理重叠：把上一块的尾巴拼到这一块前面
            if chunks:
                tail = chunks[-1][-overlap:]
                chunks.append(tail + para)
            else:
                chunks.append(para)
        else:
            # 如果段落太长，按句号切
            sentences = split_text(para, separators[1])
            current_chunk = ""
            
            for sentence in sentences:
                # 修复 Bug：不要一句一句存，要拼接到 current_chunk 里
                if len(sentence) > chunk_size:
                    # 如果单句还超长，只能硬切
                    hard_parts = split_text(sentence, separators[2])
                    for hp in hard_parts:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = hp  # 重置当前块
                else:
                    # 如果加上这句话还没超标，就拼进去
                    if len(current_chunk) + len(sentence) <= chunk_size:
                        current_chunk += sentence
                    else:
                        # 超标了，把当前拼好的存起来
                        if current_chunk:
                            chunks.append(current_chunk)
                        # 新的一块，带上上一块的尾巴（overlap）
                        tail = chunks[-1][-overlap:] if chunks else ""
                        current_chunk = tail + sentence
                        
            # 循环结束，把最后没存进去的 current_chunk 存进去
            if current_chunk:
                chunks.append(current_chunk)
                
    return chunks


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