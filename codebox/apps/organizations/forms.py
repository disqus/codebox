import re

from flask import current_app as app
from flaskext.wtf import Form, TextField, Required, SelectField
from codebox.apps.organizations.models import Organization
from codebox.apps.snippets.models import Snippet
from wtforms.validators import ValidationError

domain_re = re.compile(r'^([a-z0-9]([-a-z0-9]*[a-z0-9])?\\.)+((a[cdefgilmnoqrstuwxz]|aero|arpa)|(b[abdefghijmnorstvwyz]|biz)|(c[acdfghiklmnorsuvxyz]|cat|com|coop)|d[ejkmoz]|(e[ceghrstu]|edu)|f[ijkmor]|(g[abdefghilmnpqrstuwy]|gov)|h[kmnrtu]|(i[delmnoqrst]|info|int)|(j[emop]|jobs)|k[eghimnprwyz]|l[abcikrstuvy]|(m[acdghklmnopqrstuvwxyz]|mil|mobi|museum)|(n[acefgilopruz]|name|net)|(om|org)|(p[aefghklmnrstwy]|pro)|qa|r[eouw]|s[abcdeghijklmnortvyz]|(t[cdfghjklmnoprtvwz]|travel)|u[agkmsyz]|v[aceginu]|w[fs]|y[etu]|z[amw])$', re.I)

class IsValidDomain(object):
    def __call__(self, form, field):
        if not field.data:
            return

        if not domain_re.match(field.data):
            raise ValidationError('The domain you entered is not valid.')

        if field.data in app.config['DOMAIN_BLACKLIST']:
            raise ValidationError('You cannot register that domain.')

        if Organization.objects.index_exists('domain', field.data):
            raise ValidationError('That domain has already been registered.')

class NewOrganizationForm(Form):
    name = TextField('Organization Name', validators=[Required()])
    lang = SelectField('Default Language', choices=Snippet.languages, validators=[Required()])
    domain = TextField('Email Domain (Optional)', validators=[IsValidDomain()])