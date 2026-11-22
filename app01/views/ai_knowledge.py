"""
制度知识库问答（任务书 T3）
- 新建 Knowledge 表（标题、内容），预置若干制度条目；
- 用户提问 → SQL 关键词检索相关条目 → 拼入提示词 → 返回答案；
- 资料中没有的内容必须回答“不知道”。
"""
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from app01.models import Knowledge
from app01.utils.ai import llm_client
from app01.utils.validators import sanitize_input


# 检索命中的最大条目数
MAX_MATCH = 5

# 三段式系统提示词：角色 + 依据资料作答的要求 + 输出格式
KB_SYSTEM_PROMPT = """【角色】
你是公司内部制度问答助手，只依据下面提供的“公司制度资料”回答员工提问。

【要求】
1. 答案必须严格来自所给资料，不得使用资料以外的常识或臆测补充制度细节。
2. 如果资料中没有与问题相关的内容，必须直接回答“不知道，相关制度请咨询人事部”，不要强行作答。
3. 不得编造资料中未出现的金额、天数、比例、流程节点。
4. 回答简洁明了，先给出结论，必要时引用资料中的条款。

【输出格式】
直接输出回答正文，不要复述问题，不要输出资料原文。
"""


def _search_keywords(question):
    """从提问中提取检索关键词：英文/数字按词，中文取二元组，提升中文命中。"""
    import re
    keywords = []
    # 英文单词、数字
    keywords += re.findall(r"[A-Za-z0-9]+", question)
    # 中文片段按标点切分后取二元组（如“报销”“请假”“迟到”）
    for seg in re.split(r"[^\u4e00-\u9fa5]+", question):
        seg = seg.strip()
        if len(seg) >= 2:
            keywords.append(seg)
            for i in range(len(seg) - 1):
                keywords.append(seg[i:i + 2])
    # 去重并过滤过短词
    return list(dict.fromkeys(kw for kw in keywords if len(kw) >= 2))


def _search_knowledge(question):
    """按关键词对标题、内容做 SQL 模糊检索，返回相关条目。"""
    keywords = _search_keywords(question)
    queryset = Knowledge.objects.all()
    if keywords:
        q_obj = Q()
        for kw in keywords:
            q_obj |= Q(title__icontains=kw) | Q(content__icontains=kw)
        queryset = queryset.filter(q_obj)
    else:
        # 关键词不足时，退化为对整句做一次模糊匹配
        queryset = queryset.filter(
            Q(title__icontains=question) | Q(content__icontains=question)
        )
    return queryset[:MAX_MATCH]


def knowledge_page(request):
    """制度问答页面"""
    return render(request, "app01/ai_knowledge.html")


@csrf_exempt
def knowledge_ask(request):
    """AJAX：基于知识库回答提问"""
    if request.method != "POST":
        return JsonResponse({"status": False, "msg": "请求方式错误"})

    question = request.POST.get("question", "")
    ok, cleaned, error = sanitize_input(question)
    if not ok:
        return JsonResponse({"status": False, "msg": error})

    matched = _search_knowledge(cleaned)
    if not matched:
        # 未检索到任何资料条目，直接按要求兜底
        return JsonResponse({
            "status": True,
            "answer": "不知道，相关制度请咨询人事部。",
            "source": []
        })

    # 把命中的资料拼入提示词（上下文注入）
    context_lines = [f"【{item.title}】\n{item.content}" for item in matched]
    context_text = "\n\n".join(context_lines)
    prompt = f"公司制度资料：\n{context_text}\n\n员工提问：{cleaned}"

    answer = llm_client.chat(prompt=prompt, system_prompt=KB_SYSTEM_PROMPT)
    return JsonResponse({
        "status": True,
        "answer": answer,
        "source": [item.title for item in matched]
    })
