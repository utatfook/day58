"""day58 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from liantong import views

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT},name='media'),

    path('depart/list/', views.depart_list),
    path('depart/add/', views.depart_add),
    path('depart/delete/', views.depart_delete),
    path('depart/<int:nid>/edit/', views.depart_edit),
    path('depart/excel/', views.depart_excel),

    path('user/list/', views.user_list),
    path('user/add/', views.user_add),
    path('user/<int:nid>/edit/', views.user_edit),
    path('user/<int:nid>/delete/', views.user_delete),

    path('mobile/list/', views.mobile_list),
    path('mobile/add/', views.mobile_add),
    path('mobile/<int:nid>/edit/', views.mobile_edit),
    path('mobile/<int:nid>/delete/', views.mobile_delete),

    path('admin/list/', views.admin_list),
    path('admin/add/', views.admin_add),
    path('admin/<int:nid>/edit/', views.admin_edit),
    path('admin/<int:nid>/delete/', views.admin_delete),
    path('admin/<int:nid>/reset/', views.admin_reset),

    path('login/', views.login),
    path('logout/', views.logout),

    path('code/img/',views.img),

    path('order/list/',views.order_list),
    path('order/add/',views.order_add),
    path('order/delete/',views.order_delete),
    path('order/detail/', views.order_detail),

    path('file/detail/', views.file_detail),
    path('form/edit/', views.form_edit),
    path('modelform/list/', views.modelform_list),
]