__author__ = 'Walter Gray'
import sys
import argparse
import yaml
import unicodedata
import codecs
import re
from json import JSONEncoder


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file') #file to parse
args = parser.parse_args()

class ArmorProperty:
	Regexs = {
		'name': re.compile(r'^((?:[A-Z]{3,},*)(?:\s*\b[A-Z]{3,},*)*)', re.MULTILINE),
		'baseName': re.compile(r'^([A-Z]{3,}),(?:\s*\b[A-Z]{3,})*', re.MULTILINE),
		'price': re.compile(r'\bPrice:\s*(\+(?:\d|,)+\s(?:gp|bonus))', re.MULTILINE),
		'onType': re.compile(r'\bProperty:\s*((:?Light)?(:?Metal)?\s*[Aa]rmor(:?\sor shield)?|Shield)', re.MULTILINE),
		'casterLvl': re.compile(r'\bCaster Level: (\d*)(?:st|nd|rd|th)', re.MULTILINE),
		'aura': re.compile(r'\bAura: \b\w+\b\; \(DC (\d+)\) \b\w+\b', re.MULTILINE)
	}
	ArmorSubtypes = ['[RELIC]','[SYNERGY]']
	unprintedFields = ['name','initd','raw']
	def __init__(self):
		self.name = None
		self.baseName = None
		self.subtype = None
		self.subtypeInfo = None
		self.price = None
		self.creationGP = None
		self.creationXP = None
		self.creationDays = None
		self.onType = None
		self.casterLvl = None
		self.aura = None
		self.school = None
		self.description = None
		self.raw = None
		self.initd = True
	
	def __str__(self):
		encoder = JSONEncoder()
		string = ''
		items = self.__dict__.items()
		items = [(key,value) for key,value in items if key not in ArmorProperty.unprintedFields]
		string = '{0}\n'.format(self.name)
		for key, value in items:
			string += '    {0}: {1}'.format(key.capitalize(),value)
		return string
	def __setattr__(self, name, value):
		assert (not self.__dict__.get('initd',False)) or name in self.__dict__
		self.__dict__[name] = value
	def LoadBaseType(self,other):
		for (key,value) in other.__dict__.items():
			if self.__dict__[key] == None : self.__dict__[key] = value

ArmorProperties = {}

def extractSubtype(line,prop):
	subtypeIndex = line.find('[')
	if subtypeIndex != -1:
		prop.subtype = line[subtypeIndex:].strip('[ ]').capitalize()
	
def parseArmorProperty(title,data):
	armorProp = ArmorProperty()
		
	armorProp.name = title;
	baseNameMatch = ArmorProperty.Regexs['baseName'].search(title)
	if baseNameMatch: armorProp.baseName = baseNameMatch.group(1)
	
	print 'Parsing Armor Property'
	for field,regex in ArmorProperty.Regexs.items():
		if not getattr(armorProp,field):
			match = regex.search(data)
			if match:
				if field == 'aura': print '  Matched {0}: {1}'.format(field, match.group(1))
				setattr(armorProp, field, match.group(1))
	
	#Load the base type last so that new fields won't be overwritten
	if armorProp.baseName :
		armorProp.LoadBaseType(ArmorProperties[armorProp.baseName])
	
	return armorProp
	


with codecs.open("assets\out.txt", encoding='utf-8',mode='w',) as outFile:
	fileContents = str()
	with codecs.open(args.file, encoding='utf-8') as file:
		fileContents = file.read()
	
	fileContents = fileContents.replace(u'\xad\n', '') #replace word-break dash
	fileContents = fileContents.replace(u'\u2014','--') #replace long-dash
	
	fileSplit = ArmorProperty.Regexs['name'].split(fileContents)
	
	for title,data in zip(fileSplit[1::2],fileSplit[2::2]):
		prop = parseArmorProperty(title,data)
		ArmorProperties[prop.name] = prop
		outFile.write('BEGIN_ARMORPROP'+'\n')
		outFile.write(title+'\n'+data+'\n')
		