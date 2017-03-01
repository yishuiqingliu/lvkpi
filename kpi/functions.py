# coding=utf-8
from functools import wraps
from django.http.response import HttpResponse
import datetime

from kpi.models import *

def leader_need():
    def decorator(func):
        @wraps(func)
        def returned_wrapper(request,*args, **kwargs):
            can_pass=True
            remark=''
            if kwargs.has_key('sid'):
                sid=kwargs.get('sid')
                if sid:
                    staff=Staff.objects.get(id=sid)
                    if not staff.department in request.user.account.staff.department.children_with_self:
                        can_pass=False
                        remark=u'并非自己下属部门员工'
            if kwargs.has_key('did'):
                did=kwargs.get('did')
                if did:
                    department=Department.objects.get(id=did)
                    if not department in request.user.account.staff.department.children_with_self:
                        can_pass=False
                        remark=u'并非自己下属部门'
            if kwargs.has_key('pid'):
                pid=kwargs.get('pid')
                if pid:
                    department=Department.objects.get(id=pid)
                    if not department in request.user.account.staff.department.children_with_self:
                        can_pass=False
                        remark=u'并非自己下属部门'
            if kwargs.has_key('hrid'):
                hrid=kwargs.get('hrid')
                if hrid:
                    record=HandRecord.objects.get(id=hrid)
                    if not record.target.department in request.user.account.staff.department.children_with_self:
                        can_pass=False
                        remark=u'并非自己下属部门员工的权限记录'
            if can_pass:
                return func(request, *args, **kwargs)
            else:
                return HttpResponse(remark)
        return returned_wrapper
    return decorator

def NatureChangeCheck():
    departments=Department.objects.filter(level=2)
    today=datetime.date.today()
    if today.day==1:
        for department in departments:
            increase_months=department.departmentset.increase_type
            for staff in department.staffs:
                nature_records=staff.my_nature_records.all().order_by('-create_time')
                if nature_records.count()>0:
                    last_date=nature_records[0].create_time
                else:
                    last_date=datetime.date(staff.join_date.year,staff.join_date.month+1,1)
                if (today.month-last_date.month>=increase_months and today.day>=last_date.day) or today.month-last_date.month>increase_months:
                    increase=staff.staffset.increase
                    current_increst=(1+increase/100)**(float(increase_months)/12)
                    past_point=staff.current_point
                    point_change=int(past_point*(current_increst-1))
                    NatureRecord.objects.create(target=staff,past_point=past_point,point_change=point_change)