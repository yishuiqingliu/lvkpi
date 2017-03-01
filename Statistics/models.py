# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone
import datetime
import time

from kpi.models import *

class StaffDailyPoint(models.Model):
    target=models.ForeignKey(Staff,verbose_name=u'对应员工')
    date=models.DateField(u'记录时间',default=datetime.date.today())
    point=models.IntegerField(u'贡献点')

    class Meta:
        unique_together = (('date', 'target'),)

    def save(self, *args, **kwargs):
        if not self.id:
            if self.target:
                self.point = self.target.current_point
        super(StaffDailyPoint, self).save(*args, **kwargs)