from flaskext.wtf import Form, TextField, Required

class NewAuthForm(Form):
    text = TextField('Code', validators=[Required()])
