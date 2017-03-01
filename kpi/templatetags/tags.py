# coding=utf-8

from django import template
import os
from django.core.cache import cache
from lvkpi.settings import BASE_DIR
register = template.Library()

@register.simple_tag
def field_value(field):
    """ returns field value """
    if type(field.value()) == list:
      return field.value()[0]
    return field.value()

@register.filter 
def file_time_stamp(value):
    if value.startswith("/static"):
        fn = os.path.join(BASE_DIR,value[1:].replace("/", os.sep))
        if os.path.isfile(fn):
            ts = os.stat(fn).st_mtime
            sp = "?" if "?" not in value else "&"
            value = "%s%sv=%.1f" % (value, sp, ts)
    return value