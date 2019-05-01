import sys
import xml.etree.cElementTree as ET
import xml.dom.minidom

line_types = ["line", "dashed", "dotted", "dashed_dotted"]
font_styles = ["plain", "bold", "italic", "bolditalic"]

arrow_types = ["none", "standard", "white_delta", "diamond", "white_diamond", "short",
               "plain", "concave", "convex", "circle", "transparent_circle", "dash",
               "skewed_dash", "t_shape", "crows_foot_one_mandatory",
               "crows_foot_many_mandatory", "crows_foot_many_optional", "crows_foot_one",
               "crows_foot_many", "crows_foot_optional"]

node_shapes = ["rectangle", "rectangle3d", "roundrectangle", "diamond", "ellipse",
               "fatarrow", "fatarrow2", "hexagon", "octagon", "parallelogram",
               "parallelogram2", "star5", "star6", "star6", "star8", "trapezoid",
               "trapezoid2", "triangle", "trapezoid2", "triangle", "circle"]

shape_dict_xml_tex = {'ellipse': 'circle', 'diamond': 'diamond', 'trapezoid': 'trapezium',
                      'trapezoid2': 'trapezium, rotate=180',
                      'hexagon': 'regular polygon, regular polygon sides=6',
                      'octagon': 'regular polygon, regular polygon sides=8',
                      'star5': 'star, star points=5', 'star6': 'star, star points=6',
                      'star7': 'star, star points=7', 'star8': 'star, star points=8',
                      'triangle': 'regular polygon, regular polygon sides = 3',
                      'triangle2': 'regular polygon, regular polygon sides = 3, rotate=180',
                      'circle': 'circle', 'rectangle': 'rectangle', 'roundrectangle': 'rectangle, rounded corners = 1'}


class Node:
    def __init__(self, node_name, label=None, shape="rectangle", font_family="Dialog",
                 underlined_text="false", font_style="plain", font_size="12",
                 shape_fill="#000000", transparent="false", edge_color="#000000",
                 edge_type="line", edge_width="1.0", height=100, width=100, x=0,
                 y=0, node_type="ShapeNode"):

        if edge_type not in line_types:
            raise RuntimeWarning("Edge type %s not recognised" % edge_type)
        if shape not in node_shapes:
            raise RuntimeWarning("Node shape %s not recognised" % shape)
        if font_style not in font_styles:
            raise RuntimeWarning("Font style %s not recognised" % font_style)

        self.label = label
        if label is None:
            self.label = node_name

        self.node_name = node_name
        self.node_type = node_type
        self.shape = shape

        # label formatting options
        self.font_family = font_family
        self.underlined_text = underlined_text
        self.font_style = font_style
        self.font_size = font_size

        # shape fill
        self.shape_fill = shape_fill
        self.transparent = transparent

        # edge options
        self.edge_color = edge_color
        self.edge_width = edge_width
        self.edge_type = edge_type

        # geometry
        self.geom = {
            'height': height,
            'width': width,
            'x': x,
            'y': y
        }

    def convert(self):

        node = ET.Element("node", id=str(self.node_name))
        data = ET.SubElement(node, "data", key="data_node")
        shape = ET.SubElement(data, "y:" + self.node_type)
        ET.SubElement(shape, "y:Geometry", height=str(self.geom["height"]),
                      width=str(self.geom["width"]), x=str(self.geom["x"]), y=str(self.geom["y"]) )
        ET.SubElement(shape, "y:Fill", color=self.shape_fill, transparent=self.transparent)
        ET.SubElement(shape, "y:BorderStyle", color=self.edge_color, type=self.edge_type, width=self.edge_width)
        label = ET.SubElement(shape, "y:NodeLabel", fontFamily=self.font_family, fontSize=self.font_size,
                              underlinedText=self.underlined_text, fontStyle=self.font_style)
        label.text = self.label
        ET.SubElement(shape, "y:Shape", type=self.shape)
        return node


class Edge:
    def __init__(self, node1, node2, label="", arrowhead="standard", arrowfoot="none",
                 color="#000000", line_type="line", width=1, sx = 0, sy = 0, tx=1, ty=1):

        if arrowhead not in arrow_types:
            raise RuntimeWarning("Arrowhead type %s not recognised" % arrowhead)
        if arrowfoot not in arrow_types:
            raise RuntimeWarning("Arrowhead type %s not recognised" % arrowfoot)
        if line_type not in line_types:
            raise RuntimeWarning("Edge type %s not recognised" % line_type)

        self.node1 = node1
        self.node2 = node2
        self.edge_id = "%s_%s" % (node1, node2)
        self.label = label
        self.arrowhead = arrowhead
        self.arrowfoot = arrowfoot
        self.line_type = line_type
        self.color = color
        self.width = width
        # geometry
        self.path = {
            'sx': sx,
            'sy': sy,
            'tx': tx,
            'ty': ty
        }

    def convert(self):
        edge = ET.Element("edge", id=str(self.edge_id), source=str(self.node1), target=str(self.node2))
        data = ET.SubElement(edge, "data", key="data_edge")
        pl = ET.SubElement(data, "y:PolyLineEdge")
        ET.SubElement(pl, "y:Path",  sx=str(self.path["sx"]),
                      sy=str(self.path["sy"]), tx=str(self.path["tx"]), ty=str(self.path["ty"]))
        ET.SubElement(pl, "y:Arrows", source=self.arrowfoot, target=self.arrowhead)
        ET.SubElement(pl, "y:LineStyle", color=self.color, type=self.line_type,
                      width=str(self.width))

        if self.label:
            ET.SubElement(pl, "y:EdgeLabel").text = self.label

        return edge


class Graph:
    def __init__(self, directed="directed", graph_id="G"):

        self.nodes_in_groups = []
        self.nodes = {}
        self.edges = {}

        self.directed = directed
        self.graph_id = graph_id
        self.graphml = ""

    def construct_graphml(self):

        graphml = ET.Element("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
        graphml.set("xmlns:java", "http://www.yworks.com/xml/yfiles-common/1.0/java")
        graphml.set("xmlns:sys",
                    "http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0")
        graphml.set("xmlns:x", "http://www.yworks.com/xml/yfiles-common/markup/2.0")
        graphml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        graphml.set("xmlns:y", "http://www.yworks.com/xml/graphml")
        graphml.set("xmlns:yed", "http://www.yworks.com/xml/yed/3")
        graphml.set("xsi:schemaLocation",
                    "http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd")
        comment = ET.Comment('Graphml file Converted from Tex Code')
        graphml.append(comment)
        node_key = ET.SubElement(graphml, "key", id="data_node")
        node_key.set("for", "node")
        node_key.set("yfiles.type", "nodegraphics")

        edge_key = ET.SubElement(graphml, "key", id="data_edge")
        edge_key.set("for", "edge")
        edge_key.set("yfiles.type", "edgegraphics")

        graph = ET.SubElement(graphml, "graph", edgedefault=self.directed,
                              id=self.graph_id)

        for node_id in self.nodes:
            node = self.nodes[node_id].convert()
            graph.append(node)

        for edge_id in self.edges:
            edge = self.edges[edge_id].convert()
            graph.append(edge)

        self.graphml = graphml

    def write_graph(self, filename):
        self.construct_graphml()
        # ET.ElementTree(self.graphml).write(filename, encoding='utf-8', xml_declaration=True)

        if sys.version_info.major < 3:
            xml_string =  ET.tostring(self.graphml, encoding='UTF-8')
        else:
            xml_string= ET.tostring(self.graphml, encoding='UTF-8').decode()

        parsed_xml = xml.dom.minidom.parseString(xml_string)
        pretty_xml_as_string = parsed_xml.toprettyxml()

        file = open(filename, 'w')
        file.write(pretty_xml_as_string)
        file.close()

    def get_graph(self):
        self.construct_graphml()
        if sys.version_info.major < 3:
            return ET.tostring(self.graphml, encoding='UTF-8')
        else:
            return ET.tostring(self.graphml, encoding='UTF-8').decode()

    def add_node(self, node_name, **kwargs):
        if node_name in self.nodes.keys():
            raise RuntimeWarning("Node %s already exists" % node_name)

        self.nodes[node_name] = Node(node_name, **kwargs)

    # pass node names, not actual node objects
    def add_edge(self, node1, node2, label="", arrowhead="standard", arrowfoot="none",
                 color="#000000", line_type="line",
                 width="1.0", sx = 0, sy = 0, tx=1, ty=1):

        if node1 not in self.nodes.keys():
            self.nodes[node1] = Node(node1)

        if node2 not in self.nodes.keys():
            self.nodes[node2] = Node(node2)

        edge = Edge(node1, node2, label, arrowhead, arrowfoot, color, line_type, width, sx , sy, tx, ty)
        self.edges[edge.edge_id] = edge
