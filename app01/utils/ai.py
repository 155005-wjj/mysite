"""
大模型（LLM）统一封装

任务书要求：
- 统一封装 LLMClient，对外只暴露 chat(prompt) -> str 方法；
- API_KEY / BASE_URL / MODEL 一律走环境变量，禁止硬编码进代码；
- 调用失败必须返回友好提示，不允许页面报错崩溃；
- 支持模型参数 temperature、超时控制与失败兜底。

默认接入硅基流动 SiliconCloud（OpenAI 兼容接口，免费模型）：
- BASE_URL: https://api.siliconflow.cn/v1
- 模型 ID 带厂商前缀，如 Qwen/Qwen2-7B-Instruct

密钥来源优先级：调用时传入的临时密钥 > 环境变量 LLM_API_KEY。
"""
import os
import logging

logger = logging.getLogger("app01.ai")

# 调用失败时返回给前端的友好提示（不把异常堆栈暴露到页面）
DEFAULT_FALLBACK = "智能助手暂时不可用，请稍后再试，或检查大模型密钥与网络配置。"

# 单次请求超时（秒），避免接口长时间挂起
DEFAULT_TIMEOUT = 20

# 输入长度上限（字符），超出部分截断，防止超长提示词
MAX_PROMPT_LENGTH = 4000

# 默认硅基流动配置（可被环境变量覆盖）
DEFAULT_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL = "Qwen/Qwen3.5-4B"
# 备选模型：主模型排队时的兜底，实测首字约 0.6 秒
DEFAULT_FALLBACK_MODEL = "Qwen/Qwen2.5-7B-Instruct"
# 主模型首字等待上限（秒），超过即切换备选模型
DEFAULT_FIRST_TOKEN_TIMEOUT = 8


def _clean_prompt(prompt):
    """输入清洗：转字符串、去首尾空白、限制长度（T6 安全与健壮性）。"""
    if prompt is None:
        return ""
    text = str(prompt).strip()
    if len(text) > MAX_PROMPT_LENGTH:
        text = text[:MAX_PROMPT_LENGTH]
    return text


class LLMClient:
    """大模型客户端：读取环境变量配置，对外提供 chat 方法。"""

    def __init__(self, api_key=None, base_url=None, model=None,
                 temperature=None, timeout=None):
        # 显式传入优先，其次读环境变量，最后用默认值
        self.api_key = api_key or os.environ.get("LLM_API_KEY", "")
        self.base_url = (base_url or os.environ.get("LLM_BASE_URL")
                         or DEFAULT_BASE_URL)
        self.model = model or os.environ.get("LLM_MODEL", DEFAULT_MODEL)
        self.temperature = temperature if temperature is not None else float(
            os.environ.get("LLM_TEMPERATURE", "0.7")
        )
        self.timeout = timeout or int(os.environ.get("LLM_TIMEOUT", str(DEFAULT_TIMEOUT)))
        # 主备模型：免费模型排队时首字可能几十秒，超时自动换备选模型保证可用
        self.fallback_model = os.environ.get("LLM_MODEL_FALLBACK", DEFAULT_FALLBACK_MODEL)
        self.first_token_timeout = int(
            os.environ.get("LLM_FIRST_TOKEN_TIMEOUT", str(DEFAULT_FIRST_TOKEN_TIMEOUT))
        )
        self._client = None
        self._client_key = None

    def _get_client(self, api_key=None, timeout=None):
        """惰性创建 OpenAI 兼容客户端；未配置 Key 时抛出明确异常。"""
        key = api_key or self.api_key
        if not key:
            raise RuntimeError("未配置大模型 API 密钥")

        timeout = timeout or self.timeout
        cache_key = (key, timeout)

        # 密钥或超时变化时重建客户端；max_retries=0 关闭 SDK 自动重试，避免叠加超时等待
        if self._client is None or self._client_key != cache_key:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=key,
                base_url=self.base_url or None,
                timeout=timeout,
                max_retries=0,
            )
            self._client_key = cache_key
        return self._client

    def chat(self, prompt, system_prompt=None, history=None, fallback=None,
             api_key=None):
        """
        调用大模型，返回模型回答文本。

        :param prompt: 用户本轮输入（字符串）
        :param system_prompt: 系统提示词（角色/要求/输出格式）
        :param history: 多轮历史 [{"role": "user"/"assistant", "content": "..."}]
        :param fallback: 调用失败时返回的友好提示
        :param api_key: 本次调用使用的临时密钥（如 session 中保存的密钥）
        :return: 模型回答字符串；任何异常都回退到友好提示，不向外抛出
        """
        prompt = _clean_prompt(prompt)
        if not prompt:
            return "请输入有效内容后再提问。"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": str(system_prompt).strip()})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        last_exc = None

        # 按主→备顺序尝试流式：主模型首字超时则自动切换备选模型
        for model, model_timeout in self._model_attempts():
            try:
                client = self._get_client(api_key=api_key, timeout=model_timeout)
                parts = []
                for text in self._stream_one(client, messages, model, timeout=model_timeout):
                    parts.append(text)
                answer = "".join(parts).strip()
                if answer:
                    return answer
            except Exception as exc:  # noqa: BLE001 - 换下一个模型继续试
                last_exc = exc
                logger.warning("模型 %s 流式调用失败：%s", model, exc)
                # 余额不足/密钥无效属于账号级问题，换模型也一样失败，直接停止重试
                if self._is_account_error(exc):
                    return fallback or self._friendly_error(exc)

        # 全部流式失败，最后一次尝试普通一次性返回
        try:
            client = self._get_client(api_key=api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                timeout=self.timeout,
            )
            answer = response.choices[0].message.content
            return (answer or "").strip() or "模型返回为空，请换个问法再试。"
        except Exception as exc:  # noqa: BLE001 - 统一兜底，保证页面不崩溃
            logger.exception("大模型调用失败：%s", exc)
            return fallback or self._friendly_error(exc or last_exc)

    def _model_attempts(self):
        """返回按优先级排列的 (模型, 超时) 列表：主模型用首字超时，备选模型用完整超时。"""
        attempts = [(self.model, self.first_token_timeout)]
        if self.fallback_model and self.fallback_model != self.model:
            attempts.append((self.fallback_model, self.timeout))
        return attempts

    def _stream_one(self, client, messages, model, timeout=None):
        """对单个模型做流式调用，逐段 yield 文本。首个片段即代表模型已响应。

        timeout 为本次调用的限时（秒）：主模型传首字超时，到点未出内容即判失败，
        由 chat() 立刻切换到备选模型，避免整段等满长超时。
        """
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=self.temperature,
            timeout=timeout or self.timeout,
            stream=True,
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            text = getattr(delta, "content", None)
            if text:
                yield text

    def _chat_stream(self, client, messages):
        """流式调用并拼接完整文本；无内容时返回空串由调用方回退。"""
        parts = []
        for text in self._stream_one(client, messages, self.model):
            parts.append(text)
        return "".join(parts).strip()

    def stream(self, prompt, system_prompt=None, history=None, api_key=None):
        """
        流式生成器：逐段 yield 模型输出文本，供 SSE 前端逐字显示。

        与 chat() 的区别：不等待整段生成完，调用方拿一段就能渲染一段，
        页面不会长时间只显示“正在思考”。

        :return: 生成器，yield 文本片段（str）；异常时 yield 友好提示后结束
        """
        prompt = _clean_prompt(prompt)
        if not prompt:
            yield "请输入有效内容后再提问。"
            return

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": str(system_prompt).strip()})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        try:
            client = self._get_client(api_key=api_key)
            stream = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                timeout=self.timeout,
                stream=True,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                text = getattr(delta, "content", None)
                if text:
                    yield text
        except Exception as exc:  # noqa: BLE001 - 流式异常也兜底成一句话
            logger.exception("流式对话失败：%s", exc)
            yield self._friendly_error(exc)

    @staticmethod
    def _is_account_error(exc):
        """判断是否为账号级错误（余额不足 402 / 密钥无效 401）：换模型也无法恢复。"""
        code = getattr(exc, "status_code", None)
        if code in (401, 402):
            return True
        text = str(exc)
        return "balance" in text.lower() or "insufficient" in text.lower()

    @staticmethod
    def _friendly_error(exc):
        """把常见异常转成可直接展示的简短原因，便于答辩排障。"""
        name = type(exc).__name__
        text = str(exc)
        # 余额不足优先判断：硅基流动所有模型共用账户余额，额度为 0 时任何模型都报 402
        if "402" in text or "balance" in text.lower() or "insufficient" in text.lower():
            return ("硅基流动账户余额不足（402），所有模型都无法调用。"
                    "请登录 cloud.siliconflow.cn 充值后重试，或在浮窗“密钥”里换一个仍有额度的密钥。")
        if "未配置" in text or "api_key" in text.lower():
            return "未配置大模型密钥，请在浮窗右上角“密钥”中填写，或检查 .env 的 LLM_API_KEY。"
        if name in ("APITimeoutError", "ReadTimeout", "TimeoutException", "httpx.ReadTimeout"):
            return "模型响应超时，请稍后重试（免费模型首字较慢）。"
        if "401" in text or "authentication" in text.lower() or "invalid_api_key" in text.lower():
            return "密钥无效或已过期，请核对硅基流动 API Key。"
        if "403" in text or "Model disabled" in text or "permission" in text.lower():
            return "当前模型不可用或已停用，请在硅基流动模型广场更换可用模型。"
        if "429" in text or "rate" in text.lower():
            return "触发平台限速，请稍等片刻后再试。"
        if name in ("ConnectError", "ConnectionError", "NetworkError"):
            return "网络连接失败，请检查本机能否访问 api.siliconflow.cn。"
        return f"大模型调用失败（{name}）：{text[:120]}"


# 模块级单例，供各视图复用
llm_client = LLMClient()
