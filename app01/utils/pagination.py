import copy

from django.utils.safestring import mark_safe
from django.utils.html import escape


class Pagination:
    """分页组件：切片数据 + 生成页码 HTML（自动保留 URL 中除 page 外的全部查询参数）

    用法：
        pager = Pagination(request, queryset, page_size=10)
        数据：pager.page_queryset
        页码：pager.html()（已 mark_safe，可直接输出）
    """

    def __init__(self, request, queryset, page_size=10, page_param="page", plus=5):
        """
        :param request: 请求对象
        :param queryset: 符合条件的数据（根据这个数据给他进行分页处理）
        :param page_size: 每页显示多少条数据
        :param page_param: 在URL中传递的获取分页的参数，例如：/pretty/list/?page=12
        :param plus: 显示当前页的前/后几页（页码）
        """
        # 深拷贝 GET 参数，翻页/跳转时自动带上 keyword 等其它查询条件
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict = query_dict
        self.page_param = page_param

        page = request.GET.get(page_param, "1")
        page = int(page) if page.isdecimal() else 1

        self.page_size = page_size
        self.start = (page - 1) * page_size
        self.end = page * page_size
        self.page_queryset = queryset[self.start:self.end]

        # 总页数
        total_count = queryset.count()
        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1
        if total_page_count < 1:
            total_page_count = 1
        self.total_page_count = total_page_count

        # 页码越界修正
        self.page = min(max(page, 1), total_page_count)
        self.plus = plus

    def _url(self, page):
        """生成带当前其它查询参数（如 keyword）的链接"""
        self.query_dict.setlist(self.page_param, [page])
        return "?{}".format(self.query_dict.urlencode())

    def _hidden_inputs(self):
        """除 page 外的其它查询参数做成隐藏输入，保证跳转表单不丢失（转义防 XSS）"""
        parts = []
        for key, values in self.query_dict.lists():
            if key == self.page_param:
                continue
            for value in values:
                parts.append('<input type="hidden" name="{}" value="{}">'.format(escape(key), escape(value)))
        return "".join(parts)

    def html(self):
        """生成 Bootstrap 风格分页 HTML：首页/上一页/页码/下一页/尾页 + 页码跳转"""
        if self.total_page_count <= 2 * self.plus + 1:
            # 数据少，不足 11 页：全部展示
            start_page, end_page = 1, self.total_page_count
        else:
            if self.page <= self.plus:
                # 当前页靠前（小极值）
                start_page, end_page = 1, 2 * self.plus + 1
            elif self.page + self.plus > self.total_page_count:
                # 当前页靠后（大极值）
                start_page, end_page = self.total_page_count - 2 * self.plus, self.total_page_count
            else:
                start_page, end_page = self.page - self.plus, self.page + self.plus

        page_str_list = []

        # 首页
        page_str_list.append('<li><a href="{}">首页</a></li>'.format(self._url(1)))

        # 上一页
        prev = self.page - 1 if self.page > 1 else 1
        page_str_list.append('<li><a href="{}">上一页</a></li>'.format(self._url(prev)))

        # 页码
        for i in range(start_page, end_page + 1):
            if i == self.page:
                page_str_list.append('<li class="active"><a href="{}">{}</a></li>'.format(self._url(i), i))
            else:
                page_str_list.append('<li><a href="{}">{}</a></li>'.format(self._url(i), i))

        # 下一页
        nxt = self.page + 1 if self.page < self.total_page_count else self.total_page_count
        page_str_list.append('<li><a href="{}">下一页</a></li>'.format(self._url(nxt)))

        # 尾页
        page_str_list.append('<li><a href="{}">尾页</a></li>'.format(self._url(self.total_page_count)))

        # 页码跳转
        jump_form = """
            <li>
                <form style="float: left;margin-left: -1px" method="get">
                    {hidden}
                    <input name="{param}"
                           style="position: relative;float:left;display: inline-block;width: 80px;border-radius: 0;"
                           type="text" class="form-control" placeholder="页码">
                    <button style="border-radius: 0" class="btn btn-default" type="submit">跳转</button>
                </form>
            </li>
            """.format(hidden=self._hidden_inputs(), param=self.page_param)
        page_str_list.append(jump_form)

        return mark_safe('<ul class="pagination">{}</ul>'.format("".join(page_str_list)))
