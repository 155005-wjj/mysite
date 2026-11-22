"""
分页组件

一次性把全部数据查出来既慢又占内存。分页做两件事：
1. 查询时只取当前页（QuerySet 切片会被翻译成 SQL 的 LIMIT/OFFSET）；
2. 页面上渲染页码链接。

用法：
    page_object = Pagination(request, queryset, page_size=10)
    page_object.page_queryset   # 当前页数据
    page_object.html()          # 页码 HTML
"""
from django.utils.safestring import mark_safe


class Pagination:
    """基于 QuerySet 切片的分页器"""

    def __init__(self, request, queryset, page_size=10, page_param="page", plus=5):
        """
        :param request: 请求对象，用于取当前页码并保留其他查询参数
        :param queryset: 待分页的数据集
        :param page_size: 每页条数
        :param page_param: 页码参数名
        :param plus: 当前页前后各显示几个页码
        """
        # 复制一份 GET 参数，翻页时保留原有的筛选条件
        query_dict = request.GET.copy()
        self.query_dict = query_dict
        self.page_param = page_param

        page = request.GET.get(page_param, "1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1

        self.page_size = page_size

        total_count = queryset.count()
        # 计算总页数（整除后有余数则进一页）
        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1
        self.total_page_count = total_page_count

        # 页码越界（如手工输入过大页码）时收敛到有效范围，避免出现空白页
        if total_page_count == 0:
            page = 1
        elif page < 1:
            page = 1
        elif page > total_page_count:
            page = total_page_count

        self.page = page
        self.plus = plus

        self.start = (page - 1) * page_size
        self.end = page * page_size
        self.page_queryset = queryset[self.start:self.end]

    def html(self):
        """生成 Bootstrap 分页条 HTML"""
        if self.total_page_count <= 0:
            return ""

        # 页码区间：总页数少时全显示，多时以当前页为中心取 2*plus+1 个
        if self.total_page_count <= 2 * self.plus + 1:
            start_page = 1
            end_page = self.total_page_count
        else:
            if self.page <= self.plus:
                start_page = 1
                end_page = 2 * self.plus + 1
            elif (self.page + self.plus) > self.total_page_count:
                start_page = self.total_page_count - 2 * self.plus
                end_page = self.total_page_count
            else:
                start_page = self.page - self.plus
                end_page = self.page + self.plus

        page_str_list = []

        # 首页
        self.query_dict.setlist(self.page_param, [1])
        page_str_list.append(
            '<li><a href="?{}">首页</a></li>'.format(self.query_dict.urlencode())
        )

        # 上一页（已在第一页时仍指向第一页）
        prev_page = self.page - 1 if self.page > 1 else 1
        self.query_dict.setlist(self.page_param, [prev_page])
        page_str_list.append(
            '<li><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode())
        )

        # 中间页码，当前页高亮
        for i in range(start_page, end_page + 1):
            self.query_dict.setlist(self.page_param, [i])
            if i == self.page:
                ele = '<li class="active"><a href="?{}">{}</a></li>'.format(
                    self.query_dict.urlencode(), i
                )
            else:
                ele = '<li><a href="?{}">{}</a></li>'.format(
                    self.query_dict.urlencode(), i
                )
            page_str_list.append(ele)

        # 下一页
        next_page = self.page + 1 if self.page < self.total_page_count else self.total_page_count
        self.query_dict.setlist(self.page_param, [next_page])
        page_str_list.append(
            '<li><a href="?{}">下一页</a></li>'.format(self.query_dict.urlencode())
        )

        # 尾页
        self.query_dict.setlist(self.page_param, [self.total_page_count])
        page_str_list.append(
            '<li><a href="?{}">尾页</a></li>'.format(self.query_dict.urlencode())
        )

        # 跳转框：直接输入页码
        search_string = """
            <li>
                <form style="float: left; margin-left: -1px;" method="get">
                    <input type="text" name="{param}" style="width: 80px; border:1px solid #ddd;
                           position:relative; padding: 6px 12px; float:left;"
                           placeholder="页码">
                    <button type="submit" class="btn btn-default">跳转</button>
                </form>
            </li>
        """.format(param=self.page_param)
        page_str_list.append(search_string)

        return mark_safe("".join(page_str_list))
