# coding=utf-8

from django.db.models import Model, Manager, DecimalField, SubfieldBase, smart_text
from django.core.validators import EMPTY_VALUES
from django.forms import ValidationError, Widget
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
import django.forms
import django.db.models
import re
from dateutil.tz import tzutc
from django.db.models.query import QuerySet  

UTC = tzutc()

def serialize_date(dt):
    """
    Serialize a date/time value into an ISO8601 text representation
    adjusted (if needed) to UTC timezone.

    For instance:
    >>> serialize_date(datetime(2012, 4, 10, 22, 38, 20, 604391))
    '2012-04-10T22:38:20.604391'
    """
    if dt.tzinfo:
        dt = dt.astimezone(UTC).replace(tzinfo=None)
    return dt.isoformat()
#def model_to_dict(m):
#  d = django.forms.model_to_dict(m)
#  return {k:d[k] for k in d if d[k] and d[k] != ''}

class SpanWidget(Widget):
  def render(self, name, value, attrs=None):
    final_attrs = self.build_attrs(attrs, name=name)
    return mark_safe(u'<span%s >%s</span>' % (django.forms.util.flatatt(final_attrs), self.original_value))
  def value_from_datadict(self, data, files, name):
    return self.original_value

class SpanField(django.forms.Field):
  def __init__(self, *args, **kwargs):
    kwargs['widget'] = kwargs.get('widget', SpanWidget)
    super(SpanField, self).__init__(*args, **kwargs)

class Readonly(object):
  class NewMeta:
    readonly = tuple()
    editable = tuple()

  def __init__(self, *args, **kwargs):
    super(Readonly, self).__init__(*args, **kwargs)
    readonly = self.NewMeta.readonly
    editable = self.NewMeta.editable
    if not readonly and not editable:
      return
    if editable:
      for name, field in self.fields.items():
        if name not in editable:
          field.widget = SpanWidget()
        elif not isinstance(field, SpanField):
          continue
        field.widget.original_value = unicode(getattr(self.instance, name))
      return
    for name, field in self.fields.items():
      if name in readonly:
        field.widget = SpanWidget()
      elif not isinstance(field, SpanField):
        continue
      field.widget.original_value = str(getattr(self.instance, name))

class BaseModel(Model):
  class Meta: abstract = True
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

phone_digits_re = re.compile(r'[\d-]{8,15}')

class CNPhoneNumberField(django.forms.CharField):
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

class PhoneNumberField(django.db.models.CharField):
    description = _("Phone number")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 20
        super(PhoneNumberField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'form_class': CNPhoneNumberField}
        defaults.update(kwargs)
        return super(PhoneNumberField, self).formfield(**defaults)
    


class ChildQuerySet(QuerySet):  
    def iterator(self):  
        for obj in super(ChildQuerySet, self).iterator():  
            yield obj.get_child_object()  
    
class ChildManager(django.db.models.Manager):  
    def get_query_set(self):  
        return ChildQuerySet(self.model)  
    
def QueryGet(model,filter):
    queryset = model.filter(**filter)
    if queryset.exists():
        return queryset[0]
    else:
        return None
    