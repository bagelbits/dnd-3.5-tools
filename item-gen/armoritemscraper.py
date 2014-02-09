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

ArmorItems = {}

class ArmorItemEntry(BookEntry):
	_fieldDict = OrderedDict([
		dndparsetools.titleField.NameTuple(),
		FieldData('baseEntry',
			re.compile(r'^([A-Z]{3,}),(?:\s*\b[A-Z]{3,})*', re.MULTILINE)).NameTuple(),
		dndparsetools.subtypeField.NameTuple(),
		dndparsetools.synergyField.NameTuple(),
		dndparsetools.priceField.NameTuple(),
		FieldData('itemLvl',
			re.compile(r'\bPrice(?:\s+\(Item Level\)):\s*(?:\+?(?:\d|,)+\s(?:gp|bonus))\s*\((.*?)\)', re.MULTILINE)).NameTuple(),
		FieldData('bodySlot',
			re.compile(r'\bBody Slot:\s*(Body|--\s*\(held\))', re.MULTILINE)).NameTuple(),
		dndparsetools.casterLvlField.NameTuple(),
		dndparsetools.auraField.NameTuple(),
		dndparsetools.schoolField.NameTuple(),
		dndparsetools.activationSpeedField.NameTuple(),
		dndparsetools.activationModeField.NameTuple(),
		FieldData('weight', re.compile(r'\bWeight:\s*(\d+\s*lb\.)')).NameTuple(),
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
			self.loadOther(ArmorItems[self.baseEntry])
		return unparsed	

with codecs.open("assets\out.txt", encoding='utf-8',mode='w',) as outFile:
	fileContents = str()

	with codecs.open(args.file, encoding='utf-8') as file:
		fileContents = file.read()
	
	fileContents = fileContents.replace(u'\xad\n', '') #replace word-break dash
	fileContents = fileContents.replace(u'\xad','')
	fileContents = fileContents.replace(u'\xac ','')
	fileContents = fileContents.replace(u'\u2014','--') #replace long-dash
	
	fileSplit = ArmorItemEntry._fieldDict['title'].regex.split(fileContents)
	
	for title,data in zip(fileSplit[1::2],fileSplit[2::2]):
		title = re.sub(r'[ \r\n]+',' ',title) #clean newlines in the title before we pass it along
		prop = ArmorItemEntry()
		prop.parse(data,title)
		ArmorItems[prop.title] = prop
		outFile.write(str(prop) + '\n')
		#print prop
		#break
		unmatched = prop.unmatchedFields()
		if unmatched: print prop.title + 'failed on:' + str(unmatched)
