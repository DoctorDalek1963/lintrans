from pygments.lexer import RegexLexer
from pygments.token import Comment, Text

class SphObjInvTextLexer(RegexLexer):
    name = 'SphObjInvText'

    tokens = {
        'root': [
            (r'#.*\n', Comment),
            (r'.*\n', Text),
        ]
    }
