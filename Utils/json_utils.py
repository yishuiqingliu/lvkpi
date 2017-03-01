# -*- coding=utf-8 -*-
import json
import datetime
from django.db.models.fields.files import ImageFieldFile
from decimal import Decimal
import time


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        #convert object to a dict
        d = {}
        d['__class__'] = obj.__class__.__name__
        d['__module__'] = obj.__module__
        d.update(obj.__dict__)
        return d


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(time.mktime(obj.timetuple()))
        if isinstance(obj, datetime.date):
            return int(time.mktime(obj.timetuple()))
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj,unicode):
            obj = obj.encode('utf-8')
            return obj
        if isinstance(obj,bool):
            return 1 if obj else 0
            
        if isinstance(obj, ImageFieldFile):
            try:
                return obj.path
            except ValueError:
                return ''
        return json.JSONEncoder.default(self, obj)