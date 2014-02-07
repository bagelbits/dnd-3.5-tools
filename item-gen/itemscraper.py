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
	name = ''
	subtype = ''
	subtypeInfo = ''
	price = ''
	creationGP = -1
	creationXP = -1
	creationDays = -1
	onArmor = False
	onShield = False
	casterLvl = -1
	aura = ''
	school = ''
	description = ''
	ArmorSubtypes = ['[RELIC]','[SYNERGY]']
	
	def __str__(self):
		encoder = JSONEncoder()
		string = ''
		items = self.__dict__.items()
		items = [(key,value) for key,value in items if key != 'name']
		string = '{0}\n'.format(self.name)
		for key, value in items:
			string += '    {0}: {1}'.format(key.capitalize(),value)
		return string
	

def extractSubtype(line,prop):
	subtypeIndex = line.find('[')
	if subtypeIndex != -1:
		prop.subtype = line[subtypeIndex:].strip('[ ]').capitalize()
	
def parseArmorProperty(lines):
	armorProp = ArmorProperty()
	
	#normalize the title by removing the subtype
	armorProp.name = lines[0].split('[')[0].strip()
	
	for line in lines:
		if not armorProp.subtype : extractSubtype(line,armorProp)
	print armorProp
	


with codecs.open("assets\out.txt", encoding='utf-8',mode='w',) as outFile:
	fileContents = str()
	with codecs.open(args.file, encoding='utf-8') as file:
		fileContents = file.read()
	
	fileContents = fileContents.replace(u'\xad\n', '') #replace word-break dash
	fileContents = fileContents.replace(u'\u2014','--') #replace long-dash
	fileLines = fileContents.splitlines()
	
	armorprop = []
	for line in fileLines:
		words = line.split()
		if len(words) > 0 and all( word.isupper() for word in words) and (words[0] not in ArmorProperty.ArmorSubtypes ) :
			
			if len(armorprop) > 0 :
				parseArmorProperty(armorprop)
				armorprop = []
			outFile.write('BEGIN_ARMORPROP'+'\n')
		
		outFile.write(line+'\n')
		armorprop.append(line)
		
	