"""
多轮对话助手（任务书 T5，加分项）
- 维护最近几轮对话历史，支持连续追问（如“那如果缺勤呢？”）；
- 历史存放在 session 中，按最近 N 轮截断；
- 支持在浮窗“设置”中填写硅基流动 API 密钥，密钥存 session；
- 复用统一输入校验、超时与失败兜底（T6）。
"""
import json
import os
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from app01.models import Employee, Department, User
from app01.utils.ai import llm_client
from app01.utils.validators import sanitize_input

# session 中保存的最大消息条数（user + assistant 各算一条）
MAX_HISTORY_MESSAGES = 10

# session 键名
SESSION_HISTORY = "ai_chat_history"
SESSION_API_KEY = "llm_api_key"

CHAT_SYSTEM_PROMPT = """【角色】
你是企业员工的智能办公助手，回答友好、简洁、专业。

【要求】
1. 结合上下文理解用户的连续追问，指代不清时结合上一轮内容回答。
2. 与办公、人事、日常问题无关的内容，礼貌说明只能协助办公相关问题。
3. 回答使用中文，条理清晰。
4. 涉及员工人数、部门数量等系统内数据时，以下方“当前系统数据概览”为准直接回答；概览中没有的数据，不要凭空编造。
"""


def _system_overview():
    """汇总系统内的实时统计概览，作为上下文注入对话，便于回答人数类问题。"""
    emp_count = Employee.objects.count()
    dept_count = Department.objects.count()
    user_count = User.objects.count()
    return (
        "【当前系统数据概览】\n"
        f"- 在职员工（员工档案）共 {emp_count} 人；\n"
        f"- 部门共 {dept_count} 个；\n"
        f"- 系统登录账号共 {user_count} 个。"
    )


def _load_history(request):
    """从 session 读取对话历史（list[dict]）。"""
    history = request.session.get(SESSION_HISTORY, [])
    return history if isinstance(history, list) else []


def _save_history(request, history):
    """截断后写回 session。"""
    history = history[-MAX_HISTORY_MESSAGES:]
    request.session[SESSION_HISTORY] = history
    request.session.modified = True


def _get_api_key(request):
    """取本次调用使用的密钥：session 临时密钥优先，其次环境变量。"""
    return request.session.get(SESSION_API_KEY, "") or None


def chat_page(request):
    """多轮对话页面；新会话可清空历史"""
    if request.GET.get("reset") == "1":
        request.session.pop(SESSION_HISTORY, None)
    return render(request, "app01/ai_chat.html")


@csrf_exempt
def chat_message(request):
    """AJAX：发送一条消息，返回模型回复并更新历史"""
    if request.method != "POST":
        return JsonResponse({"status": False, "msg": "请求方式错误"})

    message = request.POST.get("message", "")
    ok, cleaned, error = sanitize_input(message)
    if not ok:
        return JsonResponse({"status": False, "msg": error})

    history = _load_history(request)
    system_prompt = CHAT_SYSTEM_PROMPT + "\n" + _system_overview()
    answer = llm_client.chat(
        prompt=cleaned,
        system_prompt=system_prompt,
        history=history,
        api_key=_get_api_key(request),
    )

    # 把本轮问答追加进历史，供下一轮上下文使用
    history.append({"role": "user", "content": cleaned})
    history.append({"role": "assistant", "content": answer})
    _save_history(request, history)

    return JsonResponse({"status": True, "answer": answer})


@csrf_exempt
def chat_stream(request):
    """
    SSE 流式对话（T7）：边生成边把文本片段推给前端，页面即时出字。

    每个事件格式：data: {"t": "文本片段"}\\n\\n
    结束事件：data: [DONE]
    """
    message = request.POST.get("message", "")
    ok, cleaned, error = sanitize_input(message)
    if not ok:
        return JsonResponse({"status": False, "msg": error})

    history = _load_history(request)
    system_prompt = CHAT_SYSTEM_PROMPT + "\n" + _system_overview()
    api_key = _get_api_key(request)

    def event_stream():
        """生成器：逐段推送模型输出，结束后把本轮问答写入 session。"""
        collected = []
        try:
            for piece in llm_client.stream(
                prompt=cleaned,
                system_prompt=system_prompt,
                history=history,
                api_key=api_key,
            ):
                collected.append(piece)
                # ensure_ascii=False 保证中文原样输出，不转成 \\uXXXX
                yield "data: " + json.dumps({"t": piece}, ensure_ascii=False) + "\n\n"
        except Exception as exc:  # noqa: BLE001 - 流中断也要给前端一句提示
            yield "data: " + json.dumps(
                {"t": "服务异常，请稍后重试。"}, ensure_ascii=False
            ) + "\n\n"
        finally:
            answer = "".join(collected).strip()
            if answer and cleaned:
                new_history = history + [
                    {"role": "user", "content": cleaned},
                    {"role": "assistant", "content": answer},
                ]
                request.session[SESSION_HISTORY] = new_history[-MAX_HISTORY_MESSAGES:]
                request.session.modified = True
                try:
                    request.session.save()  # 流式响应下需手动落盘，否则会话历史丢失
                except Exception:  # noqa: BLE001 - 保存失败不影响本轮回答
                    pass
            yield "data: [DONE]\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # 禁止代理缓冲，保证逐字到达
    return response


@csrf_exempt
def chat_clear(request):
    """清空对话历史（不清空密钥）"""
    if request.method != "POST":
        return JsonResponse({"status": False, "msg": "请求方式错误"})
    request.session.pop(SESSION_HISTORY, None)
    return JsonResponse({"status": True, "msg": "对话已清空"})


@csrf_exempt
def chat_save_key(request):
    """保存硅基流动 API 密钥到 session（浮窗设置）"""
    if request.method != "POST":
        return JsonResponse({"status": False, "msg": "请求方式错误"})

    api_key = request.POST.get("api_key", "").strip()
    if not api_key:
        return JsonResponse({"status": False, "msg": "密钥不能为空"})
    if len(api_key) > 128:
        return JsonResponse({"status": False, "msg": "密钥长度不合法"})

    request.session[SESSION_API_KEY] = api_key
    request.session.modified = True
    return JsonResponse({"status": True, "msg": "密钥已保存"})


@csrf_exempt
def chat_clear_key(request):
    """清除 session 中保存的密钥，回退到环境变量配置"""
    if request.method != "POST":
        return JsonResponse({"status": False, "msg": "请求方式错误"})
    request.session.pop(SESSION_API_KEY, None)
    return JsonResponse({"status": True, "msg": "已清除临时密钥"})


def chat_key_status(request):
    """返回当前是否已配置密钥（供前端浮窗显示状态）"""
    has_key = bool(_get_api_key(request)) or bool(os.environ.get("LLM_API_KEY", ""))
    return JsonResponse({"status": True, "has_key": has_key})
