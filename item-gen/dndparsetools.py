__author__ = 'Walter Gray'
import re
from collections import OrderedDict
from collections import namedtuple

class FieldData(namedtuple('FieldData',['name','regex','default'])):
	__slots__ = ()
	#This is just sugar so we don't hve to put 'None' everywhere
	def __new__(self,name,regex,default=None):
		return super(FieldData,self).__new__(self,name,regex,default)


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
	def LoadOther(self,other):
		self.__dict__[name] = value
		for (key,value) in other.__dict__.items():
			if key not in self.__dict__ or self.__dict__[key] == self._fieldDict[key].default:
				self.__dict__[key] = value


class ArmorPropertyEntry(BookEntry):
	_fieldList = (
		FieldData('title',
			re.compile(r'^((?:[A-Z]{3,},*)(?:\s*\b[A-Z]{3,},*)*)', re.MULTILINE)),
		FieldData('baseEntry',
			re.compile(r'^([A-Z]{3,}),(?:\s*\b[A-Z]{3,})*', re.MULTILINE)),
		FieldData('subtype',
			re.compile(r'\[([A-Z]{3,})\]', re.MULTILINE)),
		FieldData('synergy',
			re.compile(r'\bSynergy Prerequisite:\s*(\b\w+\b(?:\s*\b[a-z]+\b){,2})')),
		FieldData('price',
			re.compile(r'\bPrice:\s*(\+(?:\d|,)+\s(?:gp|bonus))', re.MULTILINE)),
		FieldData('onType',
			re.compile(r'\bProperty:\s*((?:Light)?(?:Metal)?\s*[Aa]rmor(?:\sor shield)?|Shield)', re.MULTILINE)),
		FieldData('casterLvl',
			re.compile(r'\bCaster Level: (\d*)(?:st|nd|rd|th)', re.MULTILINE)),
		FieldData('aura',
			re.compile(r'\bAura:\s+\b\w+\b;\s+\(DC (\d+)\)\s+\b\w+\b', re.MULTILINE)),
		FieldData('school',
			re.compile(r'\bAura:\s+\b\w+\b;\s+\(DC \d+\)\s+\b(\w+)\b', re.MULTILINE)),
		FieldData('activationSpeed',
			re.compile(r'\bActivation:\s*(\b\w+\b|--)(?:\s+\(\b\w+\b\))?')),
		FieldData('activationMode',
			re.compile(r'\bActivation:\s*(?:\b\w+\b\s+)?\(?(\b\w+\b|--)\)?')),
		FieldData('creationPrereqs',
			re.compile(r'\bPrerequisites: (.*?)\.')),
		FieldData('creationCost',
			re.compile(r'\bCost to Create:(.*?)\.'))
	)
		