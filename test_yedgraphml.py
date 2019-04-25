import yedgraphml
import json
# from class_objects import *

g = yedgraphml.Graph()

g.add_node('node1', font_family="Zapfino", x=0, y=0)
g.add_node('node2', shape="roundrectangle", x=0, y=300)
g.add_node('node3', shape="roundrectangle", x=300, y=300)
g.add_node('node4', shape="roundrectangle", x=300, y=0)

# g.add_node('node3', font_family="Zapfino", x=400, y=440)

g.add_edge('node1', 'node2')
g.add_edge('node2', 'node3')
g.add_edge('node3', 'node4')
g.add_edge('node4', 'node1')


# print(g.get_graph())

g.write_graph("test.graphml")