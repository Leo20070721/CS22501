import re
import time

def main(html: str):
    # ---------- 1 秒延时（避免请求过快） ----------
    time.sleep(1)

    # ---------- 初始化结果 ----------
    title = ""
    date = ""
    tags = ""
    content = ""
    has_attachments = False
    source = ""

    # ---------- 辅助函数：提取指定块内的所有文本 ----------
    def extract_text_in_block(block_html):
        """去除所有 HTML 标签，返回纯文本，合并空白"""
        clean = re.sub(r'<[^>]+>', ' ', block_html)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    # ---------- 1. 提取标题块 ----------
    # 匹配 data-block-plugin-id="article_tilte_block" 的整个 div
    title_block_pattern = r'<div[^>]*data-block-plugin-id\s*=\s*["\']article_tilte_block["\'][^>]*>.*?</div>\s*</div>'
    title_match = re.search(title_block_pattern, html, re.DOTALL | re.IGNORECASE)
    if title_match:
        title_block = title_match.group(0)
        # 提取 h3 标题
        h3_match = re.search(r'<h3>(.*?)</h3>', title_block, re.DOTALL | re.IGNORECASE)
        if h3_match:
            title = extract_text_in_block(h3_match.group(1))
        # 提取时间 (class="left-attr first")
        date_match = re.search(r'<div[^>]*class\s*=\s*["\']left-attr\s+first["\'][^>]*>(.*?)</div>', title_block, re.DOTALL | re.IGNORECASE)
        if date_match:
            date = extract_text_in_block(date_match.group(1))
        # 提取标签 (在 class="second" 中的 a 标签)
        tags_block_pattern = r'<div[^>]*class\s*=\s*["\']second["\'][^>]*>(.*?)</div>'
        tags_block_match = re.search(tags_block_pattern, title_block, re.DOTALL | re.IGNORECASE)
        if tags_block_match:
            tags_block = tags_block_match.group(1)
            # 提取所有 a 标签内的文本
            a_tags = re.findall(r'<a[^>]*>(.*?)</a>', tags_block, re.DOTALL | re.IGNORECASE)
            tag_list = [extract_text_in_block(t) for t in a_tags if extract_text_in_block(t)]
            # 去重并保持顺序
            seen = set()
            unique_tags = []
            for t in tag_list:
                if t not in seen:
                    seen.add(t)
                    unique_tags.append(t)
            tags = ";".join(unique_tags)

    # ---------- 2. 提取正文块 ----------
    body_block_pattern = r'<div[^>]*data-block-plugin-id\s*=\s*["\']entity_field:node:body["\'][^>]*>(.*?)</div>\s*</div>'
    body_match = re.search(body_block_pattern, html, re.DOTALL | re.IGNORECASE)
    if body_match:
        body_block = body_match.group(1)
        # 提取 <div class="article-content ..."> 内的内容
        article_match = re.search(r'<div[^>]*class\s*=\s*["\']article-content[^"\']*["\'][^>]*>(.*?)</div>', body_block, re.DOTALL | re.IGNORECASE)
        if article_match:
            content = extract_text_in_block(article_match.group(1))

    # ---------- 3. 检查附件 ----------
    attachment_block_pattern = r'<div[^>]*data-block-plugin-id\s*=\s*["\']entity_field:node:attachments["\'][^>]*>'
    attach_match = re.search(attachment_block_pattern, html, re.IGNORECASE)
    if attach_match:
        # 进一步检查里面是否有 field__items 或 file 链接
        if re.search(r'class\s*=\s*["\']field__items["\']', html, re.IGNORECASE):
            has_attachments = True

    # ---------- 4. 提取来源机构 ----------
    footer_block_pattern = r'<div[^>]*data-block-plugin-id\s*=\s*["\']article_content_footer_block["\'][^>]*>(.*?)</div>\s*</div>'
    footer_match = re.search(footer_block_pattern, html, re.DOTALL | re.IGNORECASE)
    if footer_match:
        footer_block = footer_match.group(1)
        # 查找“来源：”后面的 a 标签
        source_match = re.search(r'来源\s*：\s*<span>\s*<a[^>]*>(.*?)</a>', footer_block, re.DOTALL | re.IGNORECASE)
        if source_match:
            source = extract_text_in_block(source_match.group(1))

    # ---------- 返回 ----------
    return {
        "article": {               # 这个返回变量名可以自己取，比如 "article"
            "title": title,
            "date": date,
            "tags": tags,
            "content": content,
            "has_attachments": has_attachments,
            "source": source
        }}