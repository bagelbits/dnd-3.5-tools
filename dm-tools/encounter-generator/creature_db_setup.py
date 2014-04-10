#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
  Hacked together random CR encounter generator.
  No GUI planned.

  Written by Christopher Durien Ward
  With help from Noah Reson-Brown

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

from sys import stdout
import assets.dmg_tables as dmg_tables
import sqlite3
import csv
import traceback
import os
import re

standardize_list = []

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

#################################################
#               UTILITY FUNCTIONS               #
#################################################

def stitch_split_parens(level_lines):
  level_lines = re.split(', ', level_lines)
  level_lines = filter(None, level_lines)
  paran_sections = []
  for pos in range(len(level_lines)):
    if "(" in level_lines[pos] and ")" not in level_lines[pos]:
      paran_sections.append([pos])
    if "(" not in level_lines[pos] and ")" in level_lines[pos]:
      paran_sections[-1].append(pos)
  for section in reversed(paran_sections):
    level_lines[section[0]:section[1]+1] = [', '.join(level_lines[section[0]:section[1]+1])]
  return level_lines

def replace_outside_parens(level_lines, to_find, replacement, put_back):
  level_lines = re.split(to_find, level_lines)
  level_lines = filter(None, level_lines)
  paran_sections = []
  for pos in range(len(level_lines)):
    if "(" in level_lines[pos] and ")" not in level_lines[pos]:
      paran_sections.append([pos])
    if "(" not in level_lines[pos] and ")" in level_lines[pos]:
      paran_sections[-1].append(pos)
  for section in reversed(paran_sections):
    level_lines[section[0]:section[1]+1] = [put_back.join(level_lines[section[0]:section[1]+1])]
  level_lines = replacement.join(level_lines)
  return level_lines.replace(',,', ',')

#TODO: Implement this!
def print_creature_stats(db_cursor, creature_meta_data):
  pass

def get_same_cr_total(creature_cr, number):
  if re.search(r'^\d+$', creature_cr):
    creature_cr = int(creature_cr)

  if number < 1:
    raise Exception("Number of creatures less than 1")
  elif number == 1:
    return creature_cr
  elif number in range(5,7):
    number = 5
  elif number in range(7,10):
    number = 6
  elif number > 9:
    number = 7

  # Account for weird creature cr
  if creature_cr < 5:
    for row in sorted(dmg_tables.weird_same_cr.keys()):
      if isinstance(dmg_tables.weird_same_cr[row][number - 2], list):
        continue
      if dmg_tables.weird_same_cr[row][number - 2] == creature_cr:
        return row

  if isinstance(creature_cr, str):
    creature_cr = int(creature_cr.split('/')[1])
    number -= 1
    creature_cr -= number
    creature_cr = '1/%d' % creature_cr
    return creature_cr

  return int(creature_cr) + number

#TODO: Implement this!
def get_mixed_cr_total():
  pass

def de_plural_creature_name(creature_name):
  if re.search('wolves', creature_name):
    creature_name = re.sub('wolves', 'wolf', creature_name)

  creature_name = re.sub('s$', '', creature_name)

  creature_name = re.sub('frost giant', 'giant, frost', creature_name)

  return creature_name

#################################################
#             DATABASE MANAGEMENT               #
#################################################

#TODO: Add a flag for organizations to skip
def table_setup(name, db_cursor):
  if name == 'creature':
    db_cursor.execute("CREATE TABLE creature(\
      id INTEGER PRIMARY KEY, name TINYTEXT, cr TINYTEXT)")

  elif name == 'book':
    db_cursor.execute("CREATE TABLE book(\
      id INTEGER PRIMARY KEY, name TINYTEXT,\
      short_hand TINYTEXT)")

  elif name == 'creature_book':
    db_cursor.execute("CREATE TABLE creature_book(\
      creature_id INTEGER, book_id INTEGER, page INTEGER,\
      FOREIGN KEY (creature_id) REFERENCES creature(id),\
      FOREIGN KEY (book_id) REFERENCES book(id))")

  elif name == 'type':
    db_cursor.execute("CREATE TABLE type(\
      id INTEGER PRIMARY KEY, name TINYTEXT)")

  elif name == 'creature_type':
    db_cursor.execute("CREATE TABLE creature_type(\
      creature_id INTEGER, type_id INTEGER,\
      FOREIGN KEY (creature_id) REFERENCES creature(id),\
      FOREIGN KEY (type_id) REFERENCES type(id))")

  elif name == 'subtype':
    db_cursor.execute("CREATE TABLE subtype(\
      id INTEGER PRIMARY KEY, name TINYTEXT)")

  elif name == 'creature_subtype':
    db_cursor.execute("CREATE TABLE creature_subtype(\
      creature_id INTEGER, subtype_id INTEGER,\
      FOREIGN KEY (creature_id) REFERENCES creature(id),\
      FOREIGN KEY (subtype_id) REFERENCES subtype(id))")

  elif name == 'alignment':
    db_cursor.execute("CREATE TABLE alignment(\
      subtype_id INTEGER, opposing_id INTEGER,\
      FOREIGN KEY (subtype_id) REFERENCES subtype(id),\
      FOREIGN KEY (opposing_id) REFERENCES subtype(id))")

  elif name == 'element':
    db_cursor.execute("CREATE TABLE element(\
      subtype_id INTEGER,\
        FOREIGN KEY (subtype_id) REFERENCES subtype(id))")

  elif name == 'size':
    db_cursor.execute("CREATE TABLE size(\
      id INTEGER PRIMARY KEY, name TINYTEXT)")

  elif name == 'creature_size':
    db_cursor.execute("CREATE TABLE creature_size(\
      creature_id INTEGER, size_id INTEGER,\
      FOREIGN KEY (creature_id) REFERENCES creature(id),\
      FOREIGN KEY (size_id) REFERENCES size(id))")

  #TODO: Break this shit apart
  elif name == 'creature_stat':
    db_cursor.execute("CREATE TABLE creature_stat(\
      id INTEGER PRIMARY KEY, creature_id INTEGER,\
      hit_dice TINYTEXT, initiative INTEGER, speed TINYTEXT,\
      armor_class TINYTEXT, bab INTEGER, grapple TINYTEXT,\
      attack TINYTEXT, full_attack TINYTEXT, space TINYTEXT,\
      reach TINYTEXT, special_attacks TINYTEXT,\
      special_qualities TINYTEXT, saves TINYTEXT, abilities TINYTEXT,\
      skills TINYTEXT, feats TINYTEXT, environment TINYTEXT,\
      organization TINYTEXT, treasure TINYTEXT, alignment TINYTEXT,\
      advancement TINYTEXT, la TINYTEXT, description TINYTEXT,\
      ability_descriptions TINYTEXT, books TINYTEXT,\
      FOREIGN KEY (creature_id) REFERENCES creature(id))")

  elif name == 'creature_group':
    db_cursor.execute("CREATE TABLE creature_group(\
      id INTEGER PRIMARY KEY, cr TINYTEXT,\
        min_creature_total INTEGER, max_creature_total INTEGER,\
        group_name TINYTEXT, main_creature_id INTEGER,\
        non_combat BOOLEAN,\
        FOREIGN KEY (main_creature_id) REFERENCES creature(id))")

  elif name == 'creature_group_contents':
    db_cursor.execute("CREATE TABLE creature_group_contents(\
      creature_group_id INTEGER, creature_id INTEGER, min_quantity INTEGER,\
      max_quantity INTEGER,\
      FOREIGN KEY (creature_group_id) REFERENCES creature_group(id),\
      FOREIGN KEY (creature_id) REFERENCES creature(id))")

def insert_creature(db_cursor, line):

  db_cursor.execute('SELECT id FROM creature WHERE name = ? LIMIT 1', (line[0],))
  if db_cursor.fetchone():
    db_cursor.execute('SELECT id FROM creature WHERE name = ? AND cr = ? LIMIT 1',
      (line[0],line[4]))
    if db_cursor.fetchone():
      return
    else:
      #TODO: Print these after progress tracker
      print " Potentially conflicting creatures: %s" % line[0]

  # Load in creature
  db_cursor.execute('INSERT INTO creature VALUES(NULL, ?, ?)', (line[0], line[4]))

  db_cursor.execute('SELECT id FROM creature WHERE name = ? AND cr = ? LIMIT 1',
    (line[0],line[4]))
  creature_id = db_cursor.fetchone()[0]

  # Link Books
  db_cursor.execute('SELECT id FROM book WHERE short_hand = ? LIMIT 1', (line[1],))
  book_id = db_cursor.fetchone()[0]

  db_cursor.execute('INSERT INTO creature_book VALUES(?, ?, ?)',
    (creature_id, book_id, line[2]))

  # Load main type
  main_type = line[3].split(' (')[0]

  db_cursor.execute('SELECT id FROM type WHERE name = ? LIMIT 1', (main_type,))
  if not db_cursor.fetchone():
    #print "%s" % (main_type,)
    db_cursor.execute('INSERT INTO type VALUES(NULL, ?)', (main_type,))
  db_cursor.execute('SELECT id FROM type WHERE name = ? LIMIT 1', (main_type,))
  maint_type_id = db_cursor.fetchone()[0]

  db_cursor.execute('INSERT INTO creature_type VALUES(?, ?)', (creature_id, maint_type_id))

  # Load secondary types
  subtypes = line[3].split(' (')
  if len(subtypes) > 1:
    subtypes = subtypes[1]
    subtypes = subtypes.replace(')', '')
    subtypes = subtypes.split(', ')

    for subtype in subtypes:
      db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (subtype,))
      if not db_cursor.fetchone():
        #print "%s" % (subtype)
        db_cursor.execute('INSERT INTO subtype VALUES (NULL, ?)', (subtype,))
      db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (subtype,))
      subtype_id = db_cursor.fetchone()[0]

      db_cursor.execute('INSERT INTO creature_subtype VALUES(?, ?)',
        (creature_id, subtype_id))

def import_frostfell_creature(db_cursor, line):
  global standardize_list

  # First lets grab the creature id. Or whine if it doesn't exist.
  # We need CR because Aspects are giant goose wangs
  monster_name = line[0].title()
  monster_cr = line[20].split(':')[1].strip()
  db_cursor.execute('SELECT id FROM creature\
                     WHERE name = ? AND cr = ? LIMIT 1',
                     (line[0].title(), monster_cr))
  creature_id = db_cursor.fetchone()
  if not creature_id:
    print "%sBase creature not found: %s%s" % (colorz.RED, line[0].title(), colorz.ENDC)
  else:
    creature_id = creature_id[0]

  # Now lets deal with size
  size = line[1].strip()
  db_cursor.execute('SELECT id FROM size WHERE name = ? LIMIT 1', (size,))
  size_id = db_cursor.fetchone()
  if not size_id:
    print "%sNew size found: %s%s" % (colorz.RED, size, colorz.ENDC)
    db_cursor.execute('INSERT INTO size VALUES(NULL, ?)', (size,))
    db_cursor.execute('SELECT id FROM size WHERE name = ? LIMIT 1', (size,))
    size_id = db_cursor.fetchone()
  size_id = size_id[0]
  db_cursor.execute('INSERT INTO creature_size VALUES(?, ?)',
    (creature_id, size_id))

  #TODO: Come back to this
  hit_dice = line[4].split(':')[1].strip()

  initiative = int(line[5].split(':')[1].strip())
  
  #TODO: Come back to this
  speed = line[6]
  #TODO: Come back to this
  armor_class = line[7]
  
  line[8] = line[8].split(':', 1)[1].strip()
  bab_stat, grapple_stat = [int(x.replace('*', '')) for x in line[8].split('/')]
  attack = line[9]
  full_attack = line[10]

  line[11] = line[11].split(':', 1)[1].strip()
  space, reach = re.split('(?<=ft\.)/', line[11])

  #TODO: Come back to this
  special_attacks = line[12].split(':', 1)[1].strip()
  if special_attacks == '-':
    special_attacks = ''
  
  #TODO: Come back to this
  special_qualities = line[13].split(':', 1)[1].strip()

  #TODO: Come back to this
  saves = line[14].split(':', 1)[1].strip()

  #TODO: Come back to this
  abilities = line[15].split(':', 1)[1].strip()

  #TODO: Come back to this
  skills = line[16].split(':', 1)[1].strip()

  #TODO: Come back to this
  feats = line[17].split(':', 1)[1].strip()

  #TODO: Come back to this
  environment = line[18].split(':', 1)[1].strip()

  #TODO: Come back to this
  organization = line[19].split(':', 1)[1].strip()

  #TODO: Come back to this
  treasure = line[21].split(':', 1)[1].strip()

  #TODO: Comeback to this
  alignment = line[22].split(':', 1)[1].strip()

  #TODO: Comeback to this
  advancement = line[23].split(':', 1)[1].strip()

  #TODO: Comeback to this
  la = line[24].split(':', 1)[1].strip()

  description = line[25]
  ability_descriptions = line[26]

  books = line[27].split(':', 1)[1].strip()
  db_cursor.execute("SELECT book_id FROM creature_book WHERE creature_id = ?",
    (creature_id,))
  stored_book_id = db_cursor.fetchone()[0]
  db_cursor.execute("SELECT id FROM book WHERE name = ?",
    (books,))
  pulled_book_id = db_cursor.fetchone()[0]
  if stored_book_id != pulled_book_id:
    print "%sBook mismatch for %s: %s%s" % (colorz.RED,
      monster_name, books, colorz.ENDC)
  

  # if organization not in standardize_list:
  #   standardize_list.append(organization)
  # test_data = feats.lower().split(', ')
  # for test in test_data:
  #   if test not in standardize_list:
  #     standardize_list.append(test)

  db_cursor.execute('INSERT INTO creature_stat VALUES(NULL, ?, ?, ?, ?, ?, ?,\
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
    (creature_id, hit_dice, initiative, speed, armor_class, bab_stat,
      grapple_stat, attack, full_attack, space, reach, special_attacks,
      special_qualities, saves, abilities, skills, feats, environment,
      organization, treasure, alignment, advancement, la, description,
      ability_descriptions, books))

# Range is as follows:
# 1, 2, 3, 4, 5-6, 7-9, 10-12, 13+
# 13+ gets treated as non-combat and gets same CR as 10-12
def insert_single_group_cr_range(db_cursor, creature_id, creature_cr, group_range, group_name):
  sorted_group_cr = [
    [], #Creature num: 1
    [], #Creature num: 2
    [], #Creature num: 3
    [], #Creature num: 4
    [], #Creature num: 5-6
    [], #Creature num: 7-9
    [], #Creature num: 10-12
    [], #Creature num: 13+
  ]

  for number in group_range:

    if number == 1:
      sorted_group_cr[0].append(number)
    elif number == 2:
      sorted_group_cr[1].append(number)
    elif number == 3:
      sorted_group_cr[2].append(number)
    elif number == 4:
      sorted_group_cr[3].append(number)
    elif number < 7:
      sorted_group_cr[4].append(number)
    elif number < 10:
      sorted_group_cr[5].append(number)
    elif number < 13:
      sorted_group_cr[6].append(number)
    else:
      sorted_group_cr[7].append(number)

  for group in sorted_group_cr:
    if not group:
      continue

    group_cr = get_same_cr_total (creature_cr, group[0])
    group_min = group[0]
    group_max = group[-1]

    combat_group = True
    if group_min > 12:
      combat_group = False

    db_cursor.execute("INSERT INTO creature_group VALUES(NULL, ?, ?, ?, ?, ?, ?)",
      (group_cr, group_min, group_max, group_name, creature_id, combat_group))
    db_cursor.execute("SELECT id FROM creature_group WHERE main_creature_id = ?\
      AND group_name = ?", (creature_id, group_name))
    creature_group_id = db_cursor.fetchone()[0]
    db_cursor.execute("INSERT INTO creature_group_contents VALUES(?, ?, ?, ?)",
      (creature_group_id, creature_id, group_min, group_max))

#NOTE: Rolled CRs are only going to be their standard range
# without any weighted for rolling.
def populate_groups(db_cursor, main_creature_id, org_line):
  global standardize_list

  #Get main creature cr
  db_cursor.execute("SELECT cr FROM creature WHERE id = ?" , (main_creature_id,))
  main_creature_cr = db_cursor.fetchone()[0]

  db_cursor.execute("SELECT name FROM creature WHERE id = ?" , (main_creature_id,))
  main_creature_name = db_cursor.fetchone()[0]
  
  org_line = replace_outside_parens(org_line.lower(), '(?<=[\w\),]) or(?=\s)', ',', ' or')
  org_line = stitch_split_parens(org_line)


  #Lets convert those neat ranges.
  for group in org_line:

    # Pull name from everything not in parens
    group_name = group.split('(', 1)[0].strip()
    
    ###################################
    # Handle soliatry and pairs first #
    ###################################

    if group == 'pair':
      group = 2
    if group == 'mated pair':
      group = 2
    if group == 'solitary':
      group = 1

    if isinstance(group, int):
      quantity = group
      group_cr = get_same_cr_total(main_creature_cr, quantity)
      db_cursor.execute("INSERT INTO creature_group VALUES(NULL, ?, ?, ?, ?, ?, ?)",
        (group_cr, quantity, quantity, group_name, main_creature_id, True))
      db_cursor.execute("SELECT id FROM creature_group WHERE main_creature_id = ?\
        AND group_name = ?", (main_creature_id, group_name))
      creature_group_id = db_cursor.fetchone()[0]
      db_cursor.execute("INSERT INTO creature_group_contents VALUES(?, ?, ?, ?)",
        (creature_group_id, main_creature_id, quantity, quantity))
      continue

    ######################################
    # Next handle single creature groups #
    ######################################

    # Expand dice rolls
    match = re.search(r'(\d+)d(\d+)(\+(\d+)|)', group)
    if match:
      group = [int(match.group(1)), int(match.group(1))*int(match.group(2))]

      if match.group(3):
        group[0] += int(match.group(4))
        group[1] += int(match.group(4))

      group = range(group[0], group[1] + 1)

      insert_single_group_cr_range(db_cursor, main_creature_id, main_creature_cr, group, group_name)
      continue

    # Expand ranges
    match = re.search(r'\((\d+-\d+)\)', group)
    if match:
      group = [int(x) for x in match.group(1).split('-')]
      
      group = range(int(group[0]), int(group[1]) + 1)

      insert_single_group_cr_range(db_cursor, main_creature_id, main_creature_cr, group, group_name)
      continue

    ###########################################
    # Next handle multi-creature groups       #
    # Note: Doesn't handle level advances yet #
    ###########################################
    #TODO: Handle class level advances

    # Let's try and handle general cases.
    group_stats = []
    match = re.search(r'\((.*)\)', group)
    group_contents = match.group(1)
    group_contents = re.split(r' plus | and ', group_contents)
    print "%s: %s" % (group_name, group_contents)

    # First entry always refers to main creature
    match = re.search(r'(\d+(-\d+|))', group_contents[0])
    if match:
      main_creature_quantity = match.group(0)
    else:
      main_creature_quantity = '1'
    print "%s: %s" % (main_creature_name, main_creature_quantity)

    # Now lets get upper and lower bounds of the range
    if '%' in main_creature_quantity:
      print "%sERROR: Percentage symbol in main creature quantity of %s%s" % (
        colorz.RED, main_creature_name, colorz.ENDC)
      return
    if '-' in main_creature_quantity:
      main_creature_quantity = main_creature_quantity.split('-')
      main_creature_quantity = [int(x) for x in main_creature_quantity]
    else:
      main_creature_quantity = [int(main_creature_quantity), int(main_creature_quantity)]

    # Store the stats into a dict for ease of recall
    main_creature_stats = {
      'creature_id' : main_creature_id,
      'creature_name' : main_creature_name,
      'group_size_min' : main_creature_quantity[0],
      'group_size_max' : main_creature_quantity[1],
      'group_name' : group_name,
      'base_cr' : main_creature_cr,
    }

    group_stats.append(main_creature_stats)

    # And then remove the primary creature since it's been processed
    del group_contents[0]

    # Next lets try and get quantities and monster ids for
    # the rest
    for section in group_contents:
      # Let's skip anything with a percentage or class level for now
      #TODO: Handle class level advances
      #TODO: Handle noncombatants
      if '%' in section:
        if group not in standardize_list:
          print "%sPercentage encountered, aborting%s" % (colorz.RED, colorz.ENDC)
          standardize_list.append(group)
          break
      match = re.search(r'[\-\s]level', section)
      if match:
        if group not in standardize_list:
          print "%sClass level increment found, aborting%s" % (colorz.RED, colorz.ENDC)
          standardize_list.append(group)
          break

      # Okay, let's handle the rest
      match = re.search(r'(\d+(-\d+|) )', section)
      creature_quantity = match.group(0)
      creature_name = re.split(creature_quantity, section)[1].strip()

      # Let's see if we can 
      db_cursor.execute("SELECT id FROM creature WHERE lower(name) = lower(?)" , (
        creature_name,))
      creature_id = db_cursor.fetchone()
      
      # We need to depluralize creatures if they are plural
      if not creature_id:
        creature_name = de_plural_creature_name(creature_name)
        db_cursor.execute("SELECT id FROM creature WHERE lower(name) = lower(?)" , (
          creature_name,))
        creature_id = db_cursor.fetchone()
        if not creature_id:
          if group not in standardize_list:
            print "%sCreature not found: %s... aborting%s" % (
              colorz.RED, creature_name.title(), colorz.ENDC)
            standardize_list.append(group)
            break

      print "%s: %s" % (creature_name, creature_quantity)

    
    print ""

  # for group in org_line:
  #   if group not in standardize_list:
  #     standardize_list.append(group)

def preload_tables(db_cursor):
  alignments = [
    ['Evil', 'Good'],
    ['Lawful', 'Chaotic'],
    'Neutral',
  ]

  elements = [
    'Air',
    'Fire',
    'Cold',
    'Earth',
    'Water',
    'Electricity',
    'Shadow',
  ]

  creature_sizes = [
  'Large',
  'Huge',
  'Gargantuan',
  'Colossal',
  'Small',
  'Medium',
  'Tiny',
  ]

  for size in creature_sizes:
    db_cursor.execute('SELECT id FROM size WHERE name = ? LIMIT 1', (size,))
    if not db_cursor.fetchone():
      db_cursor.execute('INSERT INTO size VALUES(NULL, ?)', (size,))

  for element in elements:
    db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (element,))
    if not db_cursor.fetchone():
      db_cursor.execute('INSERT INTO subtype VALUES(NULL, ?)', (element,))
      db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (element,))

      subtype_id = db_cursor.fetchone()[0]
      db_cursor.execute('INSERT INTO element VALUES(?)', (subtype_id,))

  for alignment in alignments:
    if isinstance(alignment, list):
      db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (alignment[0],))
      if not db_cursor.fetchone():
        db_cursor.execute('INSERT INTO subtype VALUES(NULL, ?)', (alignment[0],))
        db_cursor.execute('INSERT INTO subtype VALUES(NULL, ?)', (alignment[1],))

        subtype_ids = []
        db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (alignment[0],))
        subtype_ids.append(db_cursor.fetchone()[0])
        db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (alignment[1],))
        subtype_ids.append(db_cursor.fetchone()[0])

        db_cursor.execute('INSERT INTO alignment VALUES(?, ?)', (subtype_ids[0], subtype_ids[1]))
        db_cursor.execute('INSERT INTO alignment VALUES(?, ?)', (subtype_ids[1], subtype_ids[0]))


    else:
      db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (alignment,))
      if not db_cursor.fetchone():
        db_cursor.execute('INSERT INTO subtype VALUES(NULL, ?)', (alignment,))
        db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (alignment,))

        subtype_id = db_cursor.fetchone()[0]
        db_cursor.execute('INSERT INTO alignment VALUES(?, 0)', (subtype_id,))

def db_setup(reload_db):
  global standardize_list
  tables = ['creature', 'book', 'creature_book', 'type']
  tables.extend(['creature_type', 'subtype', 'creature_subtype'])
  tables.extend(['alignment', 'element', 'creature_stat'])
  tables.extend(['size', 'creature_size', 'creature_group'])
  tables.extend(['creature_group_contents'])

  db_exists = False

  if os.path.isfile('assets/creatures.db') and not reload_db:
    db_exists = True

  db_conn = sqlite3.connect('assets/creatures.db')
  db_conn.text_factory = str
  db_cursor = db_conn.cursor()

  if db_exists:
    return db_conn, db_cursor

  db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
  table_results = db_cursor.fetchall()
  stdout.write("%sSetting up tables..." % colorz.BLUE)
  for table in tables:
    if not any(table == result[0] for result in table_results):
      try:
        table_setup(table, db_cursor)
        db_conn.commit()
      except Exception:
        traceback.print_exc()
        db_cursor.close()
        db_conn.close()
        exit(1)
  print " COMPLETE!%s" % colorz.ENDC

  #Blow out tables on reload
  if os.path.isfile('assets/creatures.db') and reload_db:
    db_cursor.execute("DELETE FROM creature_stat")
    db_cursor.execute("DELETE FROM creature_book")
    db_cursor.execute("DELETE FROM creature_type")
    db_cursor.execute("DELETE FROM creature_subtype")
    db_cursor.execute("DELETE FROM creature_size")
    db_cursor.execute("DELETE FROM creature_group_contents")
    db_cursor.execute("DELETE FROM creature_group")
    db_cursor.execute("DELETE FROM creature")

  stdout.write("%sPopulating tables..." % colorz.BLUE)
  preload_tables(db_cursor)
  print " COMPLETE!%s" % colorz.ENDC

  book_list = csv.reader(open('assets/books.csv', 'rb'),
    delimiter=',', quotechar='"')
  stdout.write("%sLoading books..." % colorz.BLUE)
  for line in book_list:
    db_cursor.execute("SELECT id FROM book WHERE short_hand = ? LIMIT 1", (line[0],))
    if not db_cursor.fetchone():
      db_cursor.execute("INSERT INTO book VALUES(NULL, ?, ?)", (line[1], line[0]))
  db_conn.commit()
  print " COMPLETE!%s" % colorz.ENDC

  monster_list = csv.reader(open('assets/monsters_by_cr.csv', 'rb'),
    delimiter=',', quotechar='"')
  monster_list = list(monster_list)
  monster_list_length = len(monster_list)
  line_count = 0
  for line in monster_list:
    line_count += 1
    per = line_count / float(monster_list_length) * 100
    stdout.write('\r%sLoading monsters... %d%%%s' % (colorz.BLUE, per, colorz.ENDC))
    stdout.flush()
    insert_creature(db_cursor, line)
    db_conn.commit()

  monster_list = csv.reader(open('assets/Frostburn_Monsters2014-02-03 01-24-09.csv', 'rb'),
    delimiter=',', quotechar='"')
  monster_list.next()
  monster_list = list(monster_list)
  monster_list_length = len(monster_list)
  line_count = 0
  for line in monster_list:
    line_count += 1
    per = line_count / float(monster_list_length) * 100
    stdout.write('\r%sLoading Frostburn monster stats... %d%%%s' % (colorz.BLUE, per, colorz.ENDC))
    stdout.flush()
    import_frostfell_creature(db_cursor, line)
    db_conn.commit()

  print " COMPLETE!%s" % colorz.ENDC

  db_cursor.execute("SELECT id FROM creature")
  creature_id_list = db_cursor.fetchall()
  creature_id_list = [x[0] for x in creature_id_list]
  id_list_length = len(creature_id_list)
  line_count = 0
  for creature_id in creature_id_list:
    line_count += 1
    per = line_count / float(id_list_length) * 100
    #stdout.write('\r%sPopulating monster organizations... %d%%%s' % (colorz.BLUE, per, colorz.ENDC))
    #stdout.flush()
    db_cursor.execute("SELECT organization FROM creature_stat WHERE creature_id = ?",
      (creature_id,))
    organization = db_cursor.fetchone()
    if organization:
      populate_groups(db_cursor, creature_id, organization[0])
  print "%s Populating monster organizations... 100%% COMPLETE!%s" % (colorz.BLUE, colorz.ENDC)
  print " COMPLETE!%s" % colorz.ENDC

  standardize_list = sorted(standardize_list)
  for term in standardize_list:
    print term
  print ""

  return db_conn, db_cursor
