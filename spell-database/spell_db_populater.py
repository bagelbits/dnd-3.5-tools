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
from spell_db_controller import table_setup, insert_spell_into_db, insert_alt_spell_into_db, preload_tables


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
      "Spellsinger",
      "Flame Steward"
    ]
    if character_class[0] in classes_to_subtype:
      character_class[1] = character_class[1][:-1]
    else:
      character_class = [" (".join(character_class)]
  else:
    character_class = [character_class]

  return character_class


##############################
#    Spell Parsing     #
##############################

def get_book_info(book_info):
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


def parse_spell(spell, alt_spells):
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
          'components': '',
         }

  spell_line = spell.pop(0).strip()

  #Handle the See "this spell" for info cases
  match = re.search('See "(.+)"', spell[0])
  if match:
    spell_info = {'Name': spell_line.strip(),
            'alt_spell_name': match.group(1),
           }
    return spell_info

  # First get the spell name and book with page number
  match = re.search('(.+) \[(.+)\]', spell_line)
  spell_info['Name'] = match.group(1)
  #print spell_info['Name']
  spell_info['Books'] = get_book_info(match.group(2))

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
    if spell[0].startswith('  '):
      break
    # Magically, you have no description
    if len(spell) == 0:
      break

    spell_line = spell.pop(0).strip()

    spell_descriptor = re.match("(\w+( \w+)*): ", spell_line).group(1).lower()
    spell_descriptor = re.sub(" +", "_", spell_descriptor)
    if spell_descriptor not in spell_info:
      print "%s New Descriptor found: %s%s" % (colorz.RED, spell_descriptor, colorz.ENDC)
    spell_line = re.sub("\w+( \w+)*: ", '', spell_line, count=1)
    spell_info[spell_descriptor] = spell_line

  #Now stich together the rest of the description
  spell_info['description'] = "".join(spell).strip()

  if spell_info['components']:
    spell_info['components'] = spell_info['components'].split(", ")

  return spell_info

tables = ['spell', 'spell_class', 'class', 'spell_domain_feat', 'domain_feat']
tables.extend(['class_domain_feat', 'book', 'spell_book', 'school', 'spell_school'])
tables.extend(['subschool', 'spell_subschool', 'descriptor', 'spell_descriptor'])
tables.extend(['component', 'spell_component', 'alt_spell', 'class_book'])
tables.extend(['domain_feat_book', 'setting', 'book_setting', 'class_setting'])
tables.extend(['domain_feat_setting'])


db_conn = sqlite3.connect('spells.db')
db_conn.text_factory = str
db_cursor = db_conn.cursor()

db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_results = db_cursor.fetchall()
print "%sSetting up tables...%s" % (colorz.BLUE, colorz.ENDC)
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

print "%sPreloading tables...%s" % (colorz.BLUE, colorz.ENDC)
preload_tables(db_cursor)
db_conn.commit()


"""
  Now let's parse the spell list! :D
"""
print "%sParsing and loading into db....%s" % (colorz.BLUE, colorz.ENDC)
alt_spells = []
all_spells_file = open('data/all-spells.txt', 'r')
spell = []

all_spells_file = list(all_spells_file)
line_count = 0
for line in all_spells_file:
  #End of the file
  line_count += 1
  per = line_count / float(len(all_spells_file)) * 100
  stdout.write("%s\rLoading: %d%%%s" % (colorz.YELLOW, per, colorz.ENDC))
  stdout.flush()

  #This may be useless now
  if re.match('\-+', line):
    break

  line = re.sub(" +$", "", line)

  if not line.strip():
    spell_info = parse_spell(spell, alt_spells)
    if "alt_spell_name" in spell_info:
      alt_spells.append(spell_info)
    else:
      insert_spell_into_db(db_cursor, spell_info)
      db_conn.commit()
    del spell[:]
    #break
    continue
  spell.append(line)
print "%s COMPLETE%s" % (colorz.YELLOW, colorz.ENDC)

# We need to stick these in after the fact.
for spell in alt_spells:
  insert_alt_spell_into_db(db_cursor, spell)


db_cursor.close()
db_conn.close()
