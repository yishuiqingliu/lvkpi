# coding=utf-8

from datetime import timedelta
import logging
import time
import hashlib
import hmac
import random
import re

from django.conf import settings
from django.db.models import Q
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_bytes

from SSO.exception import *

logger = logging.getLogger(__name__)

def salted_hmac(key_salt, value, secret):
  key = hashlib.sha1((key_salt + secret).encode('utf-8')).digest()
  return hmac.new(key, msg=force_bytes(value), digestmod=hashlib.sha1)

def get_random_string(length=16,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
  return ''.join([random.choice(allowed_chars) for i in range(length)])

class TicketManager(models.Manager):
  def create_ticket(self, ticket=None, **kwargs):
    if not ticket:
      ticket = self.create_ticket_str()
    if 'expires' not in kwargs:
      expires = now() + timedelta(seconds=self.model.TICKET_EXPIRE)
      kwargs['expires'] = expires
      t = self.create(ticket=ticket, **kwargs)
      logger.debug("Created %s %s" % (t.name, t.ticket))
      return t

  def create_ticket_str(self, prefix=None):
    if not prefix:
      prefix = self.model.TICKET_PREFIX
    return "%s-%d-%s" % (prefix, int(time.time()),
                             get_random_string(length=self.model.TICKET_RAND_LEN))

  def validate_ticket(self, ticket, renew=False):
    if not ticket:
      raise InvalidRequest("No ticket string provided")

    if not self.model.TICKET_RE.match(ticket):
      raise InvalidTicket("Ticket string %s is invalid" % ticket)

    try:
      t = self.get(ticket=ticket)
    except self.model.DoesNotExist:
      raise InvalidTicket("Ticket string %s is invalid" % ticket)

    if t.is_consumed():
      raise InvalidTicket("%s %s has already been used" %
                          (t.name, ticket))
    #t.consume()

    if t.is_expired():
      raise InvalidTicket("%s %s has expired" % (t.name, ticket))
    logger.debug("Validated %s %s" % (t.name, ticket))
    return t

  def delete_invalid_tickets(self):
    for ticket in self.filter(Q(consumed__isnull=False) |
                               Q(expires__lte=now())):
      try:
        ticket.delete()
      except models.ProtectedError:
        pass

  def consume_tickets(self, user):
    logger.info(user.id)
    for ticket in self.filter(user=user, consumed__isnull=True,
                               expires__gt=now()):
      logger.info(ticket)
      ticket.consume()

  def request_sign_out(self, user):
    for ticket in self.filter(user=user, consumed__gte=user.last_login):
      ticket.request_sign_out()

class Ticket(models.Model):
  TICKET_PREFIX = "TK"
  #TICKET_EXPIRE = getattr(settings, 'SESSION_COOKIE_AGE')
  TICKET_EXPIRE = 60 * 60 * 24 * 5
  TICKET_RAND_LEN = 32
  TICKET_RE = re.compile("^[A-Z]{2,3}-[0-9]{10,}-[a-zA-Z0-9]{%d}$" %TICKET_RAND_LEN)

  ticket = models.CharField(_('ticket'), max_length=255, unique=True)
  user = models.ForeignKey(User, verbose_name=_('user'))
  expires = models.DateTimeField(_('expires'))
  consumed = models.DateTimeField(_('consumed'), null=True)

  objects = TicketManager()

  def __str__(self):
    return self.ticket

  def consume(self):
    self.consumed = now()
    self.save()

  @property
  def name(self):
      return self._meta.verbose_name

  def is_consumed(self):
    if self.consumed:
      return True
    return False

  def is_expired(self):
    return self.expires <= now()

  def request_sign_out(self):
    pass


