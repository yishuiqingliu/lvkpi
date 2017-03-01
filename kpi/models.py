# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone
import datetime
import time

from Utils.BaseModel import PhoneNumberField, CurrencyField, MultiSelectField

INCREASE_TYPES = (
    (1, u'按月'),
    (3, u'按季'),
    (6, u'按半年'),
    (12, u'按年'),
)

# 账号相关


class Permission(models.Model):

    """docstring for Permission"""
    permission_id = models.IntegerField(u'权限ID', unique=True)
    permission_description = models.TextField(u'权限描述')

    def __unicode__(self):
        return u'ID：%s，描述：%s' % (self.permission_id, self.permission_description)


class Role(models.Model):

    """docstring for Role"""
    role_id = models.IntegerField(u'角色ID', unique=True)
    name = models.CharField(u'角色名', max_length=20)
    description = models.TextField(u'角色描述')
    permissions = models.ManyToManyField(Permission, verbose_name=u'角色权限')

    def __unicode__(self):
        return self.name


class Account(models.Model):
    accountinfo = models.OneToOneField(User)
    roles = models.ManyToManyField(Role, verbose_name=u'角色')
    default_url = models.URLField(u'默认页面', default='')

    @property
    def role_list(self):
        role_list = []
        for role in self.roles.all():
            role_list.append(role.role_id)
        return role_list

    @property
    def promission_list(self):
        promission_list = []
        for role in self.roles.all():
            for promission in role.permissions.all():
                if not promission.permission_id in promission_list:
                    promission_list.append(promission.permission_id)
        return promission_list

    @property
    def role_verbose(self):
        rolestr = ''
        for role in self.roles.all():
            if rolestr:
                rolestr = u'%s兼%s' % (rolestr, role.name)
            else:
                rolestr = role.name
        if not isinstance(rolestr, unicode):
            rolestr = rolestr.decode('utf-8')
        return rolestr

    def __unicode__(self):
        return self.staff.name


class Position(models.Model):
    level = models.IntegerField(u'重要度（数字越大越重要）')
    name = models.CharField(u'职位全称', max_length=64)
    short_name = models.CharField(u'职位简称', max_length=64)
    remark = models.TextField(u'职位描述')
    role = models.ForeignKey(
        Role, verbose_name=u'对应系统角色', blank=True, null=True)

    def __unicode__(self):
        return self.short_name


class Department(models.Model):
    DEPARTMENT_LEVELS = (
        (1, u'公司'),
        (2, u'子部门')
    )
    level = models.SmallIntegerField(
        u'部门层级', choices=DEPARTMENT_LEVELS, default=2)
    name = models.CharField(u'全称', max_length=64)
    short_name = models.CharField(u'简称', max_length=64)
    parent = models.ForeignKey(
        'self', verbose_name=u'上级部门', blank=True, null=True)
    positions = models.ManyToManyField(Position, verbose_name=u'所有岗位')
    remark = models.TextField(u'描述')

    @property
    def level_verbose(self):
        d = dict(self.DEPARTMENT_LEVELS)
        return d[self.level] if self.level in d else ''

    @property
    def positions_verbose(self):
        position_array = []
        for position in self.positions:
            position_array.append(position.short_name)
        return u'、'.join(position_array)

    @property
    def positions_set(self):
        return self.positions.all()

    @property
    def totle_positions_set(self):
        totle_positions_set = Position.objects.none()
        for child in self.children:
            totle_positions_set = totle_positions_set | child.positions_set.all()
        totle_positions_set = totle_positions_set.order_by('-level').distinct()
        return totle_positions_set

    @property
    def staffs(self):
        return self.staff_set.all()

    @property
    def staff_description(self):
        des_array = []
        for position in self.positions.all():
            des_array.append(
                u'%s个%s' % (self.staff_set.filter(position__id=position.id).count(), position))
        return u'；'.join(des_array)

    @property
    def totle_staffs(self):
        departments = self.children_with_self
        totle_staffs = Staff.objects.filter(department__in=departments)
        return totle_staffs

    @property
    def company(self):
        if self.level == 1:
            return self
        else:
            return self.parent.company

    @property
    def children(self):
        children = self.department_set.all()
        for child in self.department_set.all():
            children = children | child.children
        return children

    @property
    def children_with_self(self):
        return self.children | Department.objects.filter(id=self.id)

    @property
    def link(self):
        link = '/department_detail/%s' % self.id
        return link

    def __unicode__(self):
        return self.short_name


class DepartmentSet(models.Model):
    department = models.OneToOneField(Department, verbose_name=u'对应部门')
    increase = models.DecimalField(
        u'贡献增幅参考值(%/年)', max_digits=5, decimal_places=2)
    increase_min = models.DecimalField(
        u'贡献增幅下限(%/年)', max_digits=5, decimal_places=2)
    increase_max = models.DecimalField(
        u'贡献增幅上限(%/年)', max_digits=5, decimal_places=2)
    increase_type = models.SmallIntegerField(
        u'贡献度自然变动频率', choices=INCREASE_TYPES, default=1)
    NOTTICE_LEVLS = (
        (1000, u'满千通知'),
        (500, u'满五百通知'),
        (100, u'满百通知'),
        (50, u'满五十通知'),
        (10, u'满十通知'),
    )
    staff_notice = models.SmallIntegerField(
        u'员工贡献变动通知幅度', choices=NOTTICE_LEVLS)
    NOTICE_TARGET = (
        (1, '公司负责人'),
        (2, u'公司财务'),
        (3, u'部门负责人'),
    )
    increase_notice = MultiSelectField(
        u'增幅变动通知对象', choices=NOTICE_TARGET, max_length=60)

    @property
    def staff_notice_verbose(self):
        d = dict(self.NOTTICE_LEVLS)
        return d[self.staff_notice] if self.staff_notice in d else None

    @property
    def increase_notice_verbose(self):
        d = dict(self.NOTICE_TARGET)
        return d[self.increase_notice] if self.increase_notice in d else None

    def __unicode__(self):
        res = u'年贡献增幅参考值%s%%，贡献度增长%s' % (
            self.increase, self.staff_notice_verbose)
        return res


class BaseSet(models.Model):
    company = models.OneToOneField(Department, verbose_name=u'对应部门')
    logo = models.ImageField(
        u'公司logo', upload_to='company/logo/', default='/static/dist/img/user2-160x160.jpg')
    STAFF_NOTTICES = (
        (1, u'通知公司负责人'),
        (2, u'通知部门负责人'),
        (3, u'通知上级部门负责人'),
        (4, u'通知财务'),
        (5, u'通知本人'),
    )
    staff_notice_person = MultiSelectField(
        u'员工贡献变动直接通知对象', max_length=30, choices=STAFF_NOTTICES)
    DEPARTMENT_NOTTICES = (
        (1, u'通知公司负责人'),
        (2, u'通知部门负责人'),
        (3, u'通知上级部门负责人'),
        (4, u'通知财务'),
    )
    department_notice = MultiSelectField(
        u'部门贡献变动直接通知对象', max_length=30, choices=DEPARTMENT_NOTTICES)
    can_normal_login = models.BooleanField(u'普通员工能否登录', default=False)


class Staff(models.Model):

    """docstring for Person"""
    department = models.ForeignKey(
        Department, verbose_name=u'所在部门', blank=True, null=True)
    join_date = models.DateField(u'入职日期', default=timezone.now)
    account = models.OneToOneField(Account, verbose_name=u'账号')
    base_point = models.IntegerField(u'初始贡献点')
    current_point = models.IntegerField(u'当前贡献点')
    salary = models.IntegerField(u'薪水（元/月）')
    name = models.CharField(u'姓名', max_length=64)
    GENDERS = (
        (1, u'男'),
        (2, u'女'),
    )
    gender = models.SmallIntegerField(u'性别', choices=GENDERS)
    phone = PhoneNumberField(u'联系电话')
    photo = models.ImageField(
        u'照片', upload_to='staff/photos/', blank=True, null=True)
    qq = models.CharField(u'QQ号', max_length=12, default='')
    email = models.EmailField(u'电子邮箱', blank=True, null=True)
    position = models.ForeignKey(Position, verbose_name=u'职位')
    id_number = models.CharField(
        u'身份证号码', max_length=18, blank=True, null=True)
    id_address = models.CharField(
        u'身份证地址', max_length=500, blank=True, null=True)
    id_photo = models.ImageField(
        u'身份证复印件', upload_to='person/id/', blank=True, null=True)
    address = models.CharField(u'住址', max_length=500, blank=True, null=True)
    name2 = models.CharField(u'备用联系人姓名', max_length=16, blank=True, null=True)
    RELATIONS = (
        ('FRIEND', u'朋友'),
        ('FAMILY', u'家人'),
        ('COLLEAGUE', u'同事'),
        ('OTHER', u'其他'),)
    relation = models.CharField(
        u'备用联系人关系', choices=RELATIONS, max_length=10, blank=True, null=True)
    phone2 = PhoneNumberField(u'备用联系人电话', blank=True, null=True)

    class Meta:
        ordering = ["position"]

    @property
    def gender_verbose(self):
        d = dict(self.GENDERS)
        return d[self.gender] if self.gender in d else None

    @property
    def staff_notices_verbose(self):
        d = dict(self.RELATIONS)
        return d[self.relation] if self.relation in d else None

    @property
    def last_hand_record(self):
        hand_records = self.my_hand_records.all().order_by('-create_time')
        if hand_records.count() > 0:
            return hand_records[0]
        else:
            return None

    @property
    def link(self):
        link = '/staff_detail/%s' % self.id
        return link

    @property
    def photo_verbose(self):
        if self.photo:
            return self.photo
        elif self.department:
            return self.department.company.baseset.logo
        else:
            return '/static/dist/img/user2-160x160.jpg'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_first = False
        if not self.id:
            is_first = True
            self.base_point = self.current_point = self.salary
        super(Staff, self).save(*args, **kwargs)
        if is_first:
            account = self.account
            if self.department:
                account.default_url = '/staff_detail/%s' % self.id
            else:
                account.default_url = '/department_add'
            account.save()


class StaffSet(models.Model):
    staff = models.OneToOneField(Staff, verbose_name=u'对应员工')
    increase = models.FloatField(u'贡献度增幅')

    # @property
    # def status_verbose(self):
    #     d = dict(self.TICKET_TYPES)
    #     return d[self.status] if self.status in d else None

    def __unicode__(self):
        d = dict(INCREASE_TYPES)
        res = u'%s上涨，每次百分之%s' % (
            d[self.department.increase_type], self.increase * 100)
        return res


class NatureRecord(models.Model):

    """docstring for NatureRecord"""
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    target = models.ForeignKey(
        Staff, related_name='my_nature_records', verbose_name=u'作用对象')
    past_point = models.IntegerField(u'原贡献点', blank=True, null=True)
    point_change = models.IntegerField(u'贡献点变动', blank=True, null=True)
    remark = models.TextField(u'备注')

    class Meta:
        ordering = ["create_time"]

    def __unicode__(self):
        return self.remark

    def save(self, *args, **kwargs):
        is_first = False
        if not self.id:
            is_first = True
        remark = u'【%s】贡献点从【%s】点增加到【%s】点，增加【%s】点，增幅约【%.2f%%】' % (
            self.target, self.past_point, self.past_point + self.point_change, self.point_change, float(self.point_change * 100) / self.past_point)
        self.remark = remark
        super(NatureRecord, self).save(*args, **kwargs)
        if is_first:
            staff = self.target
            staff.current_point = self.past_point + self.point_change
            staff.save()
            PointRecord.objects.create(
                record_type=1, target=staff, nature_record=self)


class HandRecord(models.Model):
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    finish_time = models.DateTimeField(u'结算时间', blank=True, null=True)
    last_change_time = models.DateTimeField(u'最近修改时间', auto_now=True)
    target = models.ForeignKey(
        Staff, related_name='my_hand_records', verbose_name=u'作用对象')
    creator = models.ForeignKey(
        Staff, related_name='created_hand_records', verbose_name=u'创建者')
    holder = models.ForeignKey(
        Staff, related_name='processing_hand_records', verbose_name=u'责任人')
    history_holders = models.ManyToManyField(
        Staff, related_name='processed_handrecords', verbose_name=u'历史责任人')
    expect_end = models.DateField(u'预计实现日期')
    expect_notice = models.DateField(u'开始通知日期')
    RECORD_STATUS = (
        (1, u'尚未处理'),
        (2, u'处理完成'),
    )
    status = models.SmallIntegerField(u'状态', choices=RECORD_STATUS, default=1)
    CHANGE_TYPES = (
        (1, u'贡献点'),
        (2, u'贡献增幅'),
    )
    change_type = models.SmallIntegerField(
        u'变动内容', choices=CHANGE_TYPES, default=1)
    except_point_change = models.IntegerField(
        u'预计贡献点变动', blank=True, null=True)
    except_increase_change = models.FloatField(
        u'年贡献增幅变动', blank=True, null=True)
    past_point = models.IntegerField(u'原贡献点', blank=True, null=True)
    point_change = models.IntegerField(u'贡献点变动', blank=True, null=True)
    past_increase = models.FloatField(u'原年贡献增幅', blank=True, null=True)
    increase_change = models.FloatField(u'年贡献增幅变动', blank=True, null=True)
    remark = models.TextField(u'备注')

    class Meta:
        ordering = ["create_time"]

    @property
    def change_type_verbose(self):
        d = dict(self.CHANGE_TYPES)
        return d[self.change_type] if self.change_type in d else None

    @property
    def status_verbose(self):
        d = dict(self.RECORD_STATUS)
        return d[self.status] if self.status in d else None

    @property
    def expect_change(self):
        res = ''
        if self.change_type == 1:
            if self.except_point_change > 0:
                res = u'预计在【%s】增加【%s】点贡献点' % (
                    self.expect_end, self.except_point_change)
            elif self.except_point_change < 0:
                res = u'预计在【%s】消减【%s】点贡献点' % (
                    self.expect_end, abs(self.except_point_change))
            else:
                res = u'贡献点增幅预期值为0'
        else:
            if self.except_increase_change > 0:
                res = u'预计在【%s】增加【%s%%】年贡献增幅' % (
                    self.expect_end, self.except_increase_change)
            elif self.except_increase_change < 0:
                res = u'预计在【%s】消减【%s%%】年贡献增幅' % (
                    self.expect_end, abs(self.except_increase_change))
            else:
                res = u'贡献度增幅期值为0'
        return res

    @property
    def real_change(self):
        res = u'尚未完结'
        if self.status == 2:
            if self.change_type == 1:
                if self.point_change > 0:
                    res = u'在【%s】增加【%s】点贡献点，贡献点从【%s】点变为【%s】点' % (self.finish_time.strftime(
                        "%Y-%m-%d %H:%m"), self.point_change, self.past_point, self.past_point + self.point_change)
                elif self.point_change < 0:
                    res = u'在【%s】消减【%s】点贡献点，贡献点从【%s】点变为【%s】点' % (self.finish_time.strftime(
                        "%Y-%m-%d %H:%m"), abs(self.point_change), self.past_point, self.past_point + self.point_change)
                else:
                    res = u'贡献点未改动'
            else:
                if self.increase_change > 0:
                    res = u'在【%s】增加【%s%%】年贡献增幅,年贡献增幅从【%s%%】变为【%s%%】' % (self.finish_time.strftime(
                        "%Y-%m-%d %H:%m"), self.increase_change, self.past_increase, self.past_increase + self.increase_change)
                elif self.increase_change < 0:
                    res = u'在【%s】消减【%s%%】年贡献增幅,年贡献增幅从【%s%%】变为【%s%%】' % (self.finish_time.strftime(
                        "%Y-%m-%d %H:%m"), abs(self.increase_change), self.past_increase, self.past_increase + self.increase_change)
                else:
                    res = u'年贡献增幅未改动'
        return res

    def __unicode__(self):
        return u'贡献操作记录【%s】' % self.id

    def save(self, *args, **kwargs):
        completing = False
        if self.status == 2:
            if not self.finish_time:
                completing = True
        if completing:
            self.finish_time = datetime.datetime.now()
            if self.change_type == 1:
                self.past_point = self.target.current_point
            else:
                self.past_increase = self.target.staffset.increase
        super(HandRecord, self).save(*args, **kwargs)
        if not self.holder in self.history_holders.all():
            self.history_holders.add(self.holder)
        if completing:
            staff = self.target
            if self.change_type == 1:
                staff.current_point = staff.current_point + self.point_change
                staff.save()
                PointRecord.objects.create(
                    record_type=2, target=staff, hand_record=self)
            else:
                staffset = staff.staffset
                staffset.increase = staffset.increase + self.increase_change
                staffset.save()


class HandRecordHistory(models.Model):
    time = models.DateTimeField(u'创建时间', auto_now_add=True)
    handrecord = models.ForeignKey(HandRecord, verbose_name=u'对应修改记录')
    operator = models.ForeignKey(Staff, verbose_name=u'操作者')
    remark = models.TextField(u'备注')


class FootRecord(models.Model):
    FOOT_TYPES = (
        (1, u'开始体验level'),
        (2, u'添加第一个部门'),
        (3, u'添加第一个员工'),
        (4, u'第一次增加贡献'),
        (5, u'第一次扣除贡献'),
        (6, u'公司总体贡献点增长30%'),
        (7, u'公司总体贡献点增长50%'),
        (8, u'公司总体贡献点增长80%'),
        (9, u'公司总体贡献点增长100%'),
    )
    foot_type = models.SmallIntegerField(u'足迹类型', choices=FOOT_TYPES)
    target = models.ForeignKey(
        Staff, verbose_name=u'当事人', related_name='my_foot_records')
    time = models.DateTimeField(u'发生时间', auto_now_add=True)
    department = models.ForeignKey(
        Department, verbose_name=u'对应部门', blank=True, null=True)
    staff = models.ForeignKey(
        Staff, verbose_name=u'对应员工', related_name='related_foot_records', blank=True, null=True)

    @property
    def foot_type_verbose(self):
        d = dict(self.FOOT_TYPES)
        return d[self.foot_type] if self.foot_type in d else None


class PointRecord(models.Model):
    RECORD_TYPES = (
        (1, u'自然变动'),
        (2, u'人为点数变动'),
        (3, u'人为幅度变动'),
    )
    record_type = models.SmallIntegerField(u'记录类型', choices=RECORD_TYPES)
    target = models.ForeignKey(Staff, verbose_name=u'当事人')
    time = models.DateTimeField(u'发生时间', auto_now_add=True)
    nature_record = models.OneToOneField(
        NatureRecord, verbose_name=u'对应自然变动', blank=True, null=True)
    hand_record = models.OneToOneField(
        HandRecord, verbose_name=u'对应人为变动', blank=True, null=True)

    @property
    def record_type_verbose(self):
        d = dict(self.RECORD_TYPES)
        return d[self.record_type] if self.record_type in d else None

    @property
    def old_point(self):
        if self.record_type == 1:
            return self.nature_record.past_point
        elif self.record_type == 2:
            return self.hand_record.past_point
        else:
            return ''

    @property
    def new_point(self):
        if self.record_type == 1:
            return self.nature_record.past_point + self.nature_record.point_change
        elif self.record_type == 2:
            return self.hand_record.past_point + self.hand_record.point_change
        else:
            return ''

    @property
    def point_change(self):
        if self.record_type == 1:
            return self.nature_record.point_change
        elif self.record_type == 2:
            return self.hand_record.point_change
        else:
            return ''


class LoginHistory(models.Model):

    """docstring for LoginHistory"""
    time = models.DateTimeField(u'登录时间', auto_now_add=True)
    account = models.ForeignKey(Account, verbose_name=u'登录账号')
    is_login = models.BooleanField(u'登录还是登出', default=True)
    ip = models.GenericIPAddressField(u'登录IP')
    port = models.IntegerField(u'访客端口号', default=0)
    user_agent = models.CharField(u'代理标识', max_length=256, default=u'未知')
    is_first = models.BooleanField(u'是否首次登陆', default=False)
