from __future__ import annotations

import json
import re


def parse_json5(text: str) -> dict:
    """
    轻量 JSON5 解析器：使用状态机移除单行注释，再用正则移除尾逗号，
    最终交给 json.loads。
    """
    result: list[str] = []
    i = 0
    n = len(text)
    in_string = False
    escape_next = False

    while i < n:
        ch = text[i]

        if escape_next:
            result.append(ch)
            escape_next = False
            i += 1
            continue

        if in_string:
            if ch == "\\":
                result.append(ch)
                escape_next = True
            elif ch == '"':
                result.append(ch)
                in_string = False
            else:
                result.append(ch)
            i += 1
            continue

        if ch == '"':
            in_string = True
            result.append(ch)
            i += 1
            continue

        # 单行注释
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue

        result.append(ch)
        i += 1

    cleaned = "".join(result)
    # 移除尾逗号（对象/数组末尾）
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
    return json.loads(cleaned)
