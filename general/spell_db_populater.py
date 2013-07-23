#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
    Spell Database Populater
    Written by Christopher Durien Ward
    With help from Noah Reson-Brown and Becca Decso
    Special thanks to zook1shoe and JaronK from minmaxboards.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import sqlite3
import traceback
import re
import csv
from sys import exit, stdout


class colorz:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


def table_setup(name, db_cursor):
    if(name == 'spell'):
        db_cursor.execute("CREATE TABLE spell\
            (id INTEGER PRIMARY KEY, name TINYTEXT,\
            cast_time TINYTEXT, range TINYTEXT,\
            target TINYTEXT, effect TINYTEXT, area TINYTEXT, duration TINYTEXT,\
            saving_throw TINYTEXT, spell_resist TINYTEXT, description TINYTEXT,\
            components TINYTEXT)")

    elif(name == 'class'):
        db_cursor.execute("CREATE TABLE class (\
            id INTEGER PRIMARY KEY, name TINYTEXT,\
            divine INT, arcane INT, frequency INT, base_class INT,\
            setting TINYTEXT, book TINYTEXT)")

    elif(name == 'spell_class'):
        db_cursor.execute("CREATE TABLE spell_class (\
            id INTEGER PRIMARY KEY, class_id INT,\
            spell_id INT, level INT, subtype TINYTEXT)")

    elif(name == 'domain_feat'):
        db_cursor.execute("CREATE TABLE domain_feat (\
            id INTEGER PRIMARY KEY, name TINYTEXT, domain INT,\
            feat INT, class TINYTEXT, setting TINYTEXT, book TINYTEXT)")

    elif(name == 'spell_domain_feat'):
        db_cursor.execute("CREATE TABLE spell_domain_feat (\
            id INTEGER PRIMARY KEY, domain_id INT,\
            spell_id INTEGER, level INT)")

    elif(name == 'book'):
        db_cursor.execute("CREATE TABLE book (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'spell_book'):
        db_cursor.execute("CREATE TABLE spell_book (\
            id INTEGER PRIMARY KEY, book_id INT,\
            spell_id INT, page INT)")

    elif(name == 'school'):
        db_cursor.execute("CREATE TABLE school (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'spell_school'):
        db_cursor.execute("CREATE TABLE spell_school (\
            id INTEGER PRIMARY KEY, school_id INT,\
            spell_id INT)")

    elif(name == 'subschool'):
        db_cursor.execute("CREATE TABLE subschool (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'spell_subschool'):
        db_cursor.execute("CREATE TABLE spell_subschool (\
            id INTEGER PRIMARY KEY, subschool_id INT,\
            spell_id INT)")

    elif(name == 'descriptor'):
        db_cursor.execute("CREATE TABLE descriptor (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'spell_descriptor'):
        db_cursor.execute("CREATE TABLE spell_descriptor (\
            id INTEGER PRIMARY KEY, descriptor_id INT,\
            spell_id INT)")

    elif(name == 'component'):
        db_cursor.execute("CREATE TABLE component (\
            id INTEGER PRIMARY KEY, name TINYTEXT,\
            short_hand TINYTEXT)")

    elif(name == 'spell_component'):
        db_cursor.execute("CREATE TABLE spell_component (\
            id INTEGER PRIMARY KEY, component_id INT,\
            spell_id INT)")

    elif(name == 'alt_spell'):
        db_cursor.execute("CREATE TABLE alt_spell (\
            id INTEGER PRIMARY KEY, alt_spell_name TINYTEXT,\
            spell_id INT)")

    elif(name == 'web_abbrev'):
        db_cursor.execute("CREATE TABLE web_abbrev (\
            id INTEGER PRIMARY KEY, abbrev TINYTEXT, name TINYTEXT)")


def preload_tables(db_cursor):
    """
        Let's preload some of the tables:
    """
    #Load up all domains and feats
    domain_feat_file = csv.reader(open('data/domain_feat.csv', 'rU'), delimiter=";", quotechar='"')
    for line in domain_feat_file:
        db_cursor.execute("SELECT id FROM domain_feat WHERE name = ?", (line[0], ))
        if not db_cursor.fetchone():
            db_cursor.execute("INSERT INTO domain_feat VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                              (line[0], line[1], line[2], line[3], line[4], line[5]))

    #Add in the normal spell components
    spell_components = {
        'V': 'Verbal',
        'S': 'Somatic',
        'M': 'Material',
        'F': 'Focus',
        'DF': 'Divine Focus',
        'XP': 'XP Cost',
        'T': 'Truename'
    }
    for component_type in spell_components:
        db_cursor.execute("SELECT id FROM component WHERE short_hand = ?", (component_type,))
        if not db_cursor.fetchone():
            db_cursor.execute("INSERT INTO component VALUES (NULL, ?, ?)",
                              (spell_components[component_type], component_type))

    class_file = csv.reader(open('data/classes.csv', 'rU'), delimiter=";", quotechar='"')
    for line in class_file:
        db_cursor.execute("SELECT id FROM class WHERE name = ?", (line[0], ))
        if not db_cursor.fetchone():
            db_cursor.execute("INSERT INTO class VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
                              (line[0], line[1], line[2], line[3], line[4], line[5], line[6]))

    #Create a memoizie table of Web abbreviations
    web_abbrevation_file = csv.reader(open('data/web-source-abbrev.txt', 'rU'), delimiter=">", quotechar='"')
    for line in web_abbrevation_file:
        db_cursor.execute("SELECT id FROM web_abbrev WHERE abbrev = ?", (line[0],))
        if not db_cursor.fetchone():
            db_cursor.execute("INSERT INTO web_abbrev VALUES (NULL, ?, ?)", (line[0], line[1]))


def stitch_together_parens(level_lines):
    paran_sections = []
    for pos in range(len(level_lines)):
        if "(" in level_lines[pos] and ")" not in level_lines[pos]:
            paran_sections.append([pos])
        if "(" not in level_lines[pos] and ")" in level_lines[pos]:
            paran_sections[-1].append(pos)
    for section in reversed(paran_sections):
        level_lines[section[0]:section[1]+1] = [', '.join(level_lines[section[0]:section[1]+1])]
    return level_lines


def break_out_class_subtype(character_class):
    if "(" in character_class:
        character_class = character_class.strip().split(" (")
        classes_to_subtype = [
            "Wu Jen",
            "Shugenja",
            "Arachnomancer",
            "Spelldancer",
            "Pious Templar",
            "Maho-Tsukai",
            "Savant",
            "Spellsinger"
        ]
        if character_class[0] in classes_to_subtype:
            character_class[1] = character_class[1][:-1]
            if character_class[0] == "Savant":
                character_class[1] = character_class[1].split(" ")
        else:
            character_class = [" (".join(character_class)]
    else:
        character_class = [character_class]

    return character_class


##############################
#        Spell Parsing       #
##############################

def get_book_info(book_info, db_cursor):
    book_info = book_info.split(", ")
    book_info = stitch_together_parens(book_info)

    # Spells can have multiple books
    for x in range(len(book_info)):
        # Books may or may not have a page number
        book_info[x] = book_info[x].strip()
        match = re.search('\(pg\s?(\d+(, \d+)*)\)', book_info[x])
        if match:
            page = match.group(1).split(', ')
            book_name = re.search('(.+) \(pg\s?\d+(, \d+)*\)', book_info[x]).group(1)
        else:
            page = None
            book_name = book_info[x]

        #Handle web abbreviations
        db_cursor.execute("SELECT name FROM web_abbrev WHERE abbrev = ?", (book_name,))
        found = db_cursor.fetchone()
        if found:
            book_name = found[0]
        book_info[x] = [book_name, page]

    return book_info


def get_class_info(level_line):
    if level_line.lower().startswith("level: "):
        classes = {}
        level_line = filter(None, level_line.replace("Level: ", '').split(', '))
        level_line = stitch_together_parens(level_line)
        # Now lets separate class from level. We may need to come back to
        # this point later.
        for class_level in level_line:
            level = [int(re.search('(\d+)', class_level).group(1))]
            character_class = re.sub(' \d+', '', class_level, count=1).strip()
            character_class = break_out_class_subtype(character_class)

            if len(character_class) == 2:
                classes[character_class[0]] = [level, character_class[1]]
            else:
                classes[character_class[0]] = [level]
    return classes


def parse_spell(spell, alt_spells, all_descriptors):
    """
        Let's parse a spell chunk
    """

    spell_info = {'Name': '',
                  'casting_time': '',
                  'range': '',
                  'target': '',
                  'effect': '',
                  'area': '',
                  'duration': '',
                  'saving_throw': '',
                  'spell_resistance': '',
                  'description': '',
                  'components': ''}

    spell_line = spell.pop(0).strip()

    #Handle the See "this spell" for info cases
    match = re.search('See "(.+)"', spell[0])
    if match:
        alt_spells.append([spell_line.strip(), match.group(1)])
        return

    # First get the spell name and book with page number
    match = re.search('(.+) \[(.+)\]', spell_line)
    spell_info['Name'] = match.group(1)
    #print spell_info['Name']
    spell_info['Books'] = get_book_info(match.group(2), db_cursor)

    # Now lets figure out the School and sub-type
    # Because not every spell has a type.
    spell_info['Subschools'] = []
    spell_info['Descriptors'] = []
    if not re.match("\w+( \w+)*:", spell[0]):
        type_line = spell.pop(0)
        spell_info['Schools'] = type_line.split()[0].split("/")
        match = re.search('\((.+)\)', type_line)
        if match:
            spell_info['Subschools'].extend([sub_type.strip() for sub_type in match.group(1).split(",")])
        match = re.search('\[(.+)\]', type_line)
        if match:
            spell_info['Descriptors'].extend([sub_type.strip() for sub_type in match.group(1).split(",")])

    #Now let's grab the classes and levels
    spell_info['Classes'] = get_class_info(spell.pop(0))

    # Now need to break everything else out
    while True:
        #You've hit the description yay!
        if spell[0].startswith('    '):
            break
        # Magically, you have no description
        if len(spell) == 0:
            break
        # Ah, sometimes descriptors can be multiline
        spell_line = [spell.pop(0).strip()]
        #while True and len(spell) > 0:
        while True:
            if re.match('\w+( \w+)*:', spell[0]):
                break
            if spell[0].startswith('    '):
                break
            if len(spell) == 0:
                break
            spell_line.append(spell.pop(0).strip())
        spell_line = " ".join(spell_line)

        spell_descriptor = re.match("(\w+( \w+)*): ", spell_line).group(1).lower()
        spell_descriptor = re.sub(" +", "_", spell_descriptor)
        if spell_descriptor not in all_descriptors:
            all_descriptors.append(spell_descriptor)
        spell_line = re.sub("\w+( \w+)*: ", '', spell_line, count=1)
        spell_info[spell_descriptor] = spell_line

    #Now stich together the rest of the description
    spell_info['description'] = "".join(spell).strip()

    """
    if spell_info['components']:
        spell_info['components'] = spell_info['components'].split(", ")
    """

    return spell_info


# You should populate the spell first so you can populate other tables
# and link tables as we go.
def insert_into_spell_db(db_cursor, spell_info):
    # Initial spell insert:
    db_cursor.execute("SELECT id from spell WHERE name = ? LIMIT 1", (spell_info['Name'],))
    if not db_cursor.fetchone():
        db_cursor.execute("INSERT INTO spell VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (spell_info['Name'],
                           spell_info['casting_time'],
                           spell_info['range'],
                           spell_info['target'],
                           spell_info['effect'],
                           spell_info['area'],
                           spell_info['duration'],
                           spell_info['saving_throw'],
                           spell_info['spell_resistance'],
                           spell_info['description'],
                           spell_info['components']))
        db_cursor.execute("SELECT id from spell WHERE name = ? LIMIT 1", (spell_info['Name'],))
        spell_id = db_cursor.fetchone()[0]

        # Let's populate reference tables as we go:
        ## COMPONENTS ##
        """
        for component in spell_info['components']:
            db_cursor.execute("SELECT id from component WHERE short_hand = ? LIMIT 1",
                             (component,))
            component_id = db_cursor.fetchone()
            if not component_id:
                print spell_info['Name']
                print "%s New component type added: %s%s" % (colorz.RED, component, colorz.ENDC)
                db_cursor.execute("INSERT INTO component VALUES(NULL, NULL, ?)",
                                 (component,))
                db_cursor.execute("SELECT id from component WHERE short_hand = ? LIMIT 1",
                                 (component,))
                component_id = db_cursor.fetchone()
            component_id = component_id[0]
            db_cursor.execute("INSERT INTO spell_component VALUES(NULL, ?, ?)",
                              (component_id, spell_id))
        """

        ## BOOK ##
        for book in spell_info['Books']:
            db_cursor.execute("SELECT id FROM book WHERE name = ? LIMIT 1", (book[0],))
            book_id = db_cursor.fetchone()
            if not book_id:
                #print spell_info['Name']
                db_cursor.execute("INSERT INTO book VALUES(NULL, ?)", (book[0],))
                db_cursor.execute("SELECT id FROM book WHERE name = ? LIMIT 1", (book[0],))
                book_id = db_cursor.fetchone()
            book_id = book_id[0]
            if book[1]:
                for page in book[1]:
                    db_cursor.execute("INSERT INTO spell_book VALUES(NULL, ?, ?, ?)",
                                      (book_id, spell_id, page))
            else:
                db_cursor.execute("INSERT INTO spell_book VALUES(NULL, ?, ?, NULL)",
                                  (book_id, spell_id))

        ## School ##
        for school in spell_info['Schools']:
            db_cursor.execute("SELECT id FROM school WHERE name = ? LIMIT 1", (school,))
            school_id = db_cursor.fetchone()
            if not db_cursor.fetchone():
                db_cursor.execute("INSERT INTO school VALUES(NULL, ?)", (school,))
                db_cursor.execute("SELECT id FROM school WHERE name = ? LIMIT 1", (school,))
                school_id = db_cursor.fetchone()
            school_id = school_id[0]
            db_cursor.execute("INSERT INTO spell_school VALUES(NULL, ?, ?)", (school_id, spell_id))

        ## Subschools ##
        for subschool in spell_info['Subschools']:
            db_cursor.execute("SELECT id FROM subschool WHERE name = ? LIMIT 1", (subschool,))
            subschool_id = db_cursor.fetchone()
            if not db_cursor.fetchone():
                db_cursor.execute("INSERT INTO subschool VALUES(NULL, ?)", (subschool,))
                db_cursor.execute("SELECT id FROM subschool WHERE name = ? LIMIT 1", (subschool,))
                subschool_id = db_cursor.fetchone()
            subschool_id = subschool_id[0]
            db_cursor.execute("INSERT INTO spell_subschool VALUES(NULL, ?, ?)", (subschool_id, spell_id))

        ## Descriptors ##
        for descriptors in spell_info['Descriptors']:
            db_cursor.execute("SELECT id FROM descriptor WHERE name = ? LIMIT 1", (descriptors,))
            descriptor_id = db_cursor.fetchone()
            if not db_cursor.fetchone():
                db_cursor.execute("INSERT INTO descriptor VALUES(NULL, ?)", (descriptors,))
                db_cursor.execute("SELECT id FROM descriptor WHERE name = ? LIMIT 1", (descriptors,))
                descriptor_id = db_cursor.fetchone()
            descriptor_id = descriptor_id[0]
            db_cursor.execute("INSERT INTO spell_descriptor VALUES(NULL, ?, ?)", (descriptor_id, spell_id))

        ## Classes ##
        # Remember to skip domains
        for class_name in spell_info['Classes']:
            db_cursor.execute("SELECT id FROM class WHERE name = ? LIMIT 1", (class_name,))
            if not db_cursor.fetchone():
                db_cursor.execute("SELECT id FROM domain_feat WHERE name = ? LIMIT 1", (class_name,))
                if not db_cursor.fetchone():
                    db_cursor.execute("INSERT INTO class VALUES(NULL, ?, 0, 0, NULL, NULL, NULL, NULL)", (class_name,))
                    print "%s New Class added: %s from %s%s" % (colorz.RED, class_name, spell_info['Name'], colorz.ENDC)

            db_cursor.execute("SELECT id FROM class WHERE name = ? LIMIT 1", (class_name,))
            class_id = db_cursor.fetchone()
            if class_id:
                #Classes
                class_id = class_id[0]
                for level in spell_info['Classes'][class_name][0]:
                    #Don't forget to store subtypes
                    if len(spell_info['Classes'][class_name]) == 2:
                        # This is only for Savant which has a different level
                        # for divine spells
                        if isinstance(spell_info['Classes'][class_name][1], list):
                            db_cursor.execute("INSERT INTO spell_class VALUES(NULL, ?, ?, ?, NULL)",
                                              (class_id, spell_id, level))
                            alternate_level = spell_info['Classes'][class_name][1][0]
                            alternate_subtype = spell_info['Classes'][class_name][1][1]
                            db_cursor.execute("INSERT INTO spell_class VALUES(NULL, ?, ?, ?, ?)",
                                              (class_id, spell_id, alternate_level, alternate_subtype))
                        else:
                            classe_subtype = spell_info['Classes'][class_name][1]
                            db_cursor.execute("INSERT INTO spell_class VALUES(NULL, ?, ?, ?, ?)",
                                              (class_id, spell_id, level, classe_subtype))
                    else:
                        db_cursor.execute("INSERT INTO spell_class VALUES(NULL, ?, ?, ?, NULL)",
                                          (class_id, spell_id, level))
                # Don't forget to handle the Divine Savant subtype edge case
            else:
                # Domains
                db_cursor.execute("SELECT id FROM domain_feat WHERE name = ? LIMIT 1", (class_name,))
                domain_id = db_cursor.fetchone()[0]
                for level in spell_info['Classes'][class_name][0]:
                    db_cursor.execute("INSERT INTO spell_domain_feat VALUES(NULL, ?, ?, ?)",
                                      (domain_id, spell_id, level))


all_descriptors = []

tables = ['spell', 'spell_class', 'class', 'spell_domain_feat', 'domain_feat']
tables.extend(['book', 'spell_book', 'school', 'spell_school', 'subschool'])
tables.extend(['spell_subschool', 'descriptor', 'spell_descriptor', 'component'])
tables.extend(['spell_component', 'alt_spell', 'web_abbrev'])

db_conn = sqlite3.connect('spells.db')
db_conn.text_factory = str
db_cursor = db_conn.cursor()

db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_results = db_cursor.fetchall()
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


preload_tables(db_cursor)
db_conn.commit()


"""
    Now let's parse the spell list! :D
"""
alt_spells = []
all_spells_file = open('data/all-spells.txt', 'r')
spell = []

all_spells_file = list(all_spells_file)
line_count = 0
for line in all_spells_file:
    #End of the file
    line_count += 1
    per = line_count / float(len(all_spells_file)) * 100
    stdout.write("\rLoading: %d%%" % per)
    stdout.flush()
    if re.match('\-+', line):
        break

    line = re.sub(" +$", "", line)

    if not line.strip():
        spell_info = parse_spell(spell, alt_spells, all_descriptors)
        if spell_info:
            insert_into_spell_db(db_cursor, spell_info)
            db_conn.commit()
        del spell[:]
        #break
        continue
    spell.append(line)
print " COMPLETE"

# We need to stick these in after the fact.
for spell in alt_spells:
    db_cursor.execute("SELECT id FROM alt_spell WHERE alt_spell_name = ?", (spell[0],))
    if not db_cursor.fetchone():
        db_cursor.execute("SELECT id FROM spell WHERE name = ?", (spell[1],))
        spell_id = db_cursor.fetchone()
        if spell_id:
            db_cursor.execute("INSERT INTO alt_spell VALUES(NULL, ?, ?)", (spell[0], spell_id[0]))
            db_conn.commit()

#db_cursor.execute("SELECT name FROM class")
#books = list(db_cursor.fetchall())

#for book in range(len(books)):
#    books[book] = books[book][0]
#for book in sorted(books):
#    print book

db_cursor.close()
db_conn.close()
