# coding=utf-8
import logging
import datetime
import re

from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.forms.models import model_to_dict, ModelChoiceField
from django.db.models import Q
import os

from Utils.BaseForm import ReadonlyModelForm

from kpi.models import *

# from SSO.models import Ticket as SSO_Ticket

logger = logging.getLogger(__name__)

# 部门


class DepartmentForm(ReadonlyModelForm):

    class Meta:
        model = Department
        exclude = []


class CreateDepartmentForm(ModelForm):

    class Meta:
        model = Department
        exclude = ['level', 'parent']
    def __init__(self, *args, **kwargs):
        super(CreateDepartmentForm, self).__init__(*args, **kwargs)
        self.fields['positions'].required=False

# 基础配置


class DepartmentSetForm(ReadonlyModelForm):

    class Meta:
        model = DepartmentSet
        exclude = []


class CreateDepartmentSetForm(ModelForm):
    parent=None
    class Meta:
        model = DepartmentSet
        exclude = ['department']

    def clean_increase_min(self):
        increase=self.cleaned_data['increase']
        increase_min=self.cleaned_data['increase_min']
        if increase<increase_min:
            raise forms.ValidationError(u'贡献最小增幅不得高于参考增幅')
        if self.parent:
            if increase_min>parent.increase_min:
                raise forms.ValidationError(u'部门最小贡献增幅不得小于上级部门规定最小增幅')
        return increase_min

    def clean_increase_max(self):
        increase=self.cleaned_data['increase']
        increase_max=self.cleaned_data['increase_max']
        if increase_max<increase:
            raise forms.ValidationError(u'贡献最大增幅不得低于参考增幅')
        if self.parent:
            if increase_max>parent.increase_max:
                raise forms.ValidationError(u'部门最大贡献增幅不得高于上级部门规定最大增幅')
        return increase_max  

# 基础配置


class BaseSetForm(ReadonlyModelForm):

    class Meta:
        model = BaseSet
        exclude = []


class CreateBaseSetForm(ModelForm):

    class Meta:
        model = BaseSet
        exclude = ['company']


class StaffForm(ReadonlyModelForm):

    class Meta:
        model = Staff
        exclude = []


class CreateStaffForm(ModelForm):

    class Meta:
        model = Staff
        exclude = ['department', 'account', 'current_point', 'base_point']

# 基础配置


class StaffSetForm(ReadonlyModelForm):

    class Meta:
        model = StaffSet
        exclude = ['staff']


class CreateStaffSetForm(ModelForm):

    class Meta:
        model = StaffSet
        exclude = ['staff']


class HandRecordForm(ReadonlyModelForm):

    class Meta:
        model = HandRecord
        exclude = ['target','history_holders']


class CreateHandRecordForm(ModelForm):

    class Meta:
        model = HandRecord
        fields = ['expect_end', 'expect_notice', 'change_type',
                  'except_point_change', 'except_increase_change', 'remark']

    def clean_expect_end(self):
        expect_end=self.cleaned_data['expect_end']
        today=datetime.date.today()
        if expect_end<today:
            raise forms.ValidationError(u'预计实现日期不得早于今天')
        return expect_end

    def clean_expect_notice(self):
        expect_end=self.cleaned_data['expect_end']
        expect_notice=self.cleaned_data['expect_notice']
        today=datetime.date.today()
        if expect_notice<today:
            raise forms.ValidationError(u'通知时间不得早于今天')
        if expect_notice>expect_end:
            raise forms.ValidationError(u'通知时间不得迟于预计实现日期')
        return expect_notice

    def clean_except_point_change(self):
        change_type = self.cleaned_data['change_type']
        except_point_change = self.cleaned_data['except_point_change']
        if change_type == 1:
            if not except_point_change:
                raise forms.ValidationError(u'预计贡献点变动不能为空')
        elif change_type == 2:
            if except_point_change:
                raise forms.ValidationError(u'预计贡献点变动不能变动')
        else:
            raise forms.ValidationError(u'贡献变化类型错误')
        return except_point_change

    def clean_except_increase_change(self):
        change_type = self.cleaned_data['change_type']
        except_increase_change = self.cleaned_data['except_increase_change']
        if change_type == 1:
            if except_increase_change:
                raise forms.ValidationError(u'预计贡献增幅不能变动')
        elif change_type == 2:
            if not except_increase_change:
                raise forms.ValidationError(u'预计贡献增幅点变动不能为空')
        else:
            raise forms.ValidationError(u'贡献变化类型错误')
        return except_increase_change


class CompleteHandRecordForm(ModelForm):

    class Meta:
        model = HandRecord
        fields = ['point_change', 'increase_change', 'remark']

    def __init__(self, *args, **kwargs):
        super(CompleteHandRecordForm, self).__init__(*args, **kwargs)
        record = kwargs.get('instance')
        if record:
            if record.change_type == 1:
                self.fields.pop('increase_change')
            else:
                self.fields.pop('point_change')


class CreatePositionForm(ModelForm):

    class Meta:
        model = Position
        exclude = []

    def __init__(self, *args, **kwargs):
        super(CreatePositionForm, self).__init__(*args, **kwargs)
        self.fields['role'].queryset=Role.objects.exclude(id__in=[1,2])
