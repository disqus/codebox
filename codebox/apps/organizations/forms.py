import re

from flask import current_app as app
from flaskext.wtf import Form, TextField, TextAreaField, Required, SelectField
from codebox.apps.organizations.models import Organization
from codebox.apps.snippets.models import Snippet
from wtforms.validators import ValidationError

domain_re = re.compile(r'^([a-z0-9]([\-a-z0-9]*[a-z0-9])?\.)+((a[cdefgilmnoqrstuwxz]|aero|arpa)|(b[abdefghijmnorstvwyz]|biz)|(c[acdfghiklmnorsuvxyz]|cat|com|coop)|d[ejkmoz]|(e[ceghrstu]|edu)|f[ijkmor]|(g[abdefghilmnpqrstuwy]|gov)|h[kmnrtu]|(i[delmnoqrst]|info|int)|(j[emop]|jobs)|k[eghimnprwyz]|l[abcikrstuvy]|(m[acdghklmnopqrstuvwxyz]|mil|mobi|museum)|(n[acefgilopruz]|name|net)|(om|org)|(p[aefghklmnrstwy]|pro)|qa|r[eouw]|s[abcdeghijklmnortvyz]|(t[cdfghjklmnoprtvwz]|travel)|u[agkmsyz]|v[aceginu]|w[fs]|y[etu]|z[amw])$', re.I)
email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.I)  # domain

class IsValidDomain(object):
    def __call__(self, form, field):
        if not field.data:
            return

        if not domain_re.match(field.data):
            raise ValidationError('The domain you entered is not valid.')

        if field.data in app.config['DOMAIN_BLACKLIST']:
            raise ValidationError('You cannot register that domain.')

        if Organization.objects.exists(domain=field.data):
            raise ValidationError('That domain has already been registered.')

class IsValidEmailList(object):
    def __call__(self, form, field):
        if not field.data:
            return
        
        email_list = [e.strip() for e in field.data.split('\n')]
        for email in email_list:
            if not email_re.match(email):
                raise ValidationError('The email you entered, \'%s\' is not valid.' % email)

class NewOrganizationForm(Form):
    name = TextField('Organization Name', validators=[Required()])
    lang = SelectField('Default Language', choices=Snippet.languages, validators=[Required()])
    domain = TextField('Email Domain (Optional)', validators=[IsValidDomain()])

class VerifyDomainForm(Form):
    email_username = TextField('Email', validators=[Required()])

class InviteUserForm(Form):
    email_list = TextAreaField('Email', validators=[IsValidEmailList()])