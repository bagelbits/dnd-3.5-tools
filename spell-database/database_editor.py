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
import argparse
import os
from sys import exit, stdout
from spell_db_populater import parse_spell, get_class_info, get_book_info
from spell_db_controller import insert_spell_into_db, insert_alt_spell_into_db
from spell_db_controller import insert_spell_class, full_spell_description, insert_spell_book
from spell_db_controller import insert_spell_component, insert_spell_school, insert_spell_subschool
from spell_db_controller import insert_spell_descriptor


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


##
# Parses spell into useful info and 
##

def add_spell_to_db(db_cursor, spell):
  existing_spell_flag = False

  parsed_spell = parse_spell(spell)

  # First, test if spell already exists.
  # Spit out error and exit if it does.
  # This may be subject to change for now
  db_cursor.execute("SELECT id FROM spell WHERE name = ?", (spell['Name'], ))
  matched_id = db_cursor.fetchone()
  if matched_id:
    existing_spell_flag = True
    print "%sError: Spell already exists: Spell with matching name found. Please resolve in import file." \
      % (colorz.RED, )
    print "Found spell:"
    full_spell_description(db_cursor, matched_id[0])

  # If spell doesn't exist, let's put it in.
  db_cursor.execute("SELECT spell_id FROM alt_spell WHERE name = ?", (spell['Name'],))
  matched_id = db_cursor.fetchone()
  if matched_id:
    existing_spell_flag = True
    print "%sError: Spell already exists: Spell with matching name found. Please resolve in import file." \
      % (colorz.RED, )
    print "Found spell:%s" % colorz.GREY
    print "    %s" % spell['Name']
    db_cursor.execute("SELECT name FROM spell WHERE id = ?", (matched_id[0]))
    alt_spell_name =  db_cursor.fetchone()[0]
    print "See \"%s\"" % alt_spell_name

  if existing_spell_flag:
    print "%sSpell to be imported:%s" % (colorz.RED, colorz.GREY)
    print "\n".join(spell)
    return

  if "alt_spell_name" in parsed_spell:
    insert_alt_spell_into_db(db_cursor, parsed_spell)
  else:
    insert_spell_into_db(db_cursor, parsed_spell)

#Overwrites. Does not append. May want to do a separate function for appending.
def update_spell_in_db(db_cursor, spell,  crud_type):
  spell_name = spell.popleft()
  db_cursor.execute("SELECT id FROM spell WHERE name = ?", (spell_name, ))
  matched_id = db_cursor.fetchone()
  if not matched_id:
    print "%sError: Spell name does not exist: %s%s" % (colorz.RED, spell_name, colorz.ENDC)
    return

  if crud_type == "Update:Append":
    while spell:
      if spell[0].startswith("Class:"):
        spell[0] = re.sub('Class: ', '', spell[0], count=1)
        class_info = get_class_info(spell[0])
        insert_spell_class(db_cursor, class_info, spell_name, matched_id)

      if spell[0].startswith("Book:"):
        spell[0] = re.sub('Book: ', '', spell[0], count=1)
        book_info = get_book_info(spell[0])
        insert_spell_book(db_cursor, book_info, matched_id)

      if spell[0].startswith("School:"):
        spell[0] = re.sub('School: ', '', spell[0], count=1).split("/")
        insert_spell_school(db_cursor, spell[0], spell_name, matched_id)
      
      if spell[0].startswith("Subschool"):
        spell[0] = re.sub('Subschool: ', '', spell[0], count=1).split(", ")
        insert_spell_subschool(db_cursor, spell[0], spell_name, matched_id)

      if spell[0].startswith("Descriptor"):
        spell[0] = re.sub('Descriptor: ', '', spell[0], count=1).split(", ")
        insert_spell_descriptor(db_cursor, spell[0], spell_name, matched_id)

      if spell[0].startswith("Components:"):
        spell[0] = re.sub('Components: ', '', spell[0], count=1).split(", ")
        insert_spell_component(db_cursor, spell[0], spell_name, matched_id)

      spell.pop()

  if crud_type == "Update:Overwrite":
    while spell:
      if spell[0].startswith("Class:"):
        db_cursor.execute("DELETE FROM spell_class WHERE spell_id = ?", (matched_id,))
        spell[0] = re.sub('Class: ', '', spell[0], count=1)
        class_info = get_class_info(spell[0])
        insert_spell_class(db_cursor, class_info, spell_name, matched_id)

      if spell[0].startswith("Book:"):
        db_cursor.execute("DELETE FROM spell_book WHERE spell_id = ?", (matched_id[0],))
        spell[0] = re.sub('Book: ', '', spell[0], count=1)
        book_info = get_book_info(spell[0])
        insert_spell_book(db_cursor, book_info, matched_id)

      if spell[0].startswith("School:"):
        db_cursor.execute("DELETE FROM spell_school WHERE spell_id = ?", (matched_id[0],))
        spell[0] = re.sub('School: ', '', spell[0], count=1).split("/")
        insert_spell_school(db_cursor, spell[0], spell_name, matched_id)
      
      if spell[0].startswith("Subschool"):
        db_cursor.execute("DELETE FROM spell_subschool WHERE spell_id = ?", (matched_id[0],))
        spell[0] = re.sub('Subschool: ', '', spell[0], count=1).split(", ")
        insert_spell_subschool(db_cursor, spell[0], spell_name, matched_id)

      if spell[0].startswith("Descriptor"):
        db_cursor.execute("DELETE FROM spell_descriptor WHERE spell_id = ?", (matched_id[0],))
        spell[0] = re.sub('Descriptor: ', '', spell[0], count=1).split(", ")
        insert_spell_descriptor(db_cursor, spell[0], spell_name, matched_id)

      if spell[0].startswith("Components:"):
        db_cursor.execute("DELETE FROM spell_component WHERE spell_id = ?", (matched_id[0],))
        spell[0] = re.sub('Components: ', '', spell[0], count=1).split(", ")
        insert_spell_component(db_cursor, spell[0], spell_name, matched_id)

      if spell[0].startswith("Casting Time:"):
        spell[0] = re.sub('Casting Time: ', '', spell[0], count=1)
        db_cursor.execute("UPDATE spell SET cast_time = ? WHERE id = ?", (spell[0], matched_id))

      if spell[0].startswith("Range:"):
        spell[0] = re.sub('Range: ', '', spell[0], count=1)
        db_cursor.execute("UPDATE spell SET range = ? WHERE id = ?", (spell[0], matched_id))

      if spell[0].startswith("Target:"):
        spell[0] = re.sub('Target: ', '', spell[0], count=1)
        db_cursor.execute("UPDATE spell SET target = ? WHERE id = ?", (spell[0], matched_id))

      if spell[0].startswith("Effect:"):
        spell[0] = re.sub('Effect: ', '', spell[0], count=1)
        db_cursor.execute("UPDATE spell SET effect = ? WHERE id = ?", (spell[0], matched_id))

      if spell[0].startswith("Area:"):
        spell[0] = re.sub('Area: ', '', spell[0], count=1)
        db_cursor.execute("UPDATE spell SET area = ? WHERE id = ?", (spell[0], matched_id))

      if spell[0].startswith("Duration:"):
        spell[0] = re.sub('Duration: ', '', spell[0], count=1)
        db_cursor.execute("UPDATE spell SET duration = ? WHERE id = ?", (spell[0], matched_id))

      if spell[0].startswith("Saving Throw:"):
        spell[0] = re.sub('Saving Throw: ', '', spell[0], count=1)
        db_cursor.execute("UPDATE spell SET saving_throw = ? WHERE id = ?", (spell[0], matched_id))

      if spell[0].startswith("Spell Resistance:"):
        spell[0] = re.sub('Spell Resistance: ', '', spell[0], count=1)
        db_cursor.execute("UPDATE spell SET spell_resist = ? WHERE id = ?", (spell[0], matched_id))

      if spell[0].startswith("Description:"):
        spell[0] = re.sub('Description: ', '', spell[0], count=1)
        description = []
        while not re.match("\w+(\s\w+)*:", spell[0]):
          description.append(spell.pop())
        db_cursor.execute("UPDATE spell SET description = ? WHERE id = ?",
          ("\n".join(description), matched_id))
        #Just so we don't accidently pop off additional lines.
        spell.insert(0, '')

      spell.pop()


  # TODO: Change spell from alt to normal and visa versa

def delete_spell_from_db(db_cursor, spell):
  # Delete spell commands should only have one line, i.e., a spell name
  # This may match up with a spell or an alt spell
  db_cursor.execute("SELECT id FROM spell WHERE name = ?", (spell[0], ))
  matched_id = db_cursor.fetchone()
  if matched_id:
    # TODO: Make this a method in the CRUD class
    db_cursor.execute("DELETE FROM spell WHERE id = ?", (matched_id[0],))
    db_cursor.execute("DELETE FROM spell_class WHERE spell_id = ?", (matched_id[0],))
    db_cursor.execute("DELETE FROM spell_domain_feat WHERE spell_id = ?", (matched_id[0],))
    db_cursor.execute("DELETE FROM spell_book WHERE spell_id = ?", (matched_id[0],))
    db_cursor.execute("DELETE FROM spell_school WHERE spell_id = ?", (matched_id[0],))
    db_cursor.execute("DELETE FROM spell_subschool WHERE spell_id = ?", (matched_id[0],))
    db_cursor.execute("DELETE FROM spell_descriptor WHERE spell_id = ?", (matched_id[0],))
    db_cursor.execute("DELETE FROM spell_component WHERE spell_id = ?", (matched_id[0],))
    return

  db_cursor.execute("SELECT id FROM alt_spell WHERE name = ?", (spell[0],))
  matched_id = db_cursor.fetchone()
  if matched_id:
    db_cursor.execute("DELETE FROM alt_spell WHERE id = ?", (matched_id[0],))
    return

  print "%sError! Spell name does not exist: %s%s" % (colorz.RED, spell[0], colorz.ENDC)
  return


def determine_crud_type(db_cursor, spell, verbose_flag):
  crud_type = spell.popleft().strip()
  
  if crud_type == "Add":
    add_spell_to_db(db_cursor, spell)
  elif crud_type.startswith("Update"):
    update_spell_in_db(db_cursor, spell, crud_type)
  elif crud_type == "Delete":
    delete_spell_from_db(db_cursor, spell)
  else:
    print "%s'%s' is not a valid CRUD type. Spell dump:\n%s%s" \
      % (colorz.RED, crud_type, "".join(spell), colorz.ENDC)
    return

#####################
# Arguement parsing #
#####################

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true', default=False,
                    dest='verbose', help='verbose output')
parser.add_argument('-f', '--file', nargs=1, dest='import_file',
                    help='Import file name')

args = parser.parse_args()

if args.verbose:
  verbose_flag = args.verbose

###################
# Set import file #
###################

import_file_name = ""
if args.import_file:
  if not os.path.exists(args.import_file):
    print "%s%s does not exist!%s" % (colorz.RED, args.import_file, colorz.ENDC)
  import_file_name = args.import_file[0]
else:
  print "%sNo import file set%s" % (colorz.RED, colorz.ENDC)
  exit()
db_conn = sqlite3.connect('spells.db')
db_conn.text_factory = str
db_cursor = db_conn.cursor()


####################
# Load import file #
####################


if verbose_flag:
  print "Loading from import file: %s" % import_file_name

import_file = open(import_file_name, 'r')
spell = []

import_file = list(import_file)
line_count = 0
for line in import_file:
  line_count += 1
  per = line_count / float(len(import_file)) * 100
  stdout.write("%s\rImporting: %d%%%s") % (colorz.YELLOW, per, colorz.ENDC)
  stdout.flush()

  line = re.sub(" +$", "", line)

  if not line.strip():
    determine_crud_type(db_cursor, spell, verbose_flag)
    del spell[:]
    continue

  spell.append(line)


print "%s COMPLETE!%s" % (colorz.YELLOW, colorz.ENDC)
