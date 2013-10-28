#!/usr/bin/env python
# -*- coding: utf8 -*
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
import re
from sys import exit, stdout


class colorz:
  PURPLE = '\033[95m'
  BLUE = '\033[94m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  RED = '\033[91m'
  GREY = '\033[90m'
  CYAN = '\033[96m'
  WHITE = '\033[97m'
  ENDC = '\033[0m'


def table_setup(name, db_cursor):
  if(name == 'spell'):
    db_cursor.execute("CREATE TABLE spell\
      (id INTEGER PRIMARY KEY, name TINYTEXT,\
      cast_time TINYTEXT, range TINYTEXT,\
      target TINYTEXT, effect TINYTEXT, area TINYTEXT, duration TINYTEXT,\
      saving_throw TINYTEXT, spell_resist TINYTEXT, description TINYTEXT)")

  elif(name == 'class'):
    db_cursor.execute("CREATE TABLE class (\
      id INTEGER PRIMARY KEY, name TINYTEXT,\
      arcane INT, divine INT, base_class INT,\
      setting TINYTEXT, frequency TINYTEXT,\
      more_common INT)")

  elif(name == 'spell_class'):
    db_cursor.execute("CREATE TABLE spell_class (\
      id INTEGER PRIMARY KEY, class_id INT,\
      spell_id INT, level INT, subtype TINYTEXT)")

  elif(name == 'domain_feat'):
    db_cursor.execute("CREATE TABLE domain_feat (\
      id INTEGER PRIMARY KEY, name TINYTEXT, domain INT,\
      feat INT, setting TINYTEXT, book TINYTEXT)")

  elif(name == 'spell_domain_feat'):
    db_cursor.execute("CREATE TABLE spell_domain_feat (\
      id INTEGER PRIMARY KEY, domain_feat_id INT,\
      spell_id INTEGER, level INT)")

  elif(name == 'class_domain_feat'):
    db_cursor.execute("CREATE TABLE class_domain_feat (\
      id INTEGER PRIMARY KEY, domain_feat_id INT,\
      class_id INT)")

  elif(name == 'book'):
    db_cursor.execute("CREATE TABLE book (\
      id INTEGER PRIMARY KEY, name TINYTEXT)")

  elif(name == 'spell_book'):
    db_cursor.execute("CREATE TABLE spell_book (\
      id INTEGER PRIMARY KEY, book_id INT,\
      spell_id INT, page INT)")

  elif(name == 'class_book'):
    db_cursor.execute("CREATE TABLE class_book (\
      id INTEGER PRIMARY KEY, book_id INT,\
      class_id INT)")

  elif(name == 'domain_feat_book'):
    db_cursor.execute("CREATE TABLE domain_feat_book (\
      id INTEGER PRIMARY KEY, book_id INT,\
      domain_feat_id INT)")

  elif (name == 'setting'):
    db_cursor.execute("CREATE TABLE setting (\
      id INTEGER PRIMARY KEY, name TINYTEXT,\
      short_hand TINYTEXT)")

  elif (name == 'book_setting'):
    db_cursor.execute("CREATE TABLE book_setting (\
      id INTEGER PRIMARY KEY, setting_id INT,\
      book_id INT)")

  elif (name == 'class_setting'):
    db_cursor.execute("CREATE TABLE class_setting (\
      id INTEGER PRIMARY KEY, setting_id INT,\
      class_id INT)")

  elif (name == 'domain_feat_setting'):
    db_cursor.execute("CREATE TABLE domain_feat_setting (\
      id INTEGER PRIMARY KEY, setting_id INT,\
      domain_feat_id INT)")

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
      id INTEGER PRIMARY KEY, name TINYTEXT,\
      spell_id INT)")

def preload_tables(db_cursor):
  """
  Let's preload some of the tables:
  """
  #Load up all domains and feats

  #Add in the normal spell components
  spell_components = {
  'None': 'None',
  'V': 'Verbal',
  'S': 'Somatic',
  'M': 'Material',
  'F': 'Focus',
  'DF': 'Divine Focus',
  'XP': 'XP Cost',
  'T': 'Truename',
  'BV': 'Bard only verbal',
  'Fiend': 'Fiend',
  'Corrupt': 'Corrupt',
  'Demon': 'Demon',
  'Essentia': 'Essentia',
  'Coldfire': 'Coldfire',
  'Sacrifice': 'Sacrifice',
  'Drow': 'Drow',
  'Shifter': 'Shifter',
  'Archon': 'Archon',
  'Abstinence': 'Abstinence',
  'Frostfell': 'Frostfell',
  'Drug': 'Drug',
  'Undead': 'Undead',
  'Dragon Magic': 'Dragon Magic',
  'Soul': 'Soul',
  'Celestial': 'Celestial',
  'Disease': 'Disease',
  'Dwarf': 'Dwarf',
  'Devil': 'Devil',
  'Halfling': 'Halfling',
  'Location': 'Location'
  }
  for component_type in spell_components:
  db_cursor.execute("SELECT id FROM component WHERE short_hand = ?", (component_type,))
  if not db_cursor.fetchone():
    db_cursor.execute("INSERT INTO component VALUES (NULL, ?, ?)",
        (spell_components[component_type], component_type))

  # Preload classes
  class_file = csv.reader(open('data/classes.csv', 'rU'), delimiter=";", quotechar='"')
  class_file.next()
  for line in class_file:
  db_cursor.execute("SELECT id FROM class WHERE name = ?", (line[0], ))
  if not db_cursor.fetchone():
    db_cursor.execute("INSERT INTO class VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
        (line[0], line[1], line[2], line[3], line[4], line[6], line[7]))
  db_cursor.execute("SELECT id FROM class WHERE name = ?", (line[0], ))
  class_id = db_cursor.fetchone()[0]

  db_cursor.execute("SELECT id FROM book WHERE name = ?", (line[6], ))
  if not db_cursor.fetchone():
    db_cursor.execute("INSERT INTO book VALUES (NULL, ?)", (line[6], ))
  db_cursor.execute("SELECT id FROM book WHERE name = ?", (line[6], ))
  book_id = db_cursor.fetchone()[0]

  db_cursor.execute("INSERT INTO class_book VALUES (NULL, ?, ?)",
        (book_id, class_id))

  # Preload domains and feats
  domain_feat_file = csv.reader(open('data/domain_feat.csv', 'rU'), delimiter=";", quotechar='"')
  domain_feat_file.next()
  for line in domain_feat_file:
  db_cursor.execute("SELECT id FROM domain_feat WHERE name = ?", (line[0], ))
  if not db_cursor.fetchone():
    db_cursor.execute("INSERT INTO domain_feat VALUES (NULL, ?, ?, ?, ?, ?)",
      (line[0], line[1], line[2], line[4], line[5]))
    db_cursor.execute("SELECT id FROM domain_feat WHERE name = ?", (line[0], ))
    domain_feat_id = db_cursor.fetchone()[0]
    if line[3] == 'Any':
    class_ids = [0]
    elif line[3] == 'Cleric':
    db_cursor.execute("SELECT id FROM class where name = 'Cleric'")
    class_ids = [db_cursor.fetchone()[0]]
    db_cursor.execute("SELECT id FROM class where name = 'Cloistered Cleric'")
    class_ids.append(db_cursor.fetchone()[0])
    else:
    db_cursor.execute("SELECT id FROM class where name = ?", (line[3], ))
    class_ids = [db_cursor.fetchone()[0]]

    for class_id in class_ids:
    db_cursor.execute("INSERT INTO class_domain_feat VALUES (NULL, ?, ?)",
          (domain_feat_id, class_id))

########################################################
#      PRINT FULL SPELL DESCRIPTION        #
# Prints out full desctiption to stdout. Complete with #
# color. Based off general use method          #
########################################################

def full_spell_description(db_cursor, spell_id):
  header_color = colorz.BLUE
  text_color = colorz.WHITE

  #################
  # Name and Book #
  #################
  db_cursor.execute("SELECT name FROM spell WHERE id = ?", (spell_id, ))
  spell_name = db_cursor.fetchone()[0]
  db_cursor.execute("SELECT book_id, page FROM spell_book WHERE spell_id = ?", (spell_id,))
  book_meta_info = db_cursor.fetchall()
  spell_books = []
  for book in book_meta_info:
    book = list(book)
    db_cursor.execute("SELECT name FROM book WHERE id = ?", (book[0],))
    book[0] = db_cursor.fetchone()[0]
    if book[1]:
      book[1] = str(book[1])
      book[1] = "(pg %s)" % book[1]
    else:
      book[1] = ''
    book = " ".join(book).strip()
    spell_books.append(book)
  stdout.write("  %s%s %s[%s]%s\n" % (text_color, spell_name, colorz.GREY, ", ".join(spell_books), colorz.ENDC))

  #####################################
  # School, subschool, and descriptor #
  #####################################
  db_cursor.execute("SELECT school_id FROM spell_school WHERE spell_id = ?", (spell_id,))
  school_meta_info = db_cursor.fetchall()
  spell_schools = []
  for school in school_meta_info:
    school_id = school[0]
    db_cursor.execute("SELECT name FROM school WHERE id = ?", (school_id,))
    spell_schools.append(db_cursor.fetchone()[0])
  stdout.write("%s%s%s" % (text_color, "/".join(spell_schools), colorz.GREY))

  db_cursor.execute("SELECT subschool_id FROM spell_subschool WHERE spell_id = ?", (spell_id,))
  subschool_meta_info = db_cursor.fetchall()
  if subschool_meta_info:
    spell_subschools = []
    for subschool in subschool_meta_info:
      subschool_id = subschool[0]
      db_cursor.execute("SELECT name FROM subschool WHERE id = ?", (subschool_id,))
      spell_subschools.append(db_cursor.fetchone()[0])
    stdout.write(" (%s)" % ", ".join(spell_subschools))

  db_cursor.execute("SELECT descriptor_id FROM spell_descriptor WHERE spell_id = ?", (spell_id,))
  descriptor_meta_info = db_cursor.fetchall()
  if descriptor_meta_info:
    spell_descriptors = []
    for descriptor in descriptor_meta_info:
      descriptor_id = descriptor[0]
      db_cursor.execute("SELECT name FROM descriptor WHERE id = ?", (descriptor_id,))
      spell_descriptors.append(db_cursor.fetchone()[0])
    stdout.write(" [%s]" % ", ".join(spell_descriptors))
  stdout.write("\n%s" % (colorz.ENDC))

  ############################
  # Classes and spell levels #
  ############################
  # Class #
  db_cursor.execute("SELECT class_id, level, subtype FROM spell_class WHERE spell_id = ?", (spell_id,))
  class_meta_info = db_cursor.fetchall()
  spell_classes = []
  for character_class in class_meta_info:
    class_id = character_class[0]
    db_cursor.execute("SELECT name FROM class WHERE id = ?", (class_id,))
    if character_class[2]:
      spell_classes.append(" ".join([db_cursor.fetchone()[0], "(%s)" % character_class[2], str(character_class[1])]))
    else:
      spell_classes.append(" ".join([db_cursor.fetchone()[0], str(character_class[1])]))
  # Domain #
  db_cursor.execute("SELECT domain_feat_id, level FROM spell_domain_feat WHERE spell_id = ?", (spell_id,))
  class_meta_info = db_cursor.fetchall()
  for character_class in class_meta_info:
    class_id = character_class[0]
    db_cursor.execute("SELECT name FROM domain_feat WHERE id = ?", (class_id,))
    spell_classes.append(" ".join([db_cursor.fetchone()[0], str(character_class[1])]))
  spell_classes = sorted(spell_classes)
  stdout.write("%sLevel:%s %s%s\n" % (header_color, text_color, ", ".join(spell_classes), colorz.ENDC))

  #####################
  # Spell Componentes #
  #####################
  db_cursor.execute("SELECT component_id FROM spell_component WHERE spell_id = ?", (spell_id,))
  component_meta_info = db_cursor.fetchall()
  spell_components = []
  if component_meta_info:
    for component_id in component_meta_info:
      component_id = component_id[0]
      db_cursor.execute("SELECT short_hand FROM component WHERE id = ?", (component_id,))
      spell_components.append(db_cursor.fetchone()[0])
    stdout.write("%sComponents:%s %s%s\n" % (header_color, text_color, ", ".join(spell_components), colorz.ENDC))


  #####################
  # Spell Description #
  #####################
  db_cursor.execute("SELECT * FROM spell WHERE id = ?", (spell_id,))
  spell_meta_info = db_cursor.fetchone()
  if spell_meta_info[2]:
    stdout.write("%sCasting Time:%s %s%s\n" % (header_color, text_color, spell_meta_info[2], colorz.ENDC))
  if spell_meta_info[3]:
    stdout.write("%sRange:%s %s%s\n" % (header_color, text_color, spell_meta_info[3], colorz.ENDC))
  if spell_meta_info[4]:
    stdout.write("%sTarget:%s %s%s\n" % (header_color, text_color, spell_meta_info[4], colorz.ENDC))
  if spell_meta_info[5]:
    stdout.write("%sEffect:%s %s%s\n" % (header_color, text_color, spell_meta_info[5], colorz.ENDC))
  if spell_meta_info[6]:
    stdout.write("%sArea:%s %s%s\n" % (header_color, text_color, spell_meta_info[6], colorz.ENDC))
  if spell_meta_info[7]:
    stdout.write("%sDuration:%s %s%s\n" % (header_color, text_color, spell_meta_info[7], colorz.ENDC))
  if spell_meta_info[8]:
    stdout.write("%sSaving Throw:%s %s%s\n" % (header_color, text_color, spell_meta_info[8], colorz.ENDC))
  if spell_meta_info[9]:
    stdout.write("%sSpell Resistance:%s %s%s\n" % (header_color, text_color, spell_meta_info[9], colorz.ENDC))
  if spell_meta_info[10]:
    stdout.write("  %s%s%s\n" % (text_color, spell_meta_info[10], colorz.ENDC))

  stdout.write("\n")

#######################################################
#                       CREATE                        #
#######################################################

# Remember to skip domains
def insert_spell_class(db_cursor, class_info, spell_name, spell_id):
  for class_name in class_info:
    db_cursor.execute("SELECT id FROM class WHERE name = ? LIMIT 1", (class_name,))
    if not db_cursor.fetchone():
      db_cursor.execute("SELECT id FROM domain_feat WHERE name = ? LIMIT 1", (class_name,))
      if not db_cursor.fetchone():
        db_cursor.execute("INSERT INTO class VALUES(NULL, ?, 0, 0, NULL, NULL, NULL, NULL)", (class_name,))
        print "\n%s New Class added: %s from %s%s" % (colorz.RED, class_name, spell_name, colorz.ENDC)

    db_cursor.execute("SELECT id FROM class WHERE name = ? LIMIT 1", (class_name,))
    class_id = db_cursor.fetchone()
    if class_id:
      #Classes
      class_id = class_id[0]
      for level in class_info[class_name][0]:
        #Don't forget to store subtypes
        if len(class_info[class_name]) == 2:
          # This is only for Savant which has a different level
          # for divine spells
          if isinstance(class_info[class_name][1], list):
            db_cursor.execute("INSERT INTO spell_class VALUES(NULL, ?, ?, ?, NULL)",
                      (class_id, spell_id, level))
            alternate_level = class_info[class_name][1][0]
            alternate_subtype = class_info[class_name][1][1]
            db_cursor.execute("INSERT INTO spell_class VALUES(NULL, ?, ?, ?, ?)",
                      (class_id, spell_id, alternate_level, alternate_subtype))
          else:
            classe_subtype = class_info[class_name][1]
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
      for level in class_info[class_name][0]:
        db_cursor.execute("INSERT INTO spell_domain_feat VALUES(NULL, ?, ?, ?)",
                  (domain_id, spell_id, level))

def insert_spell_book(db_cursor, book_info, spell_name, spell_id):
  for book in book_info:
    db_cursor.execute("SELECT id FROM book WHERE name = ? LIMIT 1", (book[0],))
    book_id = db_cursor.fetchone()
    if not book_id:
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

def insert_spell_component(db_cursor, component_info, spell_name, spell_id):
  for component in component_info:
    db_cursor.execute("SELECT id from component WHERE short_hand = ? LIMIT 1",
             (component,))
    component_id = db_cursor.fetchone()
    if not component_id:
      print "\n%s" % spell_name
      print "%s New component type added: %s%s" % (colorz.RED, component, colorz.ENDC)
      db_cursor.execute("INSERT INTO component VALUES(NULL, NULL, ?)",
               (component,))
      db_cursor.execute("SELECT id from component WHERE short_hand = ? LIMIT 1",
               (component,))
      component_id = db_cursor.fetchone()
    component_id = component_id[0]
    db_cursor.execute("INSERT INTO spell_component VALUES(NULL, ?, ?)",
              (component_id, spell_id))

def insert_spell_school(db_cursor, school_info, spell_id):
  for school in school_info:
    db_cursor.execute("SELECT id FROM school WHERE name = ? LIMIT 1", (school,))
    school_id = db_cursor.fetchone()
    if not db_cursor.fetchone():
      db_cursor.execute("INSERT INTO school VALUES(NULL, ?)", (school,))
      db_cursor.execute("SELECT id FROM school WHERE name = ? LIMIT 1", (school,))
      school_id = db_cursor.fetchone()
    school_id = school_id[0]
    db_cursor.execute("INSERT INTO spell_school VALUES(NULL, ?, ?)", (school_id, spell_id))

def insert_spell_subschool(db_cursor, subschool_info, spell_id):
  for subschool in subschool_info:
    db_cursor.execute("SELECT id FROM subschool WHERE name = ? LIMIT 1", (subschool,))
    subschool_id = db_cursor.fetchone()
    if not db_cursor.fetchone():
      db_cursor.execute("INSERT INTO subschool VALUES(NULL, ?)", (subschool,))
      db_cursor.execute("SELECT id FROM subschool WHERE name = ? LIMIT 1", (subschool,))
      subschool_id = db_cursor.fetchone()
    subschool_id = subschool_id[0]
    db_cursor.execute("INSERT INTO spell_subschool VALUES(NULL, ?, ?)", (subschool_id, spell_id))

def insert_spell_descriptor(db_cursor, descriptor_info, spell_id):
  for descriptors in descriptor_info:
    db_cursor.execute("SELECT id FROM descriptor WHERE name = ? LIMIT 1", (descriptors,))
    descriptor_id = db_cursor.fetchone()
    if not db_cursor.fetchone():
      db_cursor.execute("INSERT INTO descriptor VALUES(NULL, ?)", (descriptors,))
      db_cursor.execute("SELECT id FROM descriptor WHERE name = ? LIMIT 1", (descriptors,))
      descriptor_id = db_cursor.fetchone()
    descriptor_id = descriptor_id[0]
    db_cursor.execute("INSERT INTO spell_descriptor VALUES(NULL, ?, ?)", (descriptor_id, spell_id))

# You should populate the spell first so you can populate other tables
# and link tables as we go
def insert_spell_into_db(db_cursor, spell_info):
  # Initial spell insert:
  db_cursor.execute("SELECT id from spell WHERE name = ? LIMIT 1", (spell_info['Name'],))
  if not db_cursor.fetchone():
    db_cursor.execute("INSERT INTO spell VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (spell_info['Name'],
               spell_info['casting_time'],
               spell_info['range'],
               spell_info['target'],
               spell_info['effect'],
               spell_info['area'],
               spell_info['duration'],
               spell_info['saving_throw'],
               spell_info['spell_resistance'],
               spell_info['description']))
    db_cursor.execute("SELECT id from spell WHERE name = ? LIMIT 1", (spell_info['Name'],))
    spell_id = db_cursor.fetchone()[0]

    # Let's populate reference tables as we go:
    ## COMPONENTS ##
    insert_spell_component(db_cursor, spell_info['components'], spell_info['Name'], spell_id)

    ## BOOK ##
    insert_spell_book(db_cursor, spell_info['Books'], spell_id)

    ## School ##
    insert_spell_school(db_cursor, spell_info['Schools'], spell_id)

    ## Subschools ##
    insert_spell_subschool(db_cursor, spell_info['Subschools'], spell_id)
  
    ## Descriptors ##
    insert_spell_descriptor(db_cursor, spell_info['Descriptors'], spell_id)
  
    ## Classes ##
    import_spell_class(db_cursor, spell_info['Classes'], spell_info['Name'], spell_id)

def insert_alt_spell_into_db(db_cursor, spell_info):
  db_cursor.execute("SELECT id FROM alt_spell WHERE name = ?", (spell_info["Name"],))
  if not db_cursor.fetchone():
    db_cursor.execute("SELECT id FROM spell WHERE name = ?", (spell_info["alt_spell_name"],))
    spell_id = db_cursor.fetchone()
    if spell_id:
      db_cursor.execute("INSERT INTO alt_spell VALUES(NULL, ?, ?)", (spell_info["Name"], spell_id[0]))
      db_conn.commit()