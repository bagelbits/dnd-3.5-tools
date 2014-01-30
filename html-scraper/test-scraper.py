#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup
import urllib2

url = "http://monsterfinder.dndrunde.de/allmonsters.php"
page = urllib2.urlopen(url)
soup = BeautifulSoup(page.read())

for link in soup.find_all('a'):
  monster_link = link.get('href')
  monster_name = link.string
  if monster_link != './':
    monster_link = "http://monsterfinder.dndrunde.de/" + monster_link
    monster_page = urllib2.urlopen(monster_link)
    monster_soup = BeautifulSoup(monster_page.read())
    print monster_soup.prettify()
    break