/*
 * AI 智能助手全站浮窗
 * - 右下角悬浮按钮，点击开合对话面板
 * - 连续多轮对话，历史由后端 session 维护
 * - Enter 发送，Shift+Enter 换行
 * - 设置中可填写硅基流动 API 密钥（存 session）
 */
$(function () {
    var $btn = $("#aiFloatBtn");
    var $panel = $("#aiFloatPanel");
    var $body = $("#aiFloatBody");
    var $input = $("#aiFloatInput");
    var $send = $("#aiFloatSend");
    var $status = $("#aiFloatStatus");
    var $setting = $("#aiFloatSetting");
    var $keyInput = $("#aiFloatKeyInput");
    var $keyMsg = $("#aiFloatKeyMsg");

    // 打开/收起面板
    function togglePanel(open) {
        $panel.toggleClass("open", open);
        if (open) {
            $setting.hide();
            $input.focus();
        }
    }

    $btn.on("click", function () {
        togglePanel(!$panel.hasClass("open"));
    });
    $("#aiFloatCloseBtn").on("click", function () {
        togglePanel(false);
    });

    // 追加气泡
    function appendBubble(role, text) {
        $body.find(".ai-float-empty").remove();
        var cls = role === "user" ? "user" : (role === "system" ? "system" : "assistant");
        var html = '<div class="ai-float-msg ' + cls + '">' +
            '<div class="ai-float-bubble">' + $("<div>").text(text).html() +
            '</div></div>';
        $body.append(html);
        $body.scrollTop($body[0].scrollHeight);
    }

    function setStatus(text) {
        $status.text(text || "");
    }

    // 发送消息（SSE 流式）
    function send() {
        var message = $.trim($input.val());
        if (!message) return;

        appendBubble("user", message);
        $input.val("");
        $send.prop("disabled", true);

        // 流式气泡：先插入空助手气泡，边收边填字
        $body.find(".ai-float-empty").remove();
        var $bubble = $('<div class="ai-float-msg assistant"><div class="ai-float-bubble"></div></div>');
        $body.append($bubble);
        var $text = $bubble.find(".ai-float-bubble");
        var buffer = "";
        var started = Date.now();

        // 等待计时：让用户看到已过了多久，避免以为卡死
        var ticker = setInterval(function () {
            var sec = Math.round((Date.now() - started) / 1000);
            setStatus(sec + " 秒，正在等待模型响应…");
        }, 1000);
        setStatus("正在连接模型…");

        function finish() {
            clearInterval(ticker);
            setStatus("");
            $send.prop("disabled", false);
            $body.scrollTop($body[0].scrollHeight);
        }

        function render(text) {
            buffer += text;
            $text.text(buffer);
            $body.scrollTop($body[0].scrollHeight);
        }

        function fallbackToPlain() {
            // 流式不可用时回退普通接口，保证功能不丢
            $.ajax({
                url: "/ai/chat/message/",
                type: "post",
                data: {message: message},
                dataType: "json",
                success: function (res) {
                    if (res.status) {
                        render(res.answer);
                    } else {
                        render(res.msg);
                    }
                },
                error: function () {
                    render("网络异常，请稍后再试");
                },
                complete: finish
            });
        }

        if (!window.fetch || !window.TextDecoder) {
            fallbackToPlain();
            return;
        }

        fetch("/ai/chat/stream/", {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
            body: "message=" + encodeURIComponent(message)
        }).then(function (resp) {
            if (!resp.ok || !resp.body) {
                throw new Error("stream unavailable");
            }
            var reader = resp.body.getReader();
            var decoder = new TextDecoder("utf-8");
            var pending = "";

            function pump() {
                return reader.read().then(function (result) {
                    if (result.done) {
                        if (!buffer) fallbackToPlain();
                        return;
                    }
                    pending += decoder.decode(result.value, {stream: true});
                    // 按空行切分 SSE 事件
                    var blocks = pending.split("\n\n");
                    pending = blocks.pop();
                    blocks.forEach(function (block) {
                        var line = block.trim();
                        if (line.indexOf("data:") !== 0) {
                            return;
                        }
                        line = line.slice(5).trim();
                        if (line === "[DONE]") return;
                        try {
                            var obj = JSON.parse(line);
                            if (obj.t) render(obj.t);
                        } catch (e) {
                            // 忽略半包
                        }
                    });
                    return pump();
                });
            }
            return pump();
        }).then(finish).catch(function () {
            fallbackToPlain();
        });
    }

    $send.on("click", send);
    // Enter 发送，Shift+Enter 换行
    $input.on("keydown", function (e) {
        if (e.keyCode === 13 && !e.shiftKey) {
            e.preventDefault();
            send();
        }
    });

    // 清空对话
    $("#aiFloatClearBtn").on("click", function () {
        $.post("/ai/chat/clear/", function (res) {
            if (res.status) {
                $body.find(".ai-float-msg").remove();
                $body.append('<div class="ai-float-empty">对话已清空</div>');
            }
        });
    });

    // 设置面板开关
    $("#aiFloatSettingBtn").on("click", function () {
        $setting.toggle();
        $keyMsg.text("");
    });

    // 保存密钥
    $("#aiFloatKeySave").on("click", function () {
        var apiKey = $.trim($keyInput.val());
        $keyMsg.text("");
        if (!apiKey) {
            $keyMsg.text("请输入密钥");
            return;
        }
        $.post("/ai/chat/key/save/", {api_key: apiKey}, function (res) {
            if (res.status) {
                $keyMsg.removeClass("text-danger").addClass("text-success").text(res.msg);
                $keyInput.val("");
            } else {
                $keyMsg.text(res.msg);
            }
        });
    });

    // 清除临时密钥
    $("#aiFloatKeyRemove").on("click", function () {
        $.post("/ai/chat/key/clear/", function (res) {
            if (res.status) {
                $keyMsg.removeClass("text-success").addClass("text-danger").text(res.msg);
            }
        });
    });

    // 初始化密钥状态提示
    $.get("/ai/chat/key/status/", function (res) {
        if (res.status && !res.has_key) {
            setStatus("未配置密钥，点击右上角 ⚙ 填写");
        }
    });
});
