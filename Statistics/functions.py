# coding:utf-8
import datetime
import time
from django.db.models import Count, Sum, Q

from kpi.models import *
from Statistics.models import *


def split_department_point_by_time(unit='day', begin_time=None, end_time=None, department=None):
    x_data = []  # x轴参数列表
    y_data = []  # 此前贡献点总量
    y_data_branchs = []  # 当天分部门贡献点
    y_titles = ['此前部门总贡献点']
    departments = department.department_set.all()
    staffs = department.totle_staffs
    if not end_time:
        end_time = datetime.date.today()
    elif isinstance(end_time, datetime.datetime):
        end_time = end_time.date()
    records = PointRecord.objects.filter(target__in=staffs, time__lte=end_time)
    if unit == 'day':
        if not begin_time:
            begin_time = datetime.date.today() - datetime.timedelta(days=10)
        elif isinstance(begin_time, datetime.datetime):
            begin_time = begin_time.date()
        current_day = begin_time
        while current_day < end_time:
            x_data.append(current_day.strftime('%y年%m月%d日'))
            totle_points = StaffDailyPoint.objects.filter(
                target__in=staffs, date=current_day).aggregate(sum=Sum('point'))['sum']
            if not totle_points:
                totle_points = 0
            y_data.append(totle_points)
            begin = current_day
            end = current_day + datetime.timedelta(days=1)
            i = 0
            for department in departments:
                title_name=u'%s增长' % department.short_name
                if not title_name in y_titles:
                    y_titles.append(title_name)
                if len(y_data_branchs) <= i:
                    y_data_branchs.append([])
                temp_array = y_data_branchs[i]
                department_records = records.filter(
                    time__range=(begin, end), target__department=department, record_type__in=[1, 2])
                totle_change = 0
                for record in department_records:
                    totle_change += record.point_change
                temp_array.append(totle_change)
                i += 1
            current_day += datetime.timedelta(days=1)
    elif unit == 'month':
        if not end_time:
            end_year = datetime.date.today().year
            end_month = datetime.date.today().month
            end_day = datetime.date.today().day
        else:
            end_year = end_time.year
            end_month = end_time.month
            end_day = end_time.day
        if not begin_time:
            begin_year = end_year
            begin_month = end_month - 5
            if begin_month < 1:
                begin_month += 12
                begin_year -= 1
            begin_day = 1
        else:
            begin_year = begin_time.year
            begin_month = begin_time.month
            begin_day = begin_time.day
        y = begin_year
        m = begin_month
        while (y * 100 + m) <= (end_year * 100 + end_month):
            x_data.append('%s年%s月' % (y, m))
            begin = datetime.date(y, m, begin_day)
            if begin_day != 1:
                begin_day = 1
            if (y * 100 + m) < (end_year * 100 + end_month):
                if m + 1 <= 12:
                    end = datetime.date(y, m + 1, 1)
                else:
                    end = datetime.date(y + 1, 1, 1)
            else:
                end = datetime.date(y, m, end_day) + datetime.timedelta(days=1)
            daily_points = StaffDailyPoint.objects.filter(
                target__in=staffs, date=begin)
            totle_points = 0
            for point in daily_points:
                totle_points += point.point
            y_data.append(totle_points)
            begin = current_day
            end = current_day + datetime.timedelta(days=1)
            i = 0
            for department in departments:
                title_name=u'%s增长' % department.short_name
                if not title_name in y_titles:
                    y_titles.append(title_name)
                department_records = records.filter(
                    time__range=(begin, end), target__department=department, record_type__in=[1, 2])
                if len(y_data_branchs) <= i:
                    y_data_branchs.append([])
                temp_array = y_data_branchs[i]
                totle_change = 0
                for record in department_records:
                    totle_change += record.point_change
                temp_array.append(totle_change)
                i += 1
            if m + 1 <= 12:
                m += 1
            else:
                m = 1
                y += 1

    elif unit == 'week':
        pass
    else:
        pass

    return (x_data, y_data, y_data_branchs, y_titles)


def department_point_option(xdata=[], ydata=[], ydata_branchs=[], ytitles=[]):
    series = [
        {
            'name': '此前部门总贡献点',
            'type': 'bar',
            'data': ydata,
            'stack': '部门贡献增长统计',
            'itemStyle': {'normal': {'areaStyle': {'type': 'default'}}},
            'markPoint': {
                    'data': [
                        {'type': 'max', 'name': '最大贡献点'},
                        {'type': 'min', 'name': '最小贡献点'}
                    ]
            },
            'markLine': {
                'data': [
                        {'type': 'average', 'name': '平均贡献点'}
                ]
            }
        }
    ]
    for data_branch in ydata_branchs:
        title = ytitles[ydata_branchs.index(data_branch) + 1]
        temp_dic = {
            'name': title,
            'type': 'bar',
            'data': data_branch,
            'stack': '部门贡献增长统计',
            'itemStyle': {'normal': {'areaStyle': {'type': 'default'}}},
            'markPoint': {
                    'data': [
                        {'type': 'max', 'name': '最大贡献点'},
                        {'type': 'min', 'name': '最小贡献点'}
                    ]
            },
            'markLine': {
                'data': [
                        {'type': 'average', 'name': '平均贡献点'}
                ]
            }
        }
        series.append(temp_dic)
    option = {
        'title': {
            'text': '部门贡献增长统计',  # 字符串
        },
        'tooltip': {
            'trigger': 'axis'
        },
        'legend': {
            'data': ytitles,
            'x': '10%',
            'y': 'bottom',
        },
        'calculable': True,
        'yAxis': [
            {
                'type': 'value',
                'name': '贡献点数',
            }
        ],
        'toolbox': {
            'show': True,
            'feature': {
                'mark': {'show': True},
                'dataView': {'show': True, 'readOnly': False},
                'magicType': {'show': True, 'type': ['line', 'bar']},
                'restore': {'show': True},
                'saveAsImage': {'show': True}
            }
        },
        'xAxis': [
            {
                'type': 'category',
                'data': xdata
            }
        ],
        'series': series,
    }
    return option


def split_staff_point_by_time(unit='day', begin_time=None, end_time=None, department=None):
    x_data = []  # x轴参数列表
    y_data = []  # 此前部门内贡献点总量
    y_data_branchs = []  # 部门各人贡献点增长量
    y_titles = ['此前部门内总贡献点']
    staffs = department.staff_set.all()
    if not end_time:
        end_time = datetime.date.today()
    elif isinstance(end_time, datetime.datetime):
        end_time = end_time.date()
    records = PointRecord.objects.filter(target__in=staffs, time__lte=end_time)
    if unit == 'day':
        if not begin_time:
            begin_time = datetime.date.today() - datetime.timedelta(days=10)
        elif isinstance(begin_time, datetime.datetime):
            begin_time = begin_time.date()
        current_day = begin_time
        while current_day < end_time:
            x_data.append(current_day.strftime('%y年%m月%d日'))
            totle_points = StaffDailyPoint.objects.filter(
                target__in=staffs, date=current_day).aggregate(sum=Sum('point'))['sum']
            if not totle_points:
                totle_points = 0
            y_data.append(totle_points)
            begin = current_day
            end = current_day + datetime.timedelta(days=1)
            i = 0
            for staff in staffs:
                title_name=u'%s' % staff.name
                if not title_name in y_titles:
                    y_titles.append(title_name)
                if len(y_data_branchs) <= i:
                    y_data_branchs.append([])
                temp_array = y_data_branchs[i]
                staff_records = records.filter(
                    time__range=(begin, end), target=staff, record_type__in=[1, 2])
                totle_change = 0
                for record in staff_records:
                    totle_change += record.point_change
                temp_array.append(totle_change)
                i += 1
            current_day += datetime.timedelta(days=1)
    elif unit == 'month':
        if not end_time:
            end_year = datetime.date.today().year
            end_month = datetime.date.today().month
            end_day = datetime.date.today().day
        else:
            end_year = end_time.year
            end_month = end_time.month
            end_day = end_time.day
        if not begin_time:
            begin_year = end_year
            begin_month = end_month - 5
            if begin_month < 1:
                begin_month += 12
                begin_year -= 1
            begin_day = 1
        else:
            begin_year = begin_time.year
            begin_month = begin_time.month
            begin_day = begin_time.day
        y = begin_year
        m = begin_month
        while (y * 100 + m) <= (end_year * 100 + end_month):
            x_data.append('%s年%s月' % (y, m))
            begin = datetime.date(y, m, begin_day)
            if begin_day != 1:
                begin_day = 1
            if (y * 100 + m) < (end_year * 100 + end_month):
                if m + 1 <= 12:
                    end = datetime.date(y, m + 1, 1)
                else:
                    end = datetime.date(y + 1, 1, 1)
            else:
                end = datetime.date(y, m, end_day) + datetime.timedelta(days=1)
            totle_points = StaffDailyPoint.objects.filter(
                target__in=staffs, date=begin).aggregate(sum=Sum('point'))['sum']
            y_data.append(totle_points)
            begin = current_day
            end = current_day + datetime.timedelta(days=1)
            i = 0
            for department in departments:
                title_name=u'%s' % staff.name
                if not title_name in y_titles:
                    y_titles.append(title_name)
                if len(y_data_branchs) <= i:
                    y_data_branchs.append([])
                temp_array = y_data_branchs[i]
                staff_records = records.filter(
                    time__range=(begin, end), target=staff, record_type__in=[1, 2])
                totle_change = 0
                for record in staff_records:
                    totle_change += record.point_change
                temp_array.append(totle_change)
                i += 1
            if m + 1 <= 12:
                m += 1
            else:
                m = 1
                y += 1

    elif unit == 'week':
        pass
    else:
        pass

    return (x_data, y_data, y_data_branchs, y_titles)


def staff_point_option(xdata=[], ydata=[], ydata_branchs=[], ytitles=[]):
    series = [
        {
            'name': '部门内员工总贡献点',
            'type': 'bar',
            'data': ydata,
            'stack': '员工贡献增长统计',
            'itemStyle': {'normal': {'areaStyle': {'type': 'default'}}},
            'markPoint': {
                    'data': [
                        {'type': 'max', 'name': '最大贡献点'},
                        {'type': 'min', 'name': '最小贡献点'}
                    ]
            },
            'markLine': {
                'data': [
                        {'type': 'average', 'name': '平均贡献点'}
                ]
            }
        }
    ]
    for data_branch in ydata_branchs:
        title = ytitles[ydata_branchs.index(data_branch) + 1]
        temp_dic = {
            'name': title,
            'type': 'bar',
            'data': data_branch,
            'stack': '员工贡献增长统计',
            'itemStyle': {'normal': {'areaStyle': {'type': 'default'}}},
            'markPoint': {
                    'data': [
                        {'type': 'max', 'name': '最大贡献点'},
                        {'type': 'min', 'name': '最小贡献点'}
                    ]
            },
            'markLine': {
                'data': [
                        {'type': 'average', 'name': '平均贡献点'}
                ]
            }
        }
        series.append(temp_dic)
    option = {
        'title': {
            'text': '员工贡献增长统计',  # 字符串
        },
        'tooltip': {
            'trigger': 'axis'
        },
        'legend': {
            'data': ytitles,
            'x': '10%',
            'y': 'bottom',
        },
        'calculable': True,
        'yAxis': [
            {
                'type': 'value',
                'name': '贡献点数',
            }
        ],
        'toolbox': {
            'show': True,
            'feature': {
                'mark': {'show': True},
                'dataView': {'show': True, 'readOnly': False},
                'magicType': {'show': True, 'type': ['line', 'bar']},
                'restore': {'show': True},
                'saveAsImage': {'show': True}
            }
        },
        'xAxis': [
            {
                'type': 'category',
                'data': xdata
            }
        ],
        'series': series,
    }
    return option



def set_staff_daily_point():
    for staff in Staff.objects.all():
        StaffDailyPoint.objects.create(target=staff)