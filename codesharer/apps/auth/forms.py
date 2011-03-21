from flaskext.wtf import Form, TextField, Required, PasswordField

class NewAuthForm(Form):
    text = TextField('Code', validators=[Required()])

class LoginForm(Form):
    username = TextField('Username')
    password = PasswordField('Password')
