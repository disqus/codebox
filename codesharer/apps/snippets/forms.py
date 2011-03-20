from flaskext.wtf import Form, TextField, Required

class NewSnippetForm(Form):
    text = TextField('Snippet', validators=[Required()])