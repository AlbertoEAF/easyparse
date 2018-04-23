import easyparse as ep
import easyparse.tokenizers as epts

class WordTokenizer(ep.Tokenizer):
    def __init__(self, extra_chars=()):
        self.extra_chars = extra_chars
    def tokenize(self, view):
        buffer = view.consume_while(lambda x: x.isalnum() or x in self.extra_chars)
        if buffer:
            return ep.Token("WORD", "".join(buffer))

class PropertyTokenizer(ep.Tokenizer):
    def tokenize(self, view):
        buffer = view.consume_while(lambda x: x.TYPE == "WORD")
        if buffer:
            return ep.Token("Property", [ token.content for token in buffer ])


class ReaperNode(object):
    def __init__(self, node):
        node = ep.DeepTreeNode(node)

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
        self.rpp_raw = open(self.filepath).read()

        self.tree, self.rpp = self._parse(self.rpp_raw)

    def _parse(self, raw_content):
        rpp_lexer_stage1 = ep.Lexer([
            WordTokenizer(extra_chars=("_","-",".", "/","\"", "{", "}")),
            epts.WhitespaceTokenizer(auto_discard=True),
            epts.SingleTokenizer("NEWLINE", lambda x: "\n" == x, lambda x: None),
            ] + [ epts.CharTokenizer(char) for char in ["<", ">"] ])

        rpp_lexer_stage2 = ep.Lexer([
            PropertyTokenizer(),
            epts.DiscardTokens(lambda token: token.TYPE == "NEWLINE"),
            epts.IdentityTokenizer()])

        tokens = rpp_lexer_stage1.parse(raw_content) # acts as tokenizer
        tokens = rpp_lexer_stage2.parse(tokens)      # parses the tokens

        tree_maker = ep.TreeMaker(ep.DeepTreeNode, lambda x: x.TYPE=="<", lambda x: x.TYPE==">")

        tree = tree_maker.parse(tokens).children[0]
        rpp = ReaperNode(tree)

        tree.pretty_print()
        print("\n"*5)
        return (tree, rpp)



if __name__ == "__main__":
    rpp = RPP(r"C:\Users\AlbertoEAF\Desktop\teste\teste.rpp")

    tracks = filter_tree(rpp.rpp, lambda x: x.name == "TRACK")

    print("RPP:", rpp.filepath, "\n")
    for track in tracks:
        track_items = track.children
        track_items = [ (item.name, item.properties["NAME"][0], item.children[0].properties["FILE"][0]) for item in track_items ]
        print(f""" TRACK {track.properties["NAME"][0]}""")
        for item in (track_items):
            print("  ", " ".join(item))