__author__ = 'Walter Gray'
import re
from collections import OrderedDict
from collections import namedtuple

FieldData = namedtuple('FieldData',['name','regex','default'])

class BookEntry:
	_fieldData = OrderedDict()
	def __init__(self):
		for field, data in self._fieldData.items() :
			self.__dict__[field] = data.default
	def __str__(self):
		string = ''
		if hasattr(self, 'title'): string = '{0}\n'.format(self.title)
		else : string = '{0}\n'.format(self.__class__.__name__)
		for fieldName in self._fieldData.keys():
			string += '    {0}: {1}\n'.format(fieldName,self.__dict__[fieldName])
		return string
	def __setattr__(self,name,value):
		assert name in self.__dict__
	def LoadOther(self,other):
		self.__dict__[name] = value
		for (key,value) in other.__dict__.items():
			if key not in self.__dict__ or self.__dict__[key] == self._fieldData[key].default:
				self.__dict__[key] = value

