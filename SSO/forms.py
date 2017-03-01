# coding=utf-8
from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth import authenticate
from SSO.models import *
from kpi.models import Staff
from django.forms import ModelForm

logger = logging.getLogger(__name__)


class TicketAuthenticationForm(forms.Form):

    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254)
    password = forms.CharField(label=_(u"密码"), widget=forms.PasswordInput)
    ticket = forms.CharField(widget=forms.HiddenInput, required=False)

    error_messages = {
        'invalid_login': _(u"请输入正确的用户名和密码. "),
        'inactive': _(u"账号被锁定."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(TicketAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        ticket = self.cleaned_data.get('ticket')
        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            # if self.user_cache is None:
            #   try:
            #     person = Person.objects.get(phone1=username)
            #     if person.account_set:
            #       self.user_cache = authenticate(username=person.account.accountinfo.username, password=password)
            #   except:
            #     pass
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login'
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive'
                )
            t = Ticket.objects.create_ticket(user=self.user_cache)
            self.cleaned_data['ticket'] = t.ticket
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class AccountSettingForm(ModelForm):

    class Meta:
        model = Staff
        exclude = ['photo']
        error_messages = {
            'name': {
                'required': "没有输入姓名哦",
            },
            'gender': {
                'required': "你是男，是女还是啥？",
            }
        }
