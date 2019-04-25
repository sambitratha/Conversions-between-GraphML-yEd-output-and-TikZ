import yedgraphml
import json


def run(jsonfilename= "sample2.json", graphfilename="test.graphml"):
	with open(jsonfilename) as f:
	    data = json.load(f)

	edge_map = {1: 'standard', 0: 'none', -1: 'standard'}
	nodes = data['Nodes']
	edges = data['Edges']
	g = yedgraphml.Graph()

	for node in nodes:
		g.add_node(node['id'], label = node['name'], shape = node['shape'], shape_fill = node['color'], x=node['position'][0], y=node['position'][1])

	for edge in edges:
		edge['edge_type'] = edge_map[edge['edge_type']]
		g.add_edge(edge['source'], edge['destination'], arrowhead = edge['edge_type'])


	g.write_graph(graphfilename)

	return graphfilename
