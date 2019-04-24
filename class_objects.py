
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
	def __init__(self, position = (0,0), attributes = Attributes(), name="", identity = ""):
		self.position = position
		self.attributes = attributes
		self.name = name
		self.id = identity
		self.shape = None
		self.color = None

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
	def __init__(self, source, destination, edge_type, attrs = None):
		self.source = source
		self.destination   = destination
		self.edge_type = abs(edge_type)
		self.attrs 		 = attrs

	def show(self):
		if self.edge_type:
			print self.source, " -> ", self.destination
		else:
			print self.source, " -- ", self.destination
	
	def toJSON(self):
		import json
		return json.dumps(self, default=lambda o: o.__dict__)

