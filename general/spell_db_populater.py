#!/usr/bin/env python
# -*- coding: utf8 -*-
import sqlite3
import traceback
import re
from sys import exit


def table_setup(name, db_cursor):
    if(name == 'spell'):
        db_cursor.execute("CREATE TABLE spell\
            (id INTEGER PRIMARY KEY, name TINYTEXT,\
            cast_time TINYTEXT, range TINYTEXT,\
            target TINYTEXT, effect TINYTEXT, area TINYTEXT, duration TINYTEXT,\
            saving_throw TINYTEXT, description TINYTEXT, components TINYTEXT)")

    elif(name == 'class'):
        db_cursor.execute("CREATE TABLE class (\
            id INTEGER PRIMARY KEY, name TINYTEXT, \
            probability INT, divine INT, arcane INT)")

    elif(name == 'class_spell'):
        db_cursor.execute("CREATE TABLE class_spell (\
            id INTEGER PRIMARY KEY, class_id INT, \
            spell_id INT, level INT)")

    elif(name == 'domain'):
        db_cursor.execute("CREATE TABLE domain (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'domain_spell'):
        db_cursor.execute("CREATE TABLE domain_spell (\
            id INTEGER PRIMARY KEY, domain_id INT, \
            spell_id INTEGER, level INT)")

    elif(name == 'book'):
        db_cursor.execute("CREATE TABLE book (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'book_spell'):
        db_cursor.execute("CREATE TABLE book_spell (\
            id INTEGER PRIMARY KEY, book_id INT, \
            spell_id INT, page TINYTEXT")

    elif(name == 'school'):
        db_cursor.execute("CREATE TABLE type (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'spell_school'):
        db_cursor.execute("CREATE TABLE spell_type (\
            id INTEGER PRIMARY KEY, school_id INT, \
            spell_id INT)")

    elif(name == 'subtype'):
        db_cursor.execute("CREATE TABLE subtype (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'spell_subtype'):
        db_cursor.execute("CREATE TABLE spell_subtype (\
            id INTEGER PRIMARY KEY, subtype_id INT, \
            spell_id INT)")


def parse_spell(spell):
    global alt_spells
    global web_abbrev
    spell_line = spell.pop(0).strip()

    #Handle the See "this spell" for info cases
    match = re.search('See "(.+)"', spell[0])
    if match:
        alt_spells.append([spell_line.strip(), match.group(1)])
        return

    # First get the spell name and book with page number
    match = re.search('(.+) \[(.+)\]', spell_line)
    spell_name = match.group(1)
    book_info = match.group(2)
    book_info = book_info.split(",")

    # Spells can have multiple books
    for x in range(len(book_info)):
        # Books may or may not have a page number
        book_info[x] = book_info[x].strip()
        match = re.search('\(pg\s?(\d+)\)', book_info[x])
        if match:
            page = match.group(1)
            book_name = re.search('(.+) \(pg\s?\d+\)', book_info[x]).group(1)
        else:
            page = None
            book_name = book_info[x]
        #Handle web abbreviations
        if book_name in web_abbrev:
            book_name = web_abbrev[book_name]
        book_info[x] = [book_name, page]

    # Now lets figure out the type and sub-type
    type_line = spell.pop(0)
    school = type_line.split()[0].split("/")
    sub_types = []
    match = re.search('\((.+)\)', type_line)
    if match:
        sub_types.extend([sub_type.strip() for sub_type in match.group(1).split(",")])
    match = re.search('\[(.+)\]', type_line)
    if match:
        sub_types.extend([sub_type.strip() for sub_type in match.group(1).split(",")])

    if spell[0].startswith("Level: "):
        classes = {}
        level_lines = [spell.pop(0).strip()]
        while True:
            if re.match("\w+:", spell[0]):
                break
            level_lines.append(spell.pop(0).strip())
        level_lines = " ".join(level_lines).replace("Level: ", '').split(', ')
        # Now lets separate class from level. We may need to come back to
        # this point later.
        for class_level in level_lines:
            level = re.search('(\d+)', class_level).group(1)
            character_class = re.sub(' \d+', '', class_level, count=1)
            classes[character_class] = level

    # Now need to break everything else out
    spell_info = {}
    while True:
        #You've hit the description yay!
        if spell[0].startswith(' '):
            break
        # Magically, you have no description
        if len(spell) == 0:
            break
        spell_line = spell.pop(0).strip()
        spell_descriptor = re.match("(\w+( \w+)*): ", spell_line).group(1).lower()
        spell_descriptor = re.sub(" +", "_", spell_descriptor)
        spell_line = re.sub("\w+( \w+)*: ", '', spell_line, count=1)
        spell_info[spell_descriptor] = spell_line

    #Now stich together the rest of the description
    spell_info['description'] = "\n".join(spell).strip()

    # Finished pieces:
    # Spell Name
    # Book Name
    # Page in Book
    # Type (school)
    # Sub-type
    # Class and level
    print "Spell: %s" % spell_name
    print book_info
    print school
    print sub_types
    print classes
    for spell_descriptor in spell_info:
        print "%s: %s" % (spell_descriptor, spell_info[spell_descriptor])

    # Unfinished pieces:
    # Components
    # Casting Time
    # Range
    # Effect
    # Duration
    # Saving Throw


tables = ['spell', 'class_spell', 'class', 'domain_spell', 'domain']
tables.extend(['book', 'type', 'spell_type', 'subtype', 'spell_subtype'])

db_conn = sqlite3.connect('spells.db')
db_conn.text_factory = str
db_cursor = db_conn.cursor()

db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_results = db_cursor.fetchall()
print table_results
for table in tables:
    if not any(table == result[0] for result in table_results):
        try:
            table_setup(table, db_cursor)
            db_conn.commit()
        except Exception, e:
            traceback.print_exc()
            db_cursor.close()
            db_conn.close()
            exit(1)

#Create a memoizie table of Web abbreviations
web_abbrevation_file = open('data/web-source-abbrev.txt', 'r')
web_abbrev = {}
for line in web_abbrevation_file:
    line = line.strip()
    line = line.split(">")
    web_abbrev[line[0]] = line[1]

#Load up all domains
cleric_domain_file = open('data/cleric_domains.txt', 'r')
for line in cleric_domain_file:
    db_cursor.execute("SELECT id FROM domain WHERE name = ?", (line.strip(), ))
    if not db_cursor.fetchone():
        db_cursor.execute("INSERT INTO domain VALUES (NULL, ?)",
                          (line.strip(), ))

alt_spells = []

#Then parse spell list
all_spells_file = open('data/all-spells.txt', 'r')
spell = []
for line in all_spells_file:
    #End of the file
    if re.match('\-+', line):
        break

    if not line.strip():
        parse_spell(spell)
        del spell[:]
        break
        continue
    spell.append(line)

print "Alt spells: %s" % alt_spells
"""
Ignore spells like:
          Horizikaul's Boom
See "Sonic Blast"

          Horizikaul's Cough
See "Sonic Snap"

          Horizikaul's Versatile Vibration
See "Sonic Rumble"

.... Actually, create a separate table for spells that are the same and have
them referenceto general spell
"""

"""
Add Divine Bard as a separate class and to any
spell that has Bard as a class
"""

"""
Populate Classes, Book, Type, and Subtype tables as you run trough the txt file
Domain should be generated off the other pdf that Noah gave me.
"""
