from codesharer.utils import yammer


YAMMER_KEY = 'kZO991WvBUdApnD6f7g'
YAMMER_SECRET = 'lNLCt5bCQDEXikioA2nhgbIyHln1C6qgON7TdyZA'

class CodeBoxYammer(objects):

    def __init__(self):
        self.yammer = yammer.Yammer(YAMMER_KEY, YAMMER_SECRET)

    def get_auth_url(self):
        return self.yammer.get_authorize_url()
