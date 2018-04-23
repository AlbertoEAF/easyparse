from easyparse import Tokenizer, Token

def eq(value):
    return lambda x: x == value

def neq(value):
    return lambda x: x != value

def concatenate(list_object):
    return "".join(list_object)


class WhitespaceTokenizer(Tokenizer):
    def __init__(self, auto_discard):
        self.auto_discard = auto_discard
    def tokenize(self, view):
        buffer = view.consume_while(lambda x: x in (" ", "\t"))
        if buffer:
            return Token("Whitespace", auto_discard=self.auto_discard)


class IdentityTokenizer(Tokenizer):
    def tokenize(self, view):
        return view.pop()


class SingleTokenizer(Tokenizer):
    def __init__(self, TYPE, match_f=None, T=lambda x:x):
        self.TYPE = TYPE
        self.match_f = match_f if match_f is not None else eq(self.TYPE)
        self.T = T

    def tokenize(self, view):
        value = view.pop()
        if self.match_f(value):
            return Token(self.TYPE, self.T(value))

class CharTokenizer(SingleTokenizer):
    def __init__(self, TYPE):
        super().__init__(TYPE, eq(TYPE), lambda x: None)

class DiscardTokens(Tokenizer):
    def __init__(self, discard_f):
        self.discard_f = discard_f
    def tokenize(self, view):
        token = view.pop()
        if self.discard_f(token):
            token.set_auto_discard(True)
        return token