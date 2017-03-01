from django.conf.urls import patterns

urlpatterns = patterns('Statistics.views',
    (r'^department_point/$','statistic_department_point'),
    (r'^staff_point/$','statistic_staff_point'),
    )
    
urlpatterns += patterns('Statistics.echarts_api',
    (r'^department_point_api/$','department_point_stat'),
    (r'^staff_point_api/$','staff_point_stat'),
    )