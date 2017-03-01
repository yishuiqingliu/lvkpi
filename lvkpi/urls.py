# -*- coding: UTF-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
import autocomplete_light

admin.autodiscover()


from lvkpi import settings

admin.autodiscover()
dajaxice_autodiscover()
autocomplete_light.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'lvkpi.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT,}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT,}),
    
    url(r'^statistics/',include('Statistics.urls')),
)

urlpatterns += patterns('kpi.views',
    (r'^$', 'staff_detail'),
    # 部门管理
    (r'^department_manage/(?P<did>\d+)/$', 'department_manage'),
    (r'^department_detail/(?P<did>\d+)/$', 'department_detail'),
    (r'^department_add/$', 'department_add'),
    (r'^department_add/(?P<pid>\d+)/$', 'department_add'),
    (r'^position_add/(?P<did>\d+)/$', 'position_add'),
    (r'^department_edit/(?P<did>\d+)/$', 'department_edit'),

    # 员工管理
    (r'^staff_manage/(?P<did>\d+)/$', 'staff_manage'),
    (r'^staff_detail/(?P<sid>\d+)/$', 'staff_detail'),
    (r'^staff_add/(?P<did>\d+)/$', 'staff_add'),
    (r'^staff_add/$', 'staff_add'),
    (r'^staff_edit/(?P<sid>\d+)/$', 'staff_edit'),

    # 贡献变动记录
    (r'^hand_record_add/(?P<sid>\d+)/$', 'hand_record_add'),
    (r'^hand_record_complete/(?P<hrid>\d+)/$', 'hand_record_complete'),
    (r'^hand_record_detail/(?P<hrid>\d+)/$', 'hand_record_detail'),

    # 默认页设置
    (r'^set_default_url/$', 'set_default_url'),
    (r'^turn_default_url/$', 'turn_default_url'),

    # 测试
    (r'^test/$', 'test'),
)

#用户登录、退出、修改用户信息、修改密码
urlpatterns += patterns('SSO.views',
    (r'^login/$', 'login', {'template_name':'registration/login.html'}),
    (r'^logout/$', 'logout', {'template_name':'registration/logout.html'}),
    (r'^account_setting/$','account_setting'),
    (r'^change_password/$', 'change_password'),
)