from flaskext.wtf import Form, TextAreaField, Required, SelectField

class NewSnippetForm(Form):
    lang = SelectField('Language', choices=[
        ('python', 'Python'),
        ('ruby', 'Ruby'),
        ('javascript', 'JavaScript'),
        ('html', 'HTML'),
    ], validators=[Required()])
    text = TextAreaField('Snippet', validators=[Required()])