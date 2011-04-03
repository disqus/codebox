from flaskext.wtf import Form, TextField, TextAreaField, Required, SelectField
from codebox.apps.snippets.models import Snippet

class NewSnippetForm(Form):
    lang = SelectField('Language', choices=Snippet.languages, validators=[Required()])
    text = TextAreaField('Snippet', validators=[Required()])
    keywords = TextField('Keywords')