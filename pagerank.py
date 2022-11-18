class Node:

    def __init__(self, id_) -> None:
        self.id_ = id_
        self.children = []
        self.parents = []
        self.rank = 1

    def add_child(self,child):

        if child not in self.children:
            self.children.append(child)

    def add_parent(self,parent):

        if parent not in self.parents:
            self.parents.append(parent)

    def update_pagerank(self) -> float:

        temp_rank = 0

        for parent in self.parents:
            temp_rank += parent.rank / len(parent.children)

        old_rank = self.rank
        self.rank = temp_rank

        return abs(old_rank - self.rank)

    def __repr__(self) -> str:
        return self.id_+" - "+str(self.rank)

class Graph:

    def __init__(self) -> None:
        self.nodes = []
    
    def get_node_from_id(self,id_):
        for node in self.nodes:
            if node.id_ == id_:
                return node

        return None

    def add_node(self,id_):
        if(self.get_node_from_id(id_)):
            raise ValueError("Id already exists")

        self.nodes.append(Node(id_))

    def add_edge(self,parent: Node, child: Node):
        parent.add_child(child)
        child.add_parent(parent)

    def add_edge_from_id(self,parent: int, child: int):
        parent_node = self.get_node_from_id(parent)

        if not parent_node:
            parent_node = Node(parent)
            self.nodes.append(parent_node)

        child_node = self.get_node_from_id(child)

        if not child_node:
            child_node = Node(child)
            self.nodes.append(child_node)

        self.add_edge(parent_node,child_node)
    
    def load_from_file(self,filename = "nodes.txt"):
        
        with open(filename,'r') as f:
            for line in f.readlines():
                data = line.split(",")
                self.add_edge_from_id(data[0].strip(),data[1].strip())

def pagerank(graph: Graph) -> dict:

    ranks = {}

    while True:

        total_diff = 0

        for node in graph.nodes:
            total_diff += node.update_pagerank()
            ranks[node.id_] = node.rank

        average_ = total_diff/ len(graph.nodes)

        if average_ <0.2:
            break
    
    # print('-----------------------------------------------------------')
    # for node in graph.nodes:
    #     print(f'{node.id_} = {node.rank}, with parents {node.parents} and children {node.children}')

    # print('----------------------------------------------------\n\n')

    return ranks

if __name__ == "__main__":
    g = Graph()
    g.load_from_file()

    ranks = pagerank(g)

    print(f'ranks: {ranks}')