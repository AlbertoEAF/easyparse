from easyparse.Buffer import *

class TreeNode(object):
    def __init__(self):
        self._properties = []

    @property
    def properties(self):
        return self._properties

    def add(self, value):
        self.add_property(value)

    def add_property(self, value):
        self._properties.append(value)

    def add_child(self, value):
        self.add(value)

    def pretty_print(self, level_indent_size = 2, level=0):
        def outer_print(x):
            print(" " * (level_indent_size * level) + str(x))
        def inner_print(x):
            print(" " * (level_indent_size * (level+1)) + str(x))

        outer_print("<")
        for property in self.properties:
            if not isinstance(property, TreeNode):
                inner_print(property)
            else:
                property.pretty_print(level_indent_size=level_indent_size, level=level+1)
        outer_print(">")

    def __repr__(self):
        return f"TreeNode(properties={self.properties})"

class DeepTreeNode(TreeNode):
    def __init__(self, node=None):
        self._properties = []
        self._children   = []

        if isinstance(node, DeepTreeNode):
            self._properties = node._properties
            self._children   = node._children
        elif isinstance(node, TreeNode):
            self._properties, self._children = __class__.fromTreeNode(node)

    @staticmethod
    def fromTreeNode(node):
        is_child = lambda x: isinstance(x, TreeNode)

        node_elements = node.properties

        properties = [ x for x in node.properties if not is_child(x) ]
        children   = [ x for x in node.properties if     is_child(x) ]

        return properties, children

    @property
    def properties(self):
        return self._properties

    @property
    def children(self):
        return self._children

    def add_property(self, value):
        self._properties.append(value)

    def add_child(self, value):
        self._children.append(value)

    def pretty_print(self, level_indent_size = 2, level=0):
        def outer_print(x):
            print(" " * (level_indent_size * level) + str(x))
        def inner_print(x):
            print(" " * (level_indent_size * (level+1)) + str(x))

        outer_print("<")
        for item in self.properties + self.children:
            if not isinstance(item, TreeNode):
                inner_print(item)
            else:
                item.pretty_print(level_indent_size=level_indent_size, level=level+1)
        outer_print(">")

    def __repr__(self):
        return f"DeepTreeNode(properties={self.properties}, children = {self.children})"


class TreeMaker(object):
    def __init__(self, NodeType, enter, leave):
        self.NodeType = NodeType
        self.enter = enter
        self.leave = leave

    def parse(self, flatlist):
        return self._parse(Buffer(flatlist)) # parses the view

    def _parse(self, view):
        node = self.NodeType()

        while len(view):
            element = view.pop()
            if   self.enter(element):
                node.add_child( self._parse(view) )
            elif self.leave(element):
                return node
            else:
                node.add_property(element)

        return node