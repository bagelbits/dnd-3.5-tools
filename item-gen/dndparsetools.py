__author__ = 'Walter Gray'
import re
from collections import OrderedDict
from collections import namedtuple

class FieldData(namedtuple('FieldData',['name','regex','default','verbose'])):
	__slots__ = ()
	#This is just sugar so we don't hve to put 'None' everywhere for default values
	def __new__(self,name,regex,default=None,verbose=False):
		return super(FieldData,self).__new__(self,name,regex,default,verbose)

	def NameTuple(self):
		return (self.name,self)
		
titleField = FieldData('title',	re.compile(r'^((?:[A-Z]{3,},*)(?:\s*\b[A-Z]{2,},*)*)', re.MULTILINE))
subtypeField = FieldData('subtype',	re.compile(r'\[([A-Z]{3,})\]', re.MULTILINE))
synergyField = FieldData('synergy',	re.compile(r'\bSynergy Prerequisite:\s*(\b\w+\b(?:\s*\b[a-z]+\b){,2})'))
priceField = FieldData('price',	re.compile(r'\bPrice(?:\s+\(Item Level\)):\s*(\+?(?:\d|,)+\s(?:gp|bonus))', re.MULTILINE))
casterLvlField = FieldData('casterLvl', re.compile(r'\bCaster Level: (\d*)(?:st|nd|rd|th)', re.MULTILINE))
auraField = FieldData('aura', re.compile(r'\bAura:\s+\b\w+\b;\s+\(DC (\d+)\)\s+\b\w+\b', re.MULTILINE))
schoolField = FieldData('school', re.compile(r'\bAura:\s+\b\w+\b;\s+\(DC \d+\)\s+\b(\w+)\b', re.MULTILINE))
activationSpeedField = FieldData('activationSpeed', re.compile(r'\bActivation:\s*(\b\w+\b|--)(?:\s+\(\b\w+\b\))?'))
activationModeField = FieldData('activationMode', re.compile(r'\bActivation:\s*(?:\b\w+\b\s+)?\(?(\b\w+\b|--)\)?'))

class BookEntry:
	_fieldDict = OrderedDict()
	
	def __init__(self):
		for field, data in self._fieldDict.items() :
			self.__dict__[field] = data.default
		
	def __str__(self):
		string = ''
		if hasattr(self, 'title'): string = '{0}\n'.format(self.title)
		else : string = '{0}\n'.format(self.__class__.__name__)
		for fieldName in self._fieldDict.keys():
			string += '    {0}: {1}\n'.format(fieldName,self.__dict__[fieldName])
		return string
	def __setattr__(self,name,value):
		assert name in self.__dict__
		self.__dict__[name] = value
	def loadOther(self,other):
		for (key,value) in other.__dict__.items():
			if key not in self.__dict__ or self.__dict__[key] == self._fieldDict[key].default:
				self.__dict__[key] = value

	#pre-parsed values may be provided as tuples following the data arg
	def parse(self, data, *values):
		#load any supplied values
		for field,value in zip(values[0::2], values[1::2]):
			assert field in self.__dict__
			self.__dict__[field] = value
		
		unmatched = data
		for field,fieldData in self._fieldDict.items():
			if field in self.__dict__ and self.__dict__[field] != self._fieldDict[field].default:
				continue
			match = fieldData.regex.search(data)
			if match:
				if fieldData.verbose:
					print 'Matched for ' + field + ':' + match.group(1)
				unmatched = unmatched.replace(match.group(0),'')
				setattr(self,field, re.sub(r'\s+',' ',match.group(1),re.MULTILINE))
			elif fieldData.verbose:
				print 'Match failed for ' + field + ': ' + data
		
		return unmatched
	def unmatchedFields(self):
		unmatched = []
		for field, fieldData in self._fieldDict.items():
			if not hasattr(self,field) or getattr(self,field) == fieldData.default:
				unmatched.append(field)
		return unmatched