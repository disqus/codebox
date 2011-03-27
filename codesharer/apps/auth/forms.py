from flaskext.wtf import Form, TextField, Required, PasswordField

class EditProfileForm(Form):
    name = TextField('Name')
