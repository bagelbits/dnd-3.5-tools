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
		'name': re.compile(r'^((?:[A-Z]{3,},*)(?:\s*\b[A-Z]{3,},*)*)'),
		'baseName': re.compile(r'((?:[A-Z]{3,} *)+), '),
		'price': re.compile(r'\bPrice:\s*(\+(?:\w|,)+\s(?:gp|bonus))'),
		'onType': re.compile(r'\bProperty:\s*((:?Light)?(:?Metal)?\s*[Aa]rmor(:?\sor shield)?|Shield)')
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
	
def parseArmorProperty(lines):
	armorProp = ArmorProperty()
		
	armorProp.raw = lines
	
	for line in lines:
		if not armorProp.name : 
			match = ArmorProperty.Regexs['name'].search(line)
			if match: 
				armorProp.name = match.group(1)
				baseMatch = ArmorProperty.Regexs['baseName'].search(armorProp.name)
				if baseMatch: 
					armorProp.baseName = baseMatch.group(1)
					armorProp.LoadBaseType(ArmorProperties[armorProp.baseName])
			
		if not armorProp.subtype : extractSubtype(line,armorProp)
		if not armorProp.price : 
			match = ArmorProperty.Regexs['price'].search(line)
			if match:
				armorProp.price = match.group(1)
		if not armorProp.onType :
			match = ArmorProperty.Regexs['onType'].search(line)
			if match:
				armorProp.onType = match.group(1)
	
	if armorProp.onType == '':
		print armorProp
	
	return armorProp
	


with codecs.open("assets\out.txt", encoding='utf-8',mode='w',) as outFile:
	fileContents = str()
	with codecs.open(args.file, encoding='utf-8') as file:
		fileContents = file.read()
	
	fileContents = fileContents.replace(u'\xad\n', '') #replace word-break dash
	fileContents = fileContents.replace(u'\u2014','--') #replace long-dash
	fileLines = fileContents.splitlines()
	
	armorprop = fileLines[:1]
	for line in fileLines[1:]:
		
		if ArmorProperty.Regexs['name'].search(line) :
			assert len(armorprop) > 0
			prop = parseArmorProperty(armorprop)
			ArmorProperties[prop.name] = prop
			armorprop = []
			outFile.write('BEGIN_ARMORPROP'+'\n')
		
		outFile.write(line+'\n')
		armorprop.append(line)
	#do the last one
	prop = parseArmorProperty(armorprop)
	ArmorProperties[prop.name] = prop
	