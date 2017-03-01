# coding=utf-8

import logging
from django.contrib.admin.widgets import AdminDateWidget
from datetimewidget.widgets import DateTimeWidget
from django.forms.fields import DateField, DateTimeField,ImageField,FileField
from django.forms import  Field, Widget, ModelForm
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
import autocomplete_light

logger = logging.getLogger(__name__)

class SpanWidget(Widget):
  def render(self, name, value, attrs=None):
    final_attrs = self.build_attrs(attrs, name=name)
    return mark_safe(u'<span %s>%s</span>' % (flatatt(final_attrs), self.display_value))
  #def value_from_datadict(self, data, files, name):
    #return self.original_value

class SpanField(Field):
  def __init__(self, *args, **kwargs):
    kwargs['widget'] = kwargs.get('widget', SpanWidget)
    super(SpanField, self).__init__(*args, **kwargs)

class ReadonlyModelForm(autocomplete_light.ModelForm):
  editable = set()
  required = set()
  def __init__(self, *args, **kwargs):
    self.editable = kwargs.pop('editable', self.editable)
    self.required = kwargs.pop('required', self.required)
    super(ReadonlyModelForm, self).__init__(*args, **kwargs)
    func = lambda x : x not in self.editable
    for name, field in self.fields.items():
      if func(name):
        if not isinstance(field, ImageField) and not isinstance(field, FileField):
          field.widget = SpanWidget()
      elif not isinstance(field, SpanField):
        if isinstance(field, DateField):
          field.widget = AdminDateWidget()
        elif isinstance(field, DateTimeField):
          field.widget = DateTimeWidget(usel10n=True, attrs={})
        if name in self.required:
          field.required = True
        continue
      if hasattr(self.instance, name) and getattr(self.instance, name) != None:
        if hasattr(self.instance, name+'_verbose'):
          value = getattr(self.instance, name+'_verbose')
          if isinstance(value,str):
              value = value.decode('utf-8')
          field.widget.display_value = value if value else ''
        else:
          #print type(getattr(self.instance, name))
          v = getattr(self.instance, name)
          if isinstance(v,str):
              v = v.decode('utf-8')
          field.widget.display_value = v
      else:
        field.widget.display_value = ""