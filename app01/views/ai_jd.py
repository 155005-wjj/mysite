"""
智能生成招聘 JD（任务书 T2）
- 输入岗位名称，输出结构化招聘 JD（职责 / 要求 / 薪资）
- 提示词采用三段式模板：角色 + 要求 + 输出格式
- 前端通过 AJAX 调用并在页面渲染结果
"""
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from app01.utils.ai import llm_client
from app01.utils.validators import sanitize_input


# 三段式系统提示词：角色（第一段）+ 要求（第二段）+ 输出格式（第三段）
JD_SYSTEM_PROMPT = """【角色】
你是一名资深 HR 招聘专家，熟悉各岗位的招聘文案撰写。

【要求】
1. 根据用户给出的岗位名称，撰写一份规范、可直接发布的招聘 JD。
2. 内容结合岗位常见职责与任职要求，表述专业、客观，不编造具体公司名。
3. 薪资范围给出合理的市场区间（人民币/月），如无明确信息可按岗位常见水平估算。

【输出格式】
严格按以下三个小标题输出，每个小标题下用分条列表，不要输出多余解释：
## 岗位职责
1. ...
## 任职要求
1. ...
## 薪资范围
- 月薪：Xk–Yk
- 其他福利：...
"""


def jd_page(request):
    """招聘 JD 生成页面"""
    return render(request, "app01/ai_jd.html")


@csrf_exempt
def jd_generate(request):
    """AJAX：根据岗位名称生成招聘 JD"""
    if request.method != "POST":
        return JsonResponse({"status": False, "msg": "请求方式错误"})

    job_name = request.POST.get("job_name", "")
    ok, cleaned, error = sanitize_input(job_name, max_length=50)
    if not ok:
        return JsonResponse({"status": False, "msg": error})

    answer = llm_client.chat(prompt=f"请为岗位「{cleaned}」撰写招聘 JD。",
                             system_prompt=JD_SYSTEM_PROMPT)
    return JsonResponse({"status": True, "jd": answer})
