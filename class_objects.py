
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

class Node:
	def __init__(self, position = (0,0), attributes = Attributes(), name=""):
		self.position = position
		self.attributes = attributes
		self.name = name

	def show(self):
		print "Name: ", self.name
		print "Position: ", self.position
		self.attributes.show()
		print



