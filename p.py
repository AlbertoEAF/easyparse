import easyparse as ep
import easyparse.tokenizers as epts

def eq(value):
    return lambda x: x == value

def neq(value):
    return lambda x: x != value

def concatenate(list_object):
    return "".join(list_object)

class WordTokenizer(ep.Tokenizer):
    def __init__(self, extra_chars=()):
        self.extra_chars = extra_chars
    def tokenize(self, view):
        buffer = view.consume_while(lambda x: x.isalnum() or x in self.extra_chars)
        if buffer:
            return ep.Token("WORD", concatenate(buffer))

class PropertyTokenizer(ep.Tokenizer):
    def tokenize(self, view):
        buffer = view.consume_while(lambda x: x.TYPE == "WORD")
        if buffer:
            return ep.Token("Property", [ token.content for token in buffer ])



rpp_lexer = ep.Lexer([
    WordTokenizer(extra_chars=("_","-",".", "/","\"", "{", "}")),
    epts.WhitespaceTokenizer(auto_discard=True),
    epts.SingleTokenizer("NEWLINE", eq("\n"), lambda x:None),
    ] + [ epts.CharTokenizer(char) for char in ["<", ">"] ])

rpp_lexer_stage2 = ep.Lexer([
    PropertyTokenizer(),
    epts.DiscardTokens(lambda token: token.TYPE == "NEWLINE"),
    epts.IdentityTokenizer()])


class ReaperNode(object):
    def __init__(self, node):
        node = ep.DeepTreeNode(node)

        parse_property_token = lambda token: { token.content[0] : token.content[1:] }

        if node.properties:
            header = node.properties[0].content
            self.name = header[0 ]
            self.args = header[1:]
        else:
            self.name = ""
            self.params = []

        self.properties = { p.content[0] : p.content[1:] for p in node.properties[1:] }
        self.children = [ ReaperNode(child) for child in node.children ]

    def __repr__(self):
        return f"ReaperNode({self.name}{self.args}, properties={self.properties}, children = {self.children})\n"

def filter_tree(tree_node, filter_f):
    nodes = []

    if filter_f(tree_node):
        nodes.append(tree_node)

    for child in tree_node.children:
        nodes.extend(filter_tree(child, filter_f))

    return nodes


class RPP(object):
    def __init__(self, rpp_filepath):
        self.filepath = rpp_filepath
        self.rpp_content = open(self.filepath).read()



phrase = open(r"C:\Users\AlbertoEAF\Desktop\teste\\teste.rpp").read()
tokens = rpp_lexer.parse(phrase)
tokens2 = rpp_lexer_stage2.parse(tokens)
tree_maker = ep.TreeMaker(ep.DeepTreeNode, lambda x: x.TYPE=="<", lambda x: x.TYPE==">")

print("\n"*20)
print(phrase)
tree = tree_maker.parse(tokens2).children[0]
print("\n"*10)
tree.pretty_print()

rpp = ReaperNode(tree)

tracks = filter_tree(rpp, lambda x: x.name == "TRACK")

print(tracks, len(tracks))