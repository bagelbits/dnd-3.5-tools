__author__ = 'Walter Gray'
import sys
import argparse
import yaml
import unicodedata
import codecs
import re
import dndparsetools
from dndparsetools import FieldData
from dndparsetools import BookEntry
from collections import OrderedDict
from json import JSONEncoder


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file') #file to parse
args = parser.parse_args()

ArmorProperties = {}

class ArmorPropertyEntry(BookEntry):
	_fieldDict = OrderedDict([
		dndparsetools.titleField.NameTuple(),
		FieldData('baseEntry',
			re.compile(r'^([A-Z]{3,}),(?:\s*\b[A-Z]{3,})*', re.MULTILINE)).NameTuple(),
		dndparsetools.subtypeField.NameTuple(),
		dndparsetools.synergyField.NameTuple(),
		dndparsetools.priceField.NameTuple(),
		FieldData('onType',
			re.compile(r'\bProperty:\s*((?:Light)?(?:Metal)?\s*[Aa]rmor(?:\sor shield)?|Shield)', re.MULTILINE)).NameTuple(),
		dndparsetools.casterLvlField.NameTuple(),
		dndparsetools.auraField.NameTuple(),
		dndparsetools.schoolField.NameTuple(),
		FieldData('activationSpeed',
			re.compile(r'\bActivation:\s*(\b\w+\b|--)(?:\s+\(\b\w+\b\))?')).NameTuple(),
		FieldData('activationMode',
			re.compile(r'\bActivation:\s*(?:\b\w+\b\s+)?\(?(\b\w+\b|--)\)?')).NameTuple(),
		FieldData('creationPrereqs',
			re.compile(r'\bPrerequisites: (.*?)\.')).NameTuple(),
		FieldData('creationCost',
			re.compile(r'\bCost to Create:(.*?)\.')).NameTuple(),
		FieldData('description',re.compile('()')).NameTuple()
	])
	
	def parse(self,data,title):
		unparsed = BookEntry.parse(self,title+'\n'+data,'title',title)
		unparsed = unparsed.replace(title,'')
		self.__dict__['description'] = re.sub(r'(\r?\n\s*)+',r'\n',unparsed).strip()
		
		#Load the base type last so that new fields won't be overwritten
		if self.baseEntry :
			self.loadOther(ArmorProperties[self.baseEntry])
		return unparsed	

with codecs.open("assets\out.txt", encoding='utf-8',mode='w',) as outFile:
	fileContents = str()

	with codecs.open(args.file, encoding='utf-8') as file:
		fileContents = file.read()
	
	fileContents = fileContents.replace(u'\xad\n', '') #replace word-break dash
	fileContents = fileContents.replace(u'\xad','')
	fileContents = fileContents.replace(u'\xac ','')
	fileContents = fileContents.replace(u'\u2014','--') #replace long-dash
	
	fileSplit = ArmorPropertyEntry._fieldDict['title'].regex.split(fileContents)
	
	for title,data in zip(fileSplit[1::2],fileSplit[2::2]):
		prop = ArmorPropertyEntry()
		prop.parse(data,title)
		ArmorProperties[prop.title] = prop
		outFile.write(str(prop) + '\n')
		#print prop
		