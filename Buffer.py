### This class implements a buffer view that is consumable. (For now no considerations for performance and memory usage were made. Copies are made everywhere.)

class Buffer(object):
    def __init__(self, content, cursor=0):
        self.content = content
        self.cursor = cursor

        assert len(self.content) > self.cursor

    def __getitem__(self, index):
        if index >= 0 and index < len(self.content):
            return self.content[index]

    def create_view(self):
        return Buffer(self.content[self.cursor:])

    def look(self, n=0):
        return self.__getitem__(n+self.cursor)

    def lookahead(self, n=1):
        return self.__getitem__(n+self.cursor)

    def __len__(self):
        return len(self.content)-self.cursor

    def matches(self, value):
        if self.look() == value:
            return True

    def pop(self):
        value = self.look()
        if len(self):
            self.cursor += 1
        return value

    def match(self, value):
        if self.look() == value:
            return self.pop()

    def fmatch(self, f):
        if f(self.look()):
            return self.pop()

    def consume(self, n=1):
        buffer = []
        for i in range(n):
            v = self.pop()
            if v is not None:
                buffer.append(v)
        return buffer

    def consume_while(self, f):
        buffer = []
        while self.look() is not None and f(self.look()):
            buffer.append(self.pop())
        return buffer

    def consumed(self):
        return self.cursor

    def is_empty(self):
        return len(self) == 0

    def __str__(self):
        return f"{self.content[self.cursor:]}"