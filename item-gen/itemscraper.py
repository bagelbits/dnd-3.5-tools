__author__ = 'Walter Gray'
import sys
import argparse
import yaml
import unicodedata
import codecs

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file') #file to parse
args = parser.parse_args()

with open("assets\out.txt", 'w') as outFile:
	fileContents = str()
	with codecs.open(args.file, encoding='utf-8') as file:
		fileContents = file.read()
	
	
	print repr(fileContents)
	fileContents = fileContents.replace(u'\xad\r\n', '') #replace word-break dash
	fileContents = fileContents.replace(u'\u2014','--') #replace long-dash
	fileContents = fileContents.split('\r\n')
	print repr(fileContents)
	
	for line in fileContents :
		outFile.write(line.encode('ascii'))
	