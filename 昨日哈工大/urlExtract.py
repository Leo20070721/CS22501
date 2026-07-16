import re

def main(html: str, path_prefix: str):
    BASE_URL = "https://today.hit.edu.cn"

    # 构建匹配模式：href="/article/2026/04/25/....."
    # 考虑引号可能是双引号或单引号，路径开头的斜杠也可能没有
    # 转义 path_prefix 中的特殊字符
    escaped_prefix = re.escape(path_prefix)
    # 匹配 href="...path_prefix..." 或 href='...path_prefix...'，后面跟任意非空白字符
    pattern = fr'href\s*=\s*["\']({escaped_prefix}[^\s"\']+)["\']'
    matches = re.findall(pattern, html, re.IGNORECASE)

    urls = []
    for relative_url in matches:
        if relative_url.startswith('/'):
            full_url = BASE_URL + relative_url
        else:
            full_url = BASE_URL + '/' + relative_url
        urls.append(full_url)

    # 去重
    urls = list(dict.fromkeys(urls))

    return {"urls": urls}