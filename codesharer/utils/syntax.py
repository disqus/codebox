from pygments import highlight
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

def colorize(code):
    """
    Takes in code and returns pygmentized code.
    Attempts to guess insert.
    """

    # TODO: actually colorize
    return highlight(code, get_lexer_by_name('python'), HtmlFormatter(linenos='table'))
