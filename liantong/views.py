import os.path
from datetime import datetime
from io import BytesIO

import openpyxl
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponse
from django import forms

from day58.settings import MEDIA_ROOT
from liantong import models
from liantong.utils.pagination import Pagination
from liantong.utils.encrypt import md5
from liantong.utils.code import check_code


class BootStrip(forms.Form):
    bootstrap_exclude_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.bootstrap_exclude_fields:
                continue
            if field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label
            else:
                field.widget.attrs = {
                    'class': 'form-control',
                    'placeholder': field.label}


class ModelFormAttrs(BootStrip, forms.ModelForm):
    pass


class FormAttrs(BootStrip, forms.Form):
    pass


# ******************部门相关函数区域******************
def depart_list(request):
    queryset = models.Department.objects.all()
    context = {'queryset': queryset}
    return render(request, 'list_depart.html', context)


def depart_add(request):
    if request.method == 'GET':
        return render(request, 'depart_add.html')
    else:
        title = request.POST.get('title')
        models.Department.objects.create(title=title)
        return redirect('/depart/list/')


def depart_delete(request):
    nid = request.GET.get('nid')
    models.Department.objects.filter(id=nid).delete()
    return redirect('/depart/list/')


def depart_edit(request, nid):
    row_object = models.Department.objects.filter(id=nid)
    if request.method == 'GET':
        context = {'row_object': row_object.first()}
        return render(request, 'depart_edit.html', context)
    else:
        title = request.POST.get('title')
        row_object.update(title=title)
        return redirect('/depart/list/')


def depart_excel(request):
    # 拿到excel文件
    file_object = request.FILES.get('excel')
    # 打开excel并处理
    wb = openpyxl.load_workbook(file_object)
    sheet = wb.worksheets[0]
    for row in sheet.iter_rows():
        text = row[0].value
        exists = models.Department.objects.filter(title=text).exists()
        if not exists:
            models.Department.objects.create(title=text)
    return redirect('/depart/list/')


# ******************用户相关函数区域******************
def user_list(request):
    queryset = models.User.objects.all()
    context = {'queryset': queryset}
    return render(request, 'list_user.html', context)


"""
# 用原始方法创建很多input框，并接收数据保存到数据库，麻烦且问题多
def user_add(request):
    if request.method == 'GET':
        gender = models.User.gender_choices
        depart = models.Department.objects.all()
        context = {
            'gender': gender,
            'depart': depart,
        }
        return render(request, '原始方法_add_edit.html', context)
    else:
        name = request.POST.get('name')
        password = request.POST.get('pwd')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        account = request.POST.get('account')
        c_time = request.POST.get('c_time')
        depart = request.POST.get('depart')
        models.User.objects.create(
            name=name, password=password,
            age=age, gender=gender,
            account=account, create_time=c_time,
            depart_id=depart)
        return redirect('/user/list/')
"""


class UserModelForm(ModelFormAttrs):
    class Meta:
        model = models.User
        fields = '__all__'


def user_add(request):
    if request.method == 'GET':
        UserForm = UserModelForm()
        context = {'Form': UserForm, 'title': '新增用户'}
        return render(request, 'user_add_edit.html', context)
    UserForm = UserModelForm(data=request.POST)
    if UserForm.is_valid():
        UserForm.save()
        return redirect('/user/list/')
    context = {'Form': UserForm, 'title': '新增用户'}
    return render(request, 'user_add_edit.html', context)


def user_edit(request, nid):
    row_object = models.User.objects.filter(id=nid).first()
    # get
    if request.method == 'GET':
        UserForm = UserModelForm(instance=row_object)
        context = {'Form': UserForm, 'title': '编辑用户'}
        return render(request, 'user_add_edit.html', context)
    # post
    UserForm = UserModelForm(data=request.POST, instance=row_object)
    if UserForm.is_valid():
        UserForm.save()
        return redirect('/user/list/')
    context = {'Form': UserForm, 'title': '编辑用户'}
    return render(request, 'user_add_edit.html', context)


def user_delete(request, nid):
    models.User.objects.filter(id=nid).delete()
    return redirect('/user/list/')


# ******************靓号管理相关函数区域******************
def mobile_list(request):
    data_dict = {}
    num = request.GET.get('q', '')
    if num:
        data_dict['mobile__contains'] = num
    queryset = models.Mobile.objects.filter(**data_dict)
    page_object = Pagination(request, queryset)
    context = {
        'page_string': page_object.html(),
        'queryset': page_object.page_queryset,
        'search_num': num
    }
    return render(request, 'list_mobile.html', context)


class MobileAddModelForm(ModelFormAttrs):
    class Meta:
        model = models.Mobile
        fields = '__all__'

    def clean_mobile(self):
        value = self.cleaned_data.get('mobile')
        exist = models.Mobile.objects.filter(mobile=value).exists()
        if exist:
            raise ValidationError('手机号已存在')
        else:
            return value


def mobile_add(request):
    # GET的处理，展示输入框
    if request.method == 'GET':
        MobileForm = MobileAddModelForm()
        context = {'Form': MobileForm, 'title': '新增靓号'}
        return render(request, 'common_add_edit.html', context)
    # POST的处理，判断后保存，或展示错误
    MobileForm = MobileAddModelForm(request.POST)
    if MobileForm.is_valid():
        MobileForm.save()
        return redirect('/mobile/list/')
    context = {'Form': MobileForm, 'title': '新增靓号'}
    return render(request, 'common_add_edit.html', context)


class MobileEditModelForm(ModelFormAttrs):
    class Meta:
        model = models.Mobile
        fields = '__all__'

    def clean_mobile(self):
        num = self.instance.pk
        value = self.cleaned_data.get('mobile')
        exist = models.Mobile.objects.exclude(id=num).filter(mobile=value).exists()
        if exist:
            raise ValidationError('手机号已存在')
        else:
            return value


def mobile_edit(request, nid):
    row_object = models.Mobile.objects.filter(id=nid).first()
    if request.method == 'GET':
        MobileForm = MobileEditModelForm(instance=row_object)
        context = {'Form': MobileForm, 'title': '编辑靓号'}
        return render(request, 'common_add_edit.html', context)
    MobileForm = MobileEditModelForm(data=request.POST, instance=row_object)
    if MobileForm.is_valid():
        MobileForm.save()
        return redirect('/mobile/list/')
    context = {'Form': MobileForm, 'title': '编辑靓号'}
    return render(request, 'common_add_edit.html', context)


def mobile_delete(request, nid):
    models.Mobile.objects.filter(id=nid).delete()
    return redirect('/mobile/list/')


# ******************管理员管理相关函数区域******************
def admin_list(request):
    print(request.session['info'])
    data_dict = {}
    search_str = request.GET.get('q', '')
    if search_str:
        data_dict['name__contains'] = search_str
    queryset = models.Admin.objects.filter(**data_dict)
    page_object = Pagination(request, queryset)
    context = {
        'page_string': page_object.html(),
        'queryset': page_object.page_queryset,
        'search_q': search_str}
    return render(request, 'list_admin.html', context)


class AdminModelForm(ModelFormAttrs):
    confirm_pas = forms.CharField(
        label='确认密码', max_length=32,
        widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = models.Admin
        fields = ['name', 'password', 'confirm_pas']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    def clean_password(self):
        pas = self.cleaned_data['password']
        return md5(pas)

    def clean_confirm_pas(self):
        c_pas = self.cleaned_data['confirm_pas']
        pas = self.cleaned_data['password']
        if md5(c_pas) != pas:
            raise ValidationError('密码不一致')
        return c_pas


def admin_add(request):
    if request.method == 'GET':
        adminForm = AdminModelForm()
        context = {'Form': adminForm, 'title': '新增管理员'}
        return render(request, 'common_add_edit.html', context)
    adminForm = AdminModelForm(data=request.POST)
    if adminForm.is_valid():
        adminForm.save()
        return redirect('/admin/list/')
    context = {'Form': adminForm, 'title': '新增管理员'}
    return render(request, 'common_add_edit.html', context)


def admin_edit(request, nid):
    one_query = models.Admin.objects.filter(id=nid).first()
    if not one_query:
        error_msg = {'e_msg': '数据不存在'}
        return render(request, 'errors.html', error_msg)
        # return redirect('/admin/list/')
    if request.method == 'GET':
        adminForm = AdminModelForm(instance=one_query)
        context = {'Form': adminForm, 'title': '编辑管理员'}
        return render(request, 'common_add_edit.html', context)
    adminForm = AdminModelForm(data=request.POST, instance=one_query)
    if adminForm.is_valid():
        adminForm.save()
        return redirect('/admin/list/')
    context = {'Form': adminForm, 'title': '编辑管理员'}
    return render(request, 'common_add_edit.html', context)


def admin_delete(request, nid):
    models.Admin.objects.filter(id=nid).delete()
    return redirect('/admin/list/')


class ResetModelForm(ModelFormAttrs):
    confirm_pas = forms.CharField(
        label='确认密码', max_length=32,
        widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = models.Admin
        fields = ['password', 'confirm_pas']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    def clean_password(self):
        pas = self.cleaned_data.get('password')
        md5pas = md5(pas)
        exist = models.Admin.objects.filter(id=self.instance.pk, password=md5pas).exists()
        if exist:
            raise ValidationError('密码不能跟之前相同')
        return md5pas

    def clean_confirm_pas(self):
        pas = self.cleaned_data.get('password')
        c_pas = self.cleaned_data.get('confirm_pas')
        if md5(c_pas) != pas:
            raise ValidationError('密码不一致')
        return c_pas


def admin_reset(request, nid):
    row_object = models.Admin.objects.filter(id=nid).first()
    title = '重置密码---{}'.format(row_object.name)
    if not row_object:
        error_msg = {'e_msg': '数据不存在'}
        return render(request, 'errors.html', error_msg)
    if request.method == 'GET':
        ResetForm = ResetModelForm()
        context = {'title': title, 'Form': ResetForm}
        return render(request, 'common_add_edit.html', context)
    ResetForm = ResetModelForm(data=request.POST, instance=row_object)
    if ResetForm.is_valid():
        ResetForm.save()
        return redirect('/admin/list/')
    context = {'title': title, 'Form': ResetForm}
    return render(request, 'common_add_edit.html', context)


# ******************登录页面相关函数区域******************

class LoginForm(forms.Form):
    name = forms.CharField(label='姓名', max_length=10, widget=forms.TextInput)
    password = forms.CharField(label='密码', max_length=32,
                               widget=forms.PasswordInput(render_value=True))
    code = forms.CharField(label='验证码', max_length=10, widget=forms.TextInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {
                'class': 'form-control',
                'placeholder': field.label}

    def clean_password(self):
        pas = self.cleaned_data.get('password')
        return md5(pas)


def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    # 这里POST传入3个值name,password,code
    form = LoginForm(request.POST)
    if form.is_valid():
        # 先判断验证码是不是对的
        s_code = request.session.get('img_code')
        f_code = form.cleaned_data.pop('code')
        # 如果不对，就直接返回login页面，对就继续执行
        if f_code != s_code:
            form.add_error('code', '验证码输入错误')
            return render(request, 'login.html', {'form': form})
        user_object = models.Admin.objects.filter(**form.cleaned_data).first()
        # 如果能在数据库中找到数据就设置session，否则就设置错误，还返回login页面
        if user_object:
            request.session['info'] = {'id': user_object.id, 'user': user_object.name}
            request.session.set_expiry(60 * 60)
            return redirect('/admin/list/')
        form.add_error('name', '输入的用户名或密码错误')
    return render(request, 'login.html', {'form': form})


def logout(request):
    request.session.clear()  # 清除session，跳转回登录页面
    return redirect('/login/')


def img(request):
    # 利用code生成图片和字母
    img1, code_str = check_code()
    # 把验证码保存到session中，以便后续调用
    # 这里把session的时间设成60s，提升验证图片的安全度
    request.session['img_code'] = code_str
    request.session.set_expiry(60)
    # 利用BytesIO生成内存中图片流
    stream = BytesIO()
    img1.save(stream, 'png')
    print(code_str, 'code_str')
    return HttpResponse(stream.getvalue())


# ******************订单管理相关函数区域******************
class OrderModelForm(ModelFormAttrs):
    class Meta:
        model = models.Order
        exclude = ['oid', 'admin']


def order_list(request):
    form = OrderModelForm()
    # 拿数据,并分页展示
    queryset = models.Order.objects.all().order_by('-id')
    page_object = Pagination(request, queryset)
    # 3. 回传到html
    context = {'page_string': page_object.html(),  # 生成的页码
               'queryset': page_object.page_queryset,  # 分完页的数据
               'Form': form
               }
    return render(request, 'list_order.html', context)


def order_add(request):
    uid = request.GET.get('uid')
    # 如果uid等于new，就执行新建保存
    if uid == 'new':
        form = OrderModelForm(request.POST)
        if form.is_valid():
            form.instance.oid = datetime.now().strftime('%Y%m%d%H%M%S') + '001'
            form.instance.admin_id = request.session['info']['id']
            form.save()
            return JsonResponse({'status': True})
        return JsonResponse({'status': False, 'error': form.errors})
    # 如果uid不等于new，就执行编辑保存
    else:
        query = models.Order.objects.filter(id=uid).first()
        # 增加了数据库中是否有数据的校验
        if not query:
            return JsonResponse({'status': False, 'tips': '数据库中没有数据'})
        # 有数据往下执行
        form = OrderModelForm(request.POST, instance=query)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': True})
        return JsonResponse({'status': False, 'error': form.errors})


def order_delete(request):
    d_id = request.GET.get('d_id')
    exists = models.Order.objects.filter(id=d_id).exists()
    if not exists:
        return JsonResponse({'status': False, 'error': '数据库中没有，删除失败'})
    models.Order.objects.filter(id=d_id).delete()
    return JsonResponse({'status': True})


def order_detail(request):
    e_id = request.GET.get('eid')
    row_object = models.Order.objects.filter(id=e_id).values('title', 'price', 'status').first()
    if not row_object:
        return JsonResponse({'status': False, 'error': '数据库中没有数据'})
    # 数据库中有数据，就把数据转换成字典回传，因为json不能解析object类型。
    context = {
        'status': True,
        'data': row_object}
    return JsonResponse(context)


# ******************文件上传相关函数区域******************
def file_detail(request):
    if request.method == 'GET':
        return render(request, 'upload_file.html')
    file_object = request.FILES.get('文件')
    with open(file_object.name, 'wb') as f:
        for chunk in file_object.chunks():
            f.write(chunk)
    return redirect('/file/detail/')


class FormEdit(FormAttrs):
    name = forms.CharField(label='姓名')
    age = forms.IntegerField(label='年龄')
    img = forms.FileField(label='头像')
    bootstrap_exclude_fields = ['img']


def form_edit(request):
    if request.method == 'GET':
        form = FormEdit()
        context = {'Form': form, 'title': 'Form编辑'}
        return render(request, 'common_add_edit.html', context)
    form = FormEdit(request.POST, request.FILES)
    if form.is_valid():
        img_data = form.cleaned_data.get('img')
        file_path = os.path.join('media', img_data.name)
        with open(file_path, 'wb') as f:
            for chunk in img_data.chunks():
                f.write(chunk)
        models.Boss.objects.create(
            name=form.cleaned_data.get('name'),
            age=form.cleaned_data.get('age'),
            img=file_path)
        return HttpResponse('.....')


class ModelFormList(ModelFormAttrs):
    bootstrap_exclude_fields = ['logo']

    class Meta:
        model = models.City
        fields = '__all__'


def modelform_list(request):
    if request.method == 'GET':
        queryset = models.City.objects.all()
        form = ModelFormList()
        context = {
            'title': '城市编辑',
            'Form': form,
            'queryset':queryset}
        return render(request, 'list_modelform.html', context)
    form = ModelFormList(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return redirect('/modelform/list/')
    context = {'Form': form,'title':'城市编辑'}
    return render(request, 'list_modelform.html', context)
