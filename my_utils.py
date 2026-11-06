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