from flaskext.wtf import Form, TextAreaField, Required

class NewSnippetForm(Form):
    text = TextAreaField('Snippet', validators=[Required()])