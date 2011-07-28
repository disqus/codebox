from flaskext.wtf import Form, TextField, Required, BooleanField

class EditProfileForm(Form):
    name = TextField('Name', validators=[Required()])
    update_token = BooleanField('Create new API token')
