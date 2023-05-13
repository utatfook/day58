from django.db import models


# Create your models here.
class Department(models.Model):
    """ 部门表 """
    title = models.CharField(verbose_name='部门', max_length=32)

    def __str__(self):
        return self.title


class User(models.Model):
    """员工表"""
    name = models.CharField(verbose_name='姓名', max_length=16)
    password = models.CharField(verbose_name='密码', max_length=8)
    age = models.IntegerField(verbose_name='年龄')
    gender_choices = ((1, '男'), (2, '女'))
    gender = models.SmallIntegerField(verbose_name='性别', choices=gender_choices)
    account = models.DecimalField(verbose_name='余额', max_digits=10, decimal_places=2, default=0)
    create_time = models.DateField(verbose_name='入职时间')
    depart = models.ForeignKey(verbose_name='部门', to='Department', to_field='id', on_delete=models.SET_NULL, null=True,
                               blank=True)


class Mobile(models.Model):
    """靓号表"""
    mobile = models.CharField(verbose_name='手机号', max_length=11)
    price = models.DecimalField(verbose_name='价格', max_digits=10, decimal_places=2, default=0)
    level_choices = ((1, '优秀'), (2, '良好'), (3, '一般'))
    level = models.SmallIntegerField(verbose_name='等级', choices=level_choices, default=1)
    status_choices = ((1, '未占用'), (2, '已占用'))
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)


class Admin(models.Model):
    name = models.CharField(verbose_name='姓名', max_length=16)
    password = models.CharField(verbose_name='密码', max_length=32)

    def __str__(self):
        return self.name


class Order(models.Model):
    oid = models.CharField(verbose_name='订单号', max_length=32)
    title = models.CharField(verbose_name='名称', max_length=16)
    price = models.IntegerField(verbose_name='价格')
    status_choices = ((1, "已支付"), (2, "待支付"))
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)
    admin = models.ForeignKey(verbose_name='管理员', to='Admin', on_delete=models.CASCADE)


class Boss(models.Model):
    name = models.CharField(verbose_name='姓名', max_length=8)
    age = models.SmallIntegerField(verbose_name='年龄')
    img = models.CharField(verbose_name='头像', max_length=128)


class City(models.Model):
    city = models.CharField(verbose_name='城市', max_length=8)
    count = models.SmallIntegerField(verbose_name='人口')
    logo = models.FileField(verbose_name='头像', upload_to='city/', max_length=128)
