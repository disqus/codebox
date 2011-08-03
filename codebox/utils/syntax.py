"""
codebox.utils.syntax
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

def colorize(code, lang):
    """
    Takes in code and returns pygmentized code.
    Attempts to guess insert.
    """

    # TODO: actually colorize
    return highlight(code, get_lexer_by_name(lang), HtmlFormatter(linenos='table'))
