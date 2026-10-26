/* 日历弹窗组件：点击「入职时间」输入框弹出，选择日期后回填 */
(function ($) {
    var WEEK = ['一', '二', '三', '四', '五', '六', '日'];

    function pad(n) {
        return n < 10 ? '0' + n : '' + n;
    }

    // 判断某日期是否早于今天（早于今天则禁选）
    function isBeforeToday(y, m, d) {
        var today = new Date();
        today.setHours(0, 0, 0, 0);
        return new Date(y, m - 1, d) < today;
    }

    function dayCls(y, m, d) {
        var cls = 'cal-day';
        if (isBeforeToday(y, m, d)) {
            cls += ' cal-disabled';
        }
        return cls;
    }

    // 一次性创建弹窗
    var $pop = $('<div class="calendar-popup"></div>')
        .append('<div class="cal-header"><button type="button" class="cal-prev">&laquo;</button>' +
            '<span class="cal-title"></span>' +
            '<button type="button" class="cal-next">&raquo;</button></div>')
        .append('<div class="cal-week">' + WEEK.map(function (w) {
            return '<span>' + w + '</span>';
        }).join('') + '</div>')
        .append('<div class="cal-grid"></div>')
        .appendTo('body');

    var state = { input: null, year: null, month: null, selected: null };

    function render() {
        var y = state.year, m = state.month;
        var first = new Date(y, m - 1, 1);
        var offset = (first.getDay() + 6) % 7;          // 周一作为第一列
        var days = new Date(y, m, 0).getDate();         // 本月天数
        var prevDays = new Date(y, m - 1, 0).getDate(); // 上月天数
        var py = m === 1 ? y - 1 : y, pm = m === 1 ? 12 : m - 1;
        var ny = m === 12 ? y + 1 : y, nm = m === 12 ? 1 : m + 1;
        var today = new Date();
        var html = '';

        // 上个月补位
        for (var i = offset - 1; i >= 0; i--) {
            var pd = prevDays - i;
            html += '<span class="' + dayCls(py, pm, pd) + ' cal-other" data-y="' + py + '" data-m="' + pm + '" data-d="' + pd + '">' + pd + '</span>';
        }
        // 本月
        for (var j = 1; j <= days; j++) {
            var cls = dayCls(y, m, j);
            if (today.getFullYear() === y && today.getMonth() + 1 === m && today.getDate() === j) {
                cls += ' cal-today';
            }
            if (state.selected && state.selected.y === y && state.selected.m === m && state.selected.d === j) {
                cls += ' cal-selected';
            }
            html += '<span class="' + cls + '" data-y="' + y + '" data-m="' + m + '" data-d="' + j + '">' + j + '</span>';
        }
        // 下个月补足 42 格
        var count = offset + days;
        var k = 1;
        while (count < 42) {
            html += '<span class="' + dayCls(ny, nm, k) + ' cal-other" data-y="' + ny + '" data-m="' + nm + '" data-d="' + k + '">' + k + '</span>';
            k++;
            count++;
        }

        $pop.find('.cal-title').text(y + '年' + m + '月');
        $pop.find('.cal-grid').html(html);
    }

    function open($input) {
        state.input = $input;
        var val = $input.val().trim();
        var m = val.match(/(\d{4})[-/](\d{1,2})[-/](\d{1,2})/);
        if (m) {
            state.year = parseInt(m[1], 10);
            state.month = parseInt(m[2], 10);
            state.selected = { y: state.year, m: state.month, d: parseInt(m[3], 10) };
        } else {
            var now = new Date();
            state.year = now.getFullYear();
            state.month = now.getMonth() + 1;
            state.selected = null;
        }
        render();

        // 定位到输入框下方（靠右溢出时左移）
        var pos = $input.offset();
        var left = pos.left;
        if (left + $pop.outerWidth() > $(window).width()) {
            left = Math.max(0, $(window).width() - $pop.outerWidth());
        }
        $pop.css({ left: left, top: pos.top + $input.outerHeight() + 4 }).addClass('open');
    }

    function close() {
        $pop.removeClass('open');
    }

    // 聚焦输入框时弹出
    $(document).on('focus', 'input[name="create_time"]', function () {
        open($(this));
    });

    // 点击弹窗外侧关闭
    $(document).on('click', function (e) {
        if ($pop[0].contains(e.target)) {
            return;
        }
        if ($(e.target).is('input[name="create_time"]')) {
            return;
        }
        close();
    });

    // 翻月
    $pop.on('click', '.cal-prev', function () {
        state.month -= 1;
        if (state.month < 1) { state.month = 12; state.year -= 1; }
        state.selected = null;
        render();
    }).on('click', '.cal-next', function () {
        state.month += 1;
        if (state.month > 12) { state.month = 1; state.year += 1; }
        state.selected = null;
        render();
    });

    // 选日期（禁选的过去日期不生效）
    $pop.on('click', '.cal-day', function () {
        if ($(this).hasClass('cal-disabled')) {
            return;
        }
        var y = parseInt($(this).data('y'), 10);
        var m = parseInt($(this).data('m'), 10);
        var d = parseInt($(this).data('d'), 10);
        state.selected = { y: y, m: m, d: d };
        $(state.input).val(y + '-' + pad(m) + '-' + pad(d));
        close();
    });
})(jQuery);
