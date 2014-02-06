__author__ = 'Walter Gray'
import sys
import argparse
import yaml
import unicodedata
import codecs

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file') #file to parse
args = parser.parse_args()

ArmorSubtypesRaw = [u'[SYNERGY]',u'[RELIC]']


class ArmorProperty:
	name = ''
	subtype = ''
	subtypeInfo = ''
	def __str__(self):
		return "{0} \n    Subtype: {1}".format(self.name, self.subtype)
	

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
		if len(words) > 0 and all( word.isupper() for word in words) and (words[0] not in ArmorSubtypesRaw) :
			
			if len(armorprop) > 0 :
				parseArmorProperty(armorprop)
				armorprop = []
			outFile.write('BEGIN_ARMORPROP'+'\n')
		
		outFile.write(line+'\n')
		armorprop.append(line)
		
	