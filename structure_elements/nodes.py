class Nodes:
    def __init__(self, accuracy=0.01):
        self.nodes = []
        self.amount = 0
        self.accuracy = accuracy

    def __repr__(self):
        return repr(self.nodes)

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i < self.amount:
            result = self.nodes[self.i]
            self.i += 1
            return result
        else:
            raise StopIteration

    def add_node(self, x, y):
        if self.amount != 0:
            distance, i = self.closest_point(x, y)
            if distance < self.accuracy:
                return self.nodes[i]
        node = Node(self.amount, x, y)
        self.nodes.append(node)
        self.amount += 1
        return node

    def closest_point(self, x, y):
        distances = [((node.x - x) ** 2 + (node.y - y) ** 2) ** 0.5 for node in self.nodes]
        distance, i = min((val, idx) for (idx, val) in enumerate(distances))
        return distance, i

    def order_nodes(self):
        self.nodes.sort(key=lambda node: node.x)
        for i in range(len(self.nodes)):
            self.nodes[i].index = i
        return

    def pop_nodes(self, nodes):
        for node in nodes:
            node.index = None
            self.nodes.remove(node)
            self.amount -= 1
        self.order_nodes()
        return

    def structural_nodes(self):
        nodes_location = [[node.x, node.y] for node in self.nodes]
        structural_nodes = {'Location': nodes_location}
        return structural_nodes


class Node:
    def __init__(self, i, x, y):
        self.index = i
        self.x = x
        self.y = y

    def __repr__(self):
        string = f'i:' + str(self.index)
        string += ',(' + str(round(self.x, 3))
        string += ',' + str(round(self.y, 3)) + ')'
        return string

    def __eq__(self, other):
        return self.index == other.index

    def coordinates(self):
        node = [self.x, self.y]
        return node
