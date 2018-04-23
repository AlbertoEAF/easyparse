from easyparse.Buffer import Buffer

class Token(object):
    def __init__(self, TYPE, content=None, auto_discard=False):
        self.TYPE = TYPE
        self.content = content

        self._auto_discard = auto_discard

    def __repr__(self):
        if self.content is None:
            return f"{{{self.TYPE}}}"
        else:
            return f"{{{self.TYPE}|{self.content}}}"

    def set_auto_discard(self, value):
        self._auto_discard = value
    def get_auto_discard(self):
        return self._auto_discard


class Tokenizer(object):
    """ Returns the next token from the buffer or raises Tokenizer.NoMatch if it didn't match. Failing to validate(token) will yield InvalidTokenException. """

    class NoMatch(Exception): pass      # raised when there is no match for the input using this Tokenizer, OK.
    class InvalidTokenException(Exception): pass # raised when the generated token fails to pass validation. ERROR!

    def _tokenize(self, input_buffer):
        """ Do not override. Automatic tokenizer behaviour generated. """
        if not input_buffer.is_empty():
            token = self.tokenize(input_buffer)
            if not isinstance(token, Token):
                raise Tokenizer.NoMatch
            elif not self.validate(token):
                raise Tokenizer.InvalidTokenException
            else:
                return token
        else:
            return None

    def tokenize(self, input_buffer):
        """ Take the input_buffer and generate the next token if applicable. Must return a Token(TYPE,content) if all went well. """
        NotImplementedError

    def validate(self, token):
        """ Can be overriden. Should give True if the generated Token by tokenize(...) is valid. Can throw exceptions, such as Tokenizer.InvalidTokenException or your own. """
        return True


class Lexer(object):
    class IncompleteRuleSetException(Exception):
        def __init__(self, msg, max_range=100):
            super().__init__(f"Lexer has no rules to parse input at:\n{str(msg)[:max_range]}\n...")
    class NullTokenException(Exception): pass

    def __init__(self, tokenizers):
        self.tokenizers = tokenizers

    def _try_tokenizer(self, buffer, tokenizer):
        view = buffer.create_view()
        try:
            token = tokenizer._tokenize(view)
            if token is None:
                raise Lexer.NullTokenException
        except Tokenizer.NoMatch:
            return None
        buffer.consume(view.consumed())
        return token

    def parse(self, input_string):
        input_buffer = Buffer(input_string)
        tokens = []

        while not input_buffer.is_empty():
            token = None
            for tokenizer in self.tokenizers:
                token = self._try_tokenizer(input_buffer, tokenizer)
                if token:
                    if not token._auto_discard:
                        tokens.append(token)
                    break
            if token is None:
                raise Lexer.IncompleteRuleSetException(input_buffer)


        return tokens