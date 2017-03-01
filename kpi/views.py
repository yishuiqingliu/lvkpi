# coding=utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate
from Utils.http import json_response
from Utils.functions import *
from dateutil import tz
import logging
import datetime
import time
import copy

from kpi.models import *
from kpi.forms import *
from kpi.functions import *
# from


@require_permission(permission_id=1)
@leader_need()
def department_manage(request,did):
    title=u'部门管理'
    department=Department.objects.get(id=did)
    departmentset=department.departmentset
    children=department.department_set.all()
    form1=DepartmentForm(instance=department)
    form2=DepartmentSetForm(instance=departmentset)
    context={
        'title':title,
        'form1':form1,
        'form2':form2,
        'department':department,
        'children':children,
    }
    return render_to_response('department/department_manage.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=2)
@leader_need()
def department_detail(request,did):
    title=u'部门详情'
    department=Department.objects.get(id=did)
    departmentset=department.departmentset
    children=department.department_set.all()
    form1=DepartmentForm(instance=department)
    form2=DepartmentSetForm(instance=departmentset)
    context={
        'title':title,
        'form1':form1,
        'form2':form2,
    }
    return render_to_response('department/department_detail.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=3)
@leader_need()
def department_add(request,pid=None):
    account=request.user.account
    context={}
    if pid:
        title=u'添加部门信息'
        parent=Department.objects.get(id=pid)
        if request.POST:
            form1=CreateDepartmentForm(request.POST)
            form1.fields['positions'].queryset=parent.positions.all()
            form2=CreateDepartmentSetForm(request.POST)
            if form1.is_valid() and form2.is_valid():
                department=form1.save(commit=False)
                department.level=2
                department.parent=parent
                departmentset=form2.save(commit=False)
                if departmentset.increase_min<parent.departmentset.increase_min:
                    return json_response({'code':1,'msg':'部门最小贡献增幅不得小于上级部门规定最小增幅'})
                if departmentset.increase_max>parent.departmentset.increase_max:
                    return json_response({'code':1,'msg':'部门最大贡献增幅不得高于上级部门规定最大增幅'})
                department.save()
                departmentset.department=department
                departmentset.save()
                return HttpResponseRedirect('/department_manage/%s' % department.parent.id)
        else:
            form1=CreateDepartmentForm()
            form1.fields['positions'].queryset=parent.positions.all()
            form2=CreateDepartmentSetForm(instance=parent.departmentset)
        context={
            'title':title,
            'form1':form1,
            'form2':form2,
            'parent':parent,
        }
    else:
        title=u'添加公司信息'
        if account.staff.department:
            return HttpResponse(u'您已经有公司信息，不能再次添加')
        if request.POST:
            form1=CreateDepartmentForm(request.POST)
            form1.fields.pop('positions')
            form2=CreateDepartmentSetForm(request.POST)
            form3=CreateBaseSetForm(request.POST)
            if form1.is_valid() and form2.is_valid() and form3.is_valid():
                department=form1.save(commit=False)
                department.level=1
                department.save()
                department.positions.add(Position.objects.get(id=1))
                account.staff.department=department
                account.staff.save()
                departmentset=form2.save(commit=False)
                departmentset.department=department
                departmentset.save()
                department.positions.add(Position.objects.get(id=1))
                baseset=form3.save(commit=False)
                baseset.company=department
                baseset.save()
                account.default_url='/staff_detail/%s' % account.staff.id
                account.save()
                return HttpResponseRedirect('/department_manage/%s' % department.id)
        else:
            form1=CreateDepartmentForm()
            form1.fields.pop('positions')
            form2=CreateDepartmentSetForm()
            form3=CreateBaseSetForm()
        context={
            'title':title,
            'form1':form1,
            'form2':form2,
            'form3':form3,

        }
    return render_to_response('department/department_add.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=4)
@leader_need()
def department_edit(request,did):
    title=u'编辑部门信息'
    account=request.user.account
    department=Department.objects.get(id=did)
    departmentset=department.departmentset
    form3=None
    if request.POST:
        form1=CreateDepartmentForm(request.POST,instance=department)
        form2=CreateDepartmentSetForm(request.POST,instance=departmentset)
        if department.level==1:
            baseset=department.baseset
            form3=CreateBaseSetForm(request.POST,request.FILES,instance=baseset)
            if form1.is_valid() and form2.is_valid() and form3.is_valid():
                form1.save()
                form2.save()
                form3.save()
                return HttpResponseRedirect('/department_manage/%s' % account.staff.department.id)
        else:
            if form1.is_valid() and form2.is_valid():
                form1.save()
                form2.save()
                return HttpResponseRedirect('/department_manage/%s' % account.staff.department.id)
    else:
        form1=CreateDepartmentForm(instance=department)
        form2=CreateDepartmentSetForm(instance=departmentset)
        if department.level==1:
            baseset=department.baseset
            form3=CreateBaseSetForm(instance=baseset)
    context={
        'title':title,
        'form1':form1,
        'form2':form2,
        'form3':form3,
    }
    return render_to_response('department/department_edit.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=5)
@leader_need()
def position_add(request,did=None):
    account=request.user.account
    department=Department.objects.get(id=did)
    title=u'添加部门职位'
    if request.POST:
        form=CreatePositionForm(request.POST)
        if form.is_valid():
            position=form.save()
            department.positions.add(position)
            return HttpResponseRedirect('/staff_manage/%s' % did)
    else:
        form=CreatePositionForm()
    context={
        'title':title,
        'form':form,
        'department':department,
    }
    return render_to_response('department/position_add.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=6)
@leader_need()
def staff_manage(request,did):
    title=u'员工管理'
    department=Department.objects.get(id=did)
    departmentset=department.departmentset
    staffs=department.staff_set.all()
    form1=DepartmentForm(instance=department)
    form2=DepartmentSetForm(instance=departmentset)
    context={
        'title':title,
        'form1':form1,
        'form2':form2,
        'department':department,
        'staffs':staffs,
    }
    return render_to_response('staff/staff_manage.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=7)
@leader_need()
def staff_detail(request,sid=None):
    title=u'个人详情'
    if sid:
        staff=Staff.objects.get(id=sid)
    else:
        staff=request.user.account.staff
    staffset=staff.staffset
    form1=StaffForm(instance=staff)
    form2=StaffSetForm(instance=staffset)
    point_dic={}
    for record in staff.pointrecord_set.all().order_by('-time'):
        record_date=record.time.strftime("%Y年%m月%d日")
        if point_dic.has_key(record_date):
            array_temp1=point_dic[record_date]
            array_temp1.append(record)
            point_dic[record_date]=array_temp1
        else:
            point_dic[record_date]=[record]
    point_records=[]
    for key in point_dic.keys():
        point_records.insert(0,{'date':key,'records':point_dic[key]})
    context={
        'title':title,
        'form1':form1,
        'form2':form2,
        'staff':staff,
        'hand_records':staff.my_hand_records.all(),
        'nature_records':staff.my_nature_records.all(),
        'point_records':point_records,
    }
    return render_to_response('staff/staff_detail.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=8)
@leader_need()
def staff_add(request,did=None):
    account=request.user.account
    title=u'添加员工信息'
    department=None
    if did:
        department=Department.objects.get(id=did)
        if request.POST:
            form1=CreateStaffForm(request.POST,request.FILES)
            form1.fields['position'].queryset=department.positions.all()
            form2=CreateStaffSetForm(request.POST)
            if form1.is_valid() and form2.is_valid():
                staff=form1.save(commit=False)
                staffset=form2.save(commit=False)
                if staffset.increase<department.departmentset.increase_min:
                    return json_response({'code':1,'msg':'个人贡献增幅不得低于部门设定中的最小增幅'})
                if staffset.increase>department.departmentset.increase_max:
                    return json_response({'code':1,'msg':'个人贡献增幅不得高于部门设定中的最大增幅'})
                staff.department=department
                user = User.objects.create_user(
                    username=staff.phone, password='123456', first_name=staff.name)
                account = Account(accountinfo=user,default_url='')
                account.save()
                if staff.position.role:
                    staff_role=staff.position.role
                    account.roles.add(staff_role)
                staff.account=account
                staff.save()
                staffset.staff=staff
                staffset.save()
                return HttpResponseRedirect('/staff_manage/%s' % did)
        else:
            form1=CreateStaffForm()
            form1.fields['position'].queryset=department.positions.all()
            form2=CreateStaffSetForm({'increase':department.departmentset.increase})
    else:
        title=u'添加创始人信息'
        if request.POST:
            form1=CreateStaffForm(request.POST,request.FILES)
            form1.fields.pop('position')
            form2=CreateStaffSetForm(request.POST)
            if form1.is_valid() and form2.is_valid():
                staff=form1.save(commit=False)
                staff.position=Position.objects.get(id=1)
                user = User.objects.create_user(
                    username=staff.phone, password='123456', first_name=staff.name)
                account = Account(accountinfo=user,default_url='')
                account.save()
                if staff.position.role:
                    staff_role=staff.position.role
                    account.roles.add(staff_role)
                staff.account=account
                staff.save()
                staffset=form2.save(commit=False)
                staffset.staff=staff
                staffset.save()
                return HttpResponseRedirect('/staff_detail/%s' % staff.id)
        else:
            form1=CreateStaffForm()
            form1.fields.pop('position')
            form2=CreateStaffSetForm()
    context={
        'title':title,
        'form1':form1,
        'form2':form2,
        'department':department,
    }        
    return render_to_response('staff/staff_add.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=9)
@leader_need()
def staff_edit(request,sid):
    title=u'编辑员工信息'
    staff=Staff.objects.get(id=sid)
    if request.POST:
        form1=CreateStaffForm(request.POST,request.FILES,instance=staff)
        if form1.is_valid():
            form1.save()
            return HttpResponseRedirect('/staff_manage/%s' % staff.department.id)
    else:
        form1=CreateStaffForm(instance=staff)
    context={
        'title':title,
        'form1':form1,
        'hand_records_count':staff.my_hand_records.all().count(),
        'nature_records_count':staff.my_nature_records.all().count(),
    }
    return render_to_response('staff/staff_edit.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=10)
@leader_need()
def hand_record_add(request,sid):
    title=u'贡献变动记录添加'
    staff=Staff.objects.get(id=sid)
    operator=request.user.account.staff
    if request.POST:
        form1=CreateHandRecordForm(request.POST)
        if form1.is_valid():
            record=form1.save(commit=False)
            record.target=staff
            record.creator=operator
            record.holder=operator
            record.save()
            HandRecordHistory.objects.create(handrecord=record,operator=operator,remark=u'【%s】创建了本条记录' % operator)
            return HttpResponseRedirect('/staff_manage/%s' % staff.department.id)
    else:
        form1=CreateHandRecordForm()
    context={
        'title':title,
        'form1':form1,
        'hand_records_count':staff.my_hand_records.all().count(),
        'nature_records_count':staff.my_nature_records.all().count(),
    }
    return render_to_response('staff/hand_record_add.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=11)
@leader_need()
def hand_record_detail(request,hrid):
    title=u'贡献变动记录详情'
    record=HandRecord.objects.get(id=hrid)
    form1=HandRecordForm(instance=record)
    historys=record.handrecordhistory_set.all()
    context={
        'title':title,
        'form1':form1,
        'historys':historys,
    }
    return render_to_response('staff/hand_record_detail.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=12)
@leader_need()
def hand_record_complete(request,hrid):
    title=u'贡献变动记录处理'
    record=HandRecord.objects.get(id=hrid)
    operator=request.user.account.staff
    if request.POST:
        old_remark=record.remark
        form1=CompleteHandRecordForm(request.POST,instance=record)
        if form1.is_valid():
            record=form1.save(commit=False)
            record.holder=operator
            record.status=2
            record.save()
            if old_remark!=record.remark:
                remark=u'【%s】确认处理了本条记录，记录备注从【%s】改成【%s】' % (operator,old_remark,record.remark)
            else:
                remark=u'【%s】确认处理了本条记录' % operator
            HandRecordHistory.objects.create(handrecord=record,operator=operator,remark=remark)
            return HttpResponseRedirect('/staff_manage/%s' % record.target.department.id)
    else:
        form1=CompleteHandRecordForm(instance=record)
    context={
        'title':title,
        'form1':form1,
        'hand_records_count':record.target.my_hand_records.all().count(),
        'nature_records_count':record.target.my_nature_records.all().count(),
    }
    return render_to_response('staff/hand_record_complete.html', context, context_instance=RequestContext(request))

@require_permission(permission_id=13)
def set_default_url(request):
    url=request.GET.get('url')
    account=request.user.account
    if url:
        account.default_url=url
        account.save()
        return json_response({'code':0,'msg':'成功'})
    else:
        return json_response({'code':1,'msg':'参数缺失'})

@require_permission(permission_id=14)
def turn_default_url(request):
    account=request.user.account
    if account.default_url:
        return HttpResponseRedirect(account.default_url)
    else:
        return json_response({'code':1,'msg':'默认页不存在'})

def test(request):
    context={
    }
    return render_to_response('base.html', context, context_instance=RequestContext(request))