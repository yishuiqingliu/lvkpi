#coding:utf-8
from Utils.http import json_response
from dateutil import tz

import calendar
import datetime,time

from kpi.models import *
from Statistics.functions import *

def department_point_stat(request):
    cds = request.GET
    unit = cds.get('timeLevel','day')
    begin_time = cds.get('begin_time')
    department_id = cds.get('department','')
    if department_id:
        department=Department.objects.get(id=department_id)
    else:
        department=request.user.account.staff.department
    if begin_time:
        begin_time = datetime.date.fromtimestamp(int(begin_time))
    end_time = cds.get('end_time')    
    if end_time:
        end_time = datetime.date.fromtimestamp(int(end_time))
    x_data,y_data,y_data_branchs,y_titles= split_department_point_by_time(unit=unit,begin_time=begin_time,end_time=end_time,department=department)
    option=department_point_option(xdata=x_data,ydata=y_data,ydata_branchs=y_data_branchs,ytitles=y_titles)
    return json_response(option)

def staff_point_stat(request):
    cds = request.GET
    unit = cds.get('timeLevel','day')
    begin_time = cds.get('begin_time')
    department_id = cds.get('department','')
    if department_id:
        department=Department.objects.get(id=department_id)
    else:
        department=request.user.account.staff.department
    if begin_time:
        begin_time = datetime.date.fromtimestamp(int(begin_time))
    end_time = cds.get('end_time')    
    if end_time:
        end_time = datetime.date.fromtimestamp(int(end_time))
    x_data,y_data,y_data_branchs,y_titles= split_staff_point_by_time(unit=unit,begin_time=begin_time,end_time=end_time,department=department)
    option=staff_point_option(xdata=x_data,ydata=y_data,ydata_branchs=y_data_branchs,ytitles=y_titles)
    return json_response(option)
