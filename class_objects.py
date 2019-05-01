
class Attributes:
	def __init__(self):
		self.named_attributes = {}
		self.unnamed_attributes = []

	def __init__(self, attributes=[]):
		self.named_attributes = {}
		self.unnamed_attributes = []
		for attribute in attributes:
			if type(attribute) == str:
				self.unnamed_attributes.append(attribute)
			else:
				self.named_attributes[attribute[0]] = attribute[1]

	def addNamedAttribute(self, key, value):
		self.named_attributes[key]=value

	def addUnnamedAttribute(self, value):
		self.unnamed_attributes.append(value)

	def show(self):
		print "Named Attributes"
		print self.named_attributes

		print "Unnamed Attributes"
		print self.unnamed_attributes

	def toJSON(self):
		import json
		print json.dumps(self)



class Node:
	def __init__(self, position = (0,0), attributes = Attributes(), name="", identity = "", transparency=False):
		self.shapes = ['ellipse', 'diamond', 'trapezoid','trapezoid2','hexagon','octagon','star5', 'star6','star7', 'star8','triangle','triangle2', 'circle', 'rectangle', 'roundrectangle']
		self.colors = {"white":"#FFFFFF","none":"#FFFFFF", "silver":"#C0C0C0", "gray":"#808080", "black":"#000000","red":"#FF0000","yellow":"#FFFF00","green":"#008000","blue":"#0000FF", "purple":"#800080"}
		self.position = position
		self.attributes = attributes
		self.name = name
		self.id = identity
		self.shape = "circle"
		self.color = "#000000"
		self.height = 30
		self.width = 30
		self.intensity = 60
		self.transparency = transparency
		if 'fill' in self.attributes.named_attributes.keys():
			color = self.attributes.named_attributes['fill']
			# print color
			if color in self.colors.keys():
				self.color = self.colors[color]
		if 'intensity' in self.attributes.named_attributes.keys():
			self.intensity = self.attributes.named_attributes['intensity']
		for attribute in self.attributes.unnamed_attributes:
			if attribute in self.shapes:
				self.shape = attribute
				break
	def makeTransparent(self):
		self.transparency = True
	def show(self):
		print "Name: ", self.name
		print "Position: ", self.position
		print "id: ", self.id
		self.attributes.show()
		print

	def toJSON(self):
		import json
		return json.dumps(self, default=lambda o: o.__dict__)


class Edge:
	def __init__(self, source, destination, s_pos, d_pos, edge_type, attrs = None,):
		self.source = source
		self.destination   = destination
		self.edge_type = abs(edge_type)
		self.attrs 		 = attrs
		self.width = 1
		self.color = "#000000"
		self.sx = 0
		self.sy = 0
		self.tx = 0
		self.ty = 0

	def show(self):
		if self.edge_type:
			print self.source, " -> ", self.destination
		else:
			print self.source, " -- ", self.destination
	
	def toJSON(self):
		import json
		return json.dumps(self, default=lambda o: o.__dict__)

