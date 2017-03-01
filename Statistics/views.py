#coding:utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime,time
from django.core.cache import cache
import urllib

from kpi.models import *
from Statistics.functions import *


def statistic_department_point(request):
    department = request.user.account.staff.department
    context={
         'departments':department.children_with_self
         }
    return render_to_response('statistics/statistic_department_point.html',context,context_instance=RequestContext(request))

def statistic_staff_point(request):
    department = request.user.account.staff.department
    context={
         'departments':department.children_with_self
         }
    return render_to_response('statistics/statistic_staff_point.html',context,context_instance=RequestContext(request))