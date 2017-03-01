# coding=utf-8
import re
from decimal import Decimal
from django.db.models import Model, Manager, DecimalField, SubfieldBase
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from django.core.validators import EMPTY_VALUES
from django.forms import CharField, ValidationError
from django.db import models
import base64

from django import forms
from django.utils.text import capfirst
from django.core import exceptions

phone_digits_re = re.compile(r'[\d-]{8,15}')

class Base64Field(models.TextField):

    def contribute_to_class(self, cls, name):
        if self.db_column is None:
            self.db_column = name
        self.field_name = name + '_base64'
        super(Base64Field, self).contribute_to_class(cls, self.field_name)
        setattr(cls, name, property(self.get_data, self.set_data))

    def get_data(self, obj):
        return base64.decodestring(getattr(obj, self.field_name))

    def set_data(self, obj, data):
        setattr(obj, self.field_name, base64.encodestring(data))

class CNPhoneNumberField(CharField):
  default_error_messages = {
    'invalid': _('Phone numbers must only contain digit and -.'),
  }

  def clean(self, value):
    super(CNPhoneNumberField, self).clean(value)
    if value in EMPTY_VALUES or value[0] in EMPTY_VALUES:
      return ''
    value = re.sub('(\(|\)|\s+)', '', smart_text(value))
    m = phone_digits_re.search(value)
    if m:
      return '%s' % (m.group(0))
    raise ValidationError(self.error_messages['invalid'])

class BaseModel(Model):
  class Meta:
    abstract = True
  obj = objects = Manager()

  def update(self, **kwargs):
    for k, v in kwargs.items():
      setattr(self, k, v)
    self.save()

class CurrencyField(DecimalField):
  __metaclass__ = SubfieldBase
  def to_python(self, value):
    try:
      return super(CurrencyField, self).to_python(value).quantize(Decimal('0.01'))
    except AttributeError:
      return None

class PhoneNumberField(models.CharField):
    description = _("Phone number")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 20
        super(PhoneNumberField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': CNPhoneNumberField}
        defaults.update(kwargs)
        return super(PhoneNumberField, self).formfield(**defaults)

class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)
    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        # if value and self.max_choices and len(value) > self.max_choices:
        #     raise forms.ValidationError('You must select a maximum of %s choice%s.'
        #             % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value

class MultiSelectField(models.Field):
    __metaclass__ = models.SubfieldBase
    def get_internal_type(self):
        return "CharField"
    def get_choices_default(self):
        return self.get_choices(include_blank=False)
    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        choicedict = dict(field.choices)
    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank, 'label': capfirst(self.verbose_name),
                    'help_text': self.help_text, 'choices': self.choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)
    def get_prep_value(self, value):
        return value
    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            result=''
            for item in value:
                if result:
                    result='%s,%s' % (result,item)
                else:
                    result='%s' % item
            return result
    def to_python(self, value):
        array=[]
        if value:
            temp_array=value if isinstance(value, list) else value.split(',')
            for item in temp_array:
                if isinstance(item, int):
                    array.append(item)
                else:
                    if item.isdigit():
                        array.append(int(item))
                    else:
                        array.append(item)
        return array
    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname = name, choicedict = dict(self.choices): ",".join([choicedict.get(value, value) for value in getattr(self, fieldname)])
            setattr(cls, 'get_%s_display' % self.name, func)
    def validate(self, value, model_instance):
        arr_choices = self.get_choices_selected(self.get_choices_default())
        for opt_select in value:
            if (int(opt_select) not in arr_choices):  # the int() here is for comparing with integer choices
                raise exceptions.ValidationError(self.error_messages[u'无效值'])
        return
    def get_choices_selected(self, arr_choices=''):
        if not arr_choices:
            return False
        list = []
        for choice_selected in arr_choices:
            list.append(choice_selected[0])
        return list
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
    
    
# class ParentModel(models.Model):
#     _child_name = models.CharField(max_length=100, editable=False)  
  
#     class Meta:  
#         abstract = True  
  
#     def save(self, *args, **kwargs):  
#         self._child_name = self.get_child_name()  
#         super(ParentModel, self).save(*args, **kwargs)  
  
#     def get_child_name(self):  
#         if type(self) is self.get_parent_model():  
#             return self._child_name  
#         return self.get_parent_link().related_query_name()  
  
#     def get_child_object(self):  
#         return getattr(self, self.get_child_name())  
  
#     def get_parent_link(self):  
#         return self._meta.parents[self.get_parent_model()]  
  
#     def get_parent_model(self):  
#         raise NotImplementedError  
  
#     def get_parent_object(self):  
#         return getattr(self, self.get_parent_link().name)  