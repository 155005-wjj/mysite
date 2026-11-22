"""
AI 模块输入校验与安全工具（对应任务书 T6 安全与健壮性）
"""
import re

# 允许输入的最大字符数
MAX_INPUT_LENGTH = 500

# 简单敏感词/越权关键词过滤（可按需扩充）
BLOCKED_PATTERNS = [
    re.compile(r"密码|口令|验证码|token|api\s*key", re.IGNORECASE),
    re.compile(r"删除|drop\s+table|delete\s+from|insert\s+into", re.IGNORECASE),
]


def sanitize_input(text, max_length=MAX_INPUT_LENGTH):
    """
    校验用户输入。
    :return: (是否通过, 清洗后文本, 错误提示)
    """
    if text is None:
        return False, "", "输入内容不能为空。"

    text = str(text).strip()
    if not text:
        return False, "", "输入内容不能为空。"

    if len(text) > max_length:
        return False, text[:max_length], f"输入内容过长，请控制在 {max_length} 字以内。"

    for pattern in BLOCKED_PATTERNS:
        if pattern.search(text):
            return False, text, "输入内容包含不允许的信息，请更换提问方式。"

    return True, text, ""
