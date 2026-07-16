def main(articles: list):
    # 粗略估算 token 数：
    # 中文字符约占 1.5 字符/token，非中文字符约占 4 字符/token
    chinese_chars = 0
    other_chars = 0
    for item in articles:
        for ch in item:
            if '\u4e00' <= ch <= '\u9fff':
                chinese_chars += 1
            else:
                other_chars += 1
    estimated = int(chinese_chars * 0.7 + other_chars * 0.4)
    return {"token_count": estimated}