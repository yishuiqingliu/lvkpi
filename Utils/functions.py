#coding:utf-8
from django.db.models.loading import get_model
import re
import datetime
from functools import wraps
from django.db.models import Q
from dateutil import tz
from django.http.response import HttpResponse

def require_permission(permission_id):
    def decorator(func):
        @wraps(func)
        def returned_wrapper(request, *args, **kwargs):
            # try:
            if request.user.account.roles.filter(permissions__permission_id=permission_id).exists():
                return func(request, *args, **kwargs)
            else:
                return HttpResponse(u'没有当前操作权限')
        return returned_wrapper
    return decorator


def getmodelfield(appname,modelname):
    modelobj = get_model(appname,modelname)
    fielddic={}
    for field in modelobj._meta.fields:
        fielddic[field.name] = field.verbose_name
        #print '字段类型:',type(field).__name__        #返回的是‘charfield’,'textfield',等这些类型
    return fielddic

def ErrorDic2str(dic):
    res_list = []
    for key in dic.keys():
        res_list.append('%s%s'%(key,dic[key].as_text()))
                        
    return '\n'.join(res_list)

def getChanges(old,new,app_name='api'):
    changes = []
    model_name = old._meta.object_name
    veborse_dic = getmodelfield(app_name,model_name)
    for key in veborse_dic:
        if key == 'last_change_time':
            continue
            
        op = getattr(old, key)
        np = getattr(new, key)
        if not op and not np:
            continue
        if isinstance(np,datetime.datetime):
            tz = np.tzinfo
            if isinstance(op,datetime.datetime):
                if not np.tzinfo:
                    op = op.strftime("%Y年%m月%d日 %H点%M分")
                else:
                    op = op.astimezone(tz).strftime("%Y年%m月%d日 %H点%M分")
            else:
                op = ''
            np = np.strftime("%Y年%m月%d日 %H点%M分")
        if isinstance(np,datetime.date):
            np = np.strftime("%Y年%m月%d日")
        if isinstance(op,datetime.date):
            try:
                op = op.strftime("%Y年%m月%d日")
            except ValueError as e:
                op = ''
        if op != np:
            if str(type(op)) == "<class 'decimal.Decimal'>":
                if float(op) == np:
                    continue
            ver = veborse_dic[key]
            
            if isinstance(veborse_dic[key], unicode):
                ver = ver.encode('utf-8')
    
            if isinstance(op, unicode):
                op = op.encode('utf-8')
            
            if isinstance(np, unicode):
                np = np.encode('utf-8')
                
            if not np:
                np = ''
            if not op:
                op = ''
            try:
                    changes.append("【%s】 从 【%s】 改为 【%s】"%(ver,op,np))
            except:
                pass
    return ";".join(changes).decode('utf-8')

def QueryFilter(QueryList,**q):
    if not QueryList:
        return QueryList
    cds = q
    union_set=None
    if cds.has_key('union_set'):
        union_set=cds.pop('union_set')
    field_dic = QueryList[0]._meta.get_all_field_names()
    for key in cds.keys():
        if not key in field_dic and not key.split('__')[0] in field_dic and not key.replace('_id','') in field_dic:
            cds.pop(key)
            continue
        if re.findall(r'__[gl]te??$',key):
            if cds.get(key) and cds[key].isdigit():
                    cds[key] = datetime.datetime.fromtimestamp(int(cds[key]))
        if re.findall(r'_id$',key):
            if not cds[key].isdigit():
                cds.pop(key)
    NewQuery=QueryList.filter(**cds)
    if union_set:
        Query=QueryList.none()
        for key in union_set.keys():
            if re.findall(r'__[gl]te??$',key):
                if union_set.get(key) and union_set[key].isdigit():
                    union_set[key] = datetime.datetime.fromtimestamp(int(union_set[key]))
        NewQuery=NewQuery|QueryList.filter(**{key:union_set[key]})
    return NewQuery


def QueryDict2Dict(**kwrags):
    get_dic= kwrags
    cds = {}
    for k in get_dic:
        if len(get_dic[k]) > 1:
            cds[k] = get_dic[k]
        elif len(get_dic[k]) == 1:
            cds[k] = get_dic[k][0]
        else:
            pass    
    return cds