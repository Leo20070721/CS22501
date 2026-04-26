import re
import time

def main(html: str):
    # ---------- 1 秒延时 ----------
    time.sleep(1)

    # ---------- 辅助函数：根据 plugin-id 提取完整的块 ----------
    def extract_block_by_plugin_id(html, plugin_id):
        # 匹配开始标签
        start_pattern = re.compile(
            r'<div[^>]*data-block-plugin-id\s*=\s*["\']' + re.escape(plugin_id) + r'["\'][^>]*>',
            re.IGNORECASE | re.DOTALL
        )
        match = start_pattern.search(html)
        if not match:
            return ""
        start_pos = match.end()
        # 逐字符遍历，计算 div 嵌套深度
        depth = 1
        i = start_pos
        while i < len(html) and depth > 0:
            next_open = html.find('<div', i)
            next_close = html.find('</div>', i)
            if next_open == -1 and next_close == -1:
                break
            # 选择较近的标记
            if next_open != -1 and (next_close == -1 or next_open < next_close):
                # 检查是否为真正的 <div 开始（排除 </div 或 <div/>
                if html[next_open:next_open+4].lower() == '<div':
                    depth += 1
                i = next_open + 4
            elif next_close != -1:
                depth -= 1
                if depth == 0:
                    end_pos = next_close + len('</div>')
                    return html[match.start():end_pos]
                i = next_close + len('</div>')
            else:
                i += 1
        return ""

    # ---------- 提取纯文本辅助函数 ----------
    def clean_text(html_text):
        text = re.sub(r'<[^>]+>', ' ', html_text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    # ---------- 提取结果初始化 ----------
    title = ""
    date = ""
    tags = ""
    content = ""
    has_attachments = "False"
    source = ""

    # ---------- 1. 标题块 ----------
    title_block = extract_block_by_plugin_id(html, 'article_tilte_block')
    if title_block:
        # 标题
        h3_match = re.search(r'<h3>(.*?)</h3>', title_block, re.DOTALL | re.IGNORECASE)
        if h3_match:
            title = clean_text(h3_match.group(1))
        # 日期
        date_match = re.search(r'<div[^>]*class\s*=\s*"left-attr\s+first"[^>]*>(.*?)</div>', title_block, re.DOTALL | re.IGNORECASE)
        if date_match:
            date = clean_text(date_match.group(1))
        # 标签（在 class="second" 内）
        second_match = re.search(r'<div[^>]*class\s*=\s*"second"[^>]*>(.*?)</div>\s*$', title_block, re.DOTALL | re.IGNORECASE)
        if not second_match:
            # 如果上面的不行，尝试更宽松的匹配
            second_match = re.search(r'<div[^>]*class\s*=\s*"second"[^>]*>(.*?)</div>', title_block, re.DOTALL | re.IGNORECASE)
        if second_match:
            second_html = second_match.group(1)
            # 提取所有 a 标签内的文本
            a_texts = re.findall(r'<a[^>]*>(.*?)</a>', second_html, re.DOTALL | re.IGNORECASE)
            clean_tags = [clean_text(t) for t in a_texts if clean_text(t)]
            # 去重
            seen = set()
            unique = []
            for t in clean_tags:
                if t not in seen:
                    seen.add(t)
                    unique.append(t)
            tags = ";".join(unique)

    # ---------- 2. 正文块 ----------
    body_block = extract_block_by_plugin_id(html, 'entity_field:node:body')
    if body_block:
        # 找到 article-content 类的 div
        article_match = re.search(r'<div[^>]*class\s*=\s*"article-content[^"]*"[^>]*>(.*?)</div>', body_block, re.DOTALL | re.IGNORECASE)
        if article_match:
            content = clean_text(article_match.group(1))

    # ---------- 3. 附件块 ----------
    attach_block = extract_block_by_plugin_id(html, 'entity_field:node:attachments')
    if attach_block:
        # 检查是否有 field__items 或 a 标签
        if re.search(r'class\s*=\s*"field__items"', attach_block, re.IGNORECASE) and re.search(r'<a\s', attach_block, re.IGNORECASE):
            has_attachments = "True"

    # ---------- 4. 脚注块 ----------
    footer_block = extract_block_by_plugin_id(html, 'article_content_footer_block')
    if footer_block:
        # 提取“来源：”后的 a 标签
        source_match = re.search(r'来源\s*：\s*<span>\s*<a[^>]*>(.*?)</a>', footer_block, re.DOTALL | re.IGNORECASE)
        if source_match:
            source = clean_text(source_match.group(1))

    # ---------- 返回单对象 ----------
    return {
        "article": {
            "title": title,
            "date": date,
            "tags": tags,
            "content": content,
            "has_attachments": has_attachments,
            "source": source
        }
    }