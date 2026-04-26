def main(articles: object):    
    # 每个 item 的结构： { "article": { "title": "...", "date": "...", ... } }
    art = articles
    title = art.get("title", "")
    date = art.get("date", "")
    tags = art.get("tags", "")
    source = art.get("source", "")
    has_att = art.get("has_attachments", False)
    content = art.get("content", "")

    # 构建一条公告的文本块
    block = f"""---
标题：{title}
日期：{date}
标签：{tags}
来源：{source}
有无附件：{"是" if has_att else "否"}
正文：
{content}
"""
    output_lines = block
    return {"combined_text": output_lines}