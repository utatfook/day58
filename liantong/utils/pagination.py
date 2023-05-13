from django.utils.safestring import mark_safe
import copy

"""
自定义的分页组件,以后如果要使用这个组件，需要做几件事

在视图函数中
    def XXXX_list(request):
        # 1. 根据自己的情况去筛选想要的数据
        queryset = models.PrettyNum.objects.filter(**fil_dic)
        # 2. 实例化分页对象
        page_object = Pagination(request, queryset)
        # 3. 回传到html
        context = {'page_string': page_object.html(),  # 生成的页码
                   'queryset': page_object.page_queryset,  # 分完页的数据
                   }
        return render(request, 'xxxxx.html', context)

在HTML页面中

        {% for obj in queryset %}
            {{ obj.XXX }}
        {% endfor %}
        
        <ul class="pagination">
            {{ page_string }}
        </ul>
"""


class Pagination(object):
    def __init__(self, request, queryset, page_param='page', page_size=10, plus=3):
        """
        :param request: 请求的对象
        :param queryset: 符合条件的数据（根据这个数据来分页)
        :param page_size: 每页显示多少条数据
        :param page_param: 在URL中传递的获取分页的参数，例如：/pretty/list/?page=12
        :param plus: 显示当前页的前后几页
        """
        self.page_size = page_size
        self.plus = plus
        page = request.GET.get(page_param, '1')
        # 这里判断page具体获得了哪个值
        if page.isdecimal():
            # 是数字就返回页码
            page = int(page)
        else:
            # 其余都返回1
            page = 1
        self.page = page

        # 深拷贝，并设置其可修改，方便后面拼接page和其他参数，组成url
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True  # 设置其可以修改
        self.query_dict = query_dict

        # 计算分页时，从哪里开始，哪里结束
        self.start = (self.page - 1) * page_size
        self.end = self.page * page_size
        self.page_queryset = queryset[self.start:self.end]
        # 1.获取总条数，总页数
        total_count = queryset.count()  # 统计选择数
        total_page, div = divmod(total_count, page_size)
        if div:
            total_page += 1
        self.total_page = total_page

    def html(self):
        # 定义一个生成HTML的方法，用来生成页码导航  # 添加分页导航按钮
        # 2.获取显示哪几页的标签,self.plus是前后标签数
        # 2.1 判断如果页码特别少,开始和结束是多少
        if self.total_page < 2 * self.plus + 1:
            start_page = 1
            end_page = self.total_page
        # 2.2 依次判断，如果小到接近1，或大到接近total 开始和结束是多少
        else:
            if self.page <= self.plus:
                start_page = 1
                end_page = 2 * self.plus + 1
            else:
                if self.page >= self.total_page - self.plus:
                    start_page = self.total_page - 2 * self.plus
                    end_page = self.total_page
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus

        page_str_list = []
        # 首页
        # 列表新增加一项page
        self.query_dict.setlist('page', [1])
        # urlencode组合成含多参数的url
        First_ele = '<li><a href="?{}">首页</a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(First_ele)

        # 上一页的页码
        if self.page <= 1:
            Pre_page = 1
        else:
            Pre_page = self.page - 1
        self.query_dict.setlist('page', [Pre_page])
        pre_ele = '<li><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(pre_ele)

        # 中间页的页码
        for i in range(start_page, end_page + 1):
            self.query_dict.setlist('page', [i])
            if i == self.page:
                ele = '<li class ="active"><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            else:
                ele = '<li><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            page_str_list.append(ele)

        # 下一页的页码
        if self.page >= self.total_page:
            Next_page = self.total_page
        else:
            Next_page = self.page + 1
        self.query_dict.setlist('page', [Next_page])
        Next_ele = '<li><a href="?{}">下一页</a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(Next_ele)

        # 尾页
        self.query_dict.setlist('page', [self.total_page])
        Last_ele = '<li><a href="?{}">尾页</a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(Last_ele)

        # 跳转页
        Search_ele = """
            <li>
                <form method="get" style="float: left; margin-left: -1px">
                    <input style="position: relative; float: left; display: inline-block;width: 80px"
                           type="text" name="page" class="form-control" placeholder="页码">
                    <button type="submit" class="btn btn-default">跳转</button>
                </form>
            </li>
            """
        page_str_list.append(Search_ele)

        # 列表统一join成字符串
        page_string = mark_safe(' '.join(page_str_list))
        return page_string
