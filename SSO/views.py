# coding=utf-8

import urlparse
from django.shortcuts import render_to_response, resolve_url
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import base36_to_int, is_safe_url
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.middleware.csrf import rotate_token
from django.contrib.sites.models import get_current_site
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from .forms import TicketAuthenticationForm
from .models import Ticket
from kpi.models import LoginHistory
from Utils.functions import ErrorDic2str
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from Utils.http import json_response
from django.template import RequestContext
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import User
from SSO.forms import AccountSettingForm

logger = logging.getLogger(__name__)

def secure_required(view_func):
    """Decorator makes sure URL is accessed over https."""
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.is_secure():
            if getattr(settings, 'HTTPS_SUPPORT', True):
                request_url = request.build_absolute_uri(request.get_full_path())
                secure_url = request_url.replace('http://', 'https://')
                return HttpResponseRedirect(secure_url)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

@sensitive_post_parameters()
@never_cache
@csrf_exempt
def login(request, template_name='registration/login.html',
                    redirect_field_name=REDIRECT_FIELD_NAME):
    redirect_to = request.REQUEST.get(redirect_field_name, '/')
    error = ''
    if request.method == 'POST':
        form = TicketAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            #if not is_safe_url(url=redirect_to, host=request.get_host()):
                #redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            rotate_token(request)
            user=form.get_user()
            account=user.account
            if account.default_url:
                redirect_to = account.default_url
            else:
                redirect_to = ''
            # is_credit=False
            # try:
            #     if user.credit_account:
            #         is_credit=True
            # except:
            #     pass
            # if is_credit:
            #     redirect_to = '/credit/'
            # else:
            #     if not set(form.get_user().account.role_list) & set([1,3,8,9,10,11,18,12,15,16,17,22,6,5,4]):
            #         redirect_to = '/old/'
            #         #if 13 in form.get_user().account.role_list:
            #             #redirect_to = '/purchase_view/'
            
            response = HttpResponseRedirect(redirect_to)
            response.set_cookie('ticket', form.cleaned_data['ticket'])
            if request.META.has_key('HTTP_X_FORWARDED_FOR'):    
                ip =    request.META['HTTP_X_FORWARDED_FOR']    
            else:    
                ip = request.META['REMOTE_ADDR']                
            ua=request.META.get('HTTP_USER_AGENT','')
            LoginHistory.objects.create(account=form.get_user().account,ip=ip,user_agent=ua)
            return response
        else:
            error = u'请输入正确的用户名和密码'
        
    current_site = get_current_site(request)
    context = {
        'error':error,
        redirect_field_name: redirect_to,
        'site':current_site,
        'site_name':current_site.name,
    }
    return TemplateResponse(request, template_name, context)


def logout(request, next_page=None,
                     template_name='registration/login.html',
                     redirect_field_name=REDIRECT_FIELD_NAME,
                     current_app=None, extra_context=None):
    user = getattr(request, 'user', None)
    is_credit=False
    try:
        if user.credit_account:
            is_credit=True
    except:
        pass
    Ticket.objects.consume_tickets(request.user)
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):    
        ip =    request.META['HTTP_X_FORWARDED_FOR']    
    else:    
        ip = request.META['REMOTE_ADDR']
    ua=request.META.get('HTTP_USER_AGENT',None)
    if not is_credit:
        LoginHistory.objects.create(account=request.user.account,ip=ip,is_login=False,user_agent=ua) 
    if hasattr(user, 'is_authenticated') and not user.is_authenticated():
        user = None
    if hasattr(request, 'user'):
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()

    if next_page is not None:
        next_page = resolve_url(next_page)

    if redirect_field_name in request.REQUEST:
        next_page = request.REQUEST[redirect_field_name]
        # Security check -- don't allow redirection to a different host.
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    return HttpResponseRedirect('/login/')

@csrf_exempt
def account_setting(request):
    if request.method == 'POST':
        cds = json.loads(request.body)
        p = request.user.account.personinfo
        if p:
            f = AccountSettingForm(cds,instance=p)
        else:
            f = AccountSettingForm(cds)
        if not f.is_valid():
            return json_response({'code':1,"msg":ErrorDic2str(f.errors)})
        p = f.save()
        request.user.account.personinfo = p
        request.user.account.save() 
        return json_response({"code":0,"msg":"成功修改个人信息"})
    else:
        person = request.user.account.personinfo
        POSITIONS = Person.POSITIONS
        return render_to_response('registration/account_settings.html',{'person':person,'POSITIONS':POSITIONS},context_instance=RequestContext(request))

@csrf_exempt     
def change_password(request):
    if request.method == 'POST':
        msg=u'修改密码成功'
        code=0
        cds = request.POST
        print cds
        u = request.user
        old_pwd = cds.get('old_pwd', '')
        if u.check_password(old_pwd):
            pwd = cds.get('new_pwd', '')
            if len(pwd) < 6 or len(pwd) > 20:
                msg = u'密码长度应该为6到20位之间'
                code = 1
            if pwd == old_pwd:
                msg = u'新旧密码不能相同'
                code = 1
                
            pwd_rep = cds.get('new_pwd_rep','')
            if pwd != pwd_rep:
                msg = u'两次输入的密码不相同'
                code = 1              
        else:
            code = 1
            msg = u'原密码错误'
        if not code:
            u.set_password(pwd)
            u.save()
        return json_response({'code':code,'msg':msg})
    else:
        return render_to_response('registration/change_password.html',context_instance=RequestContext(request))
