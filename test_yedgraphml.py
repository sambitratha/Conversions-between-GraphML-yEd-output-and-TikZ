import yedgraphml

g = yedgraphml.Graph()

g.add_node('foo', font_family="Zapfino", x=0, y=0)
g.add_node('foo2', shape="roundrectangle", font_style="bolditalic",
           underlined_text="true", x=300, y=300)

g.add_node('foo3', font_family="Zapfino", x=400, y=440)

g.add_edge('foo', 'foo2')


# print(g.get_graph())

g.write_graph("test.graphml")