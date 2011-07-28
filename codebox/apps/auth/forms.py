from flaskext.wtf import Form, TextField, Required

class EditProfileForm(Form):
    name = TextField('Name', validators=[Required()])
