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

import argparse
from random import randint
from creature_db_setup import db_setup
import assets.dmg_tables as dmg_tables

def coin_flip():
  return randint(0, 1)

def encounter_var(set_cr):
  # Distribution pulled from DMG pg. 49
  d100_roll = randint(0, 99)

  #Each teir has distribution now so really hard and really easy are less likely
  if d100_roll < 10:
    # Easy
    d100_roll = randint(0, 99)
    if d100_roll < 52:
      set_cr -= 1
    elif d100_roll < 79:
      set_cr -= 2
    elif d100_roll < 93:
      set_cr -= 3
    elif d100_roll < 98:
      set_cr -= 4
    else:
      set_cr -= 5

  elif d100_roll < 30:
    print "\nNote to DM: This encounter is easy if done right!"
    print "Addendum: Don't forget to lower the rewarded XP!"
    set_cr += randint(0, 4)

  elif d100_roll < 80:
    # Challenging
    pass

  elif d100_roll < 95:
    # Very difficult
    d100_roll = randint(0, 99)
    if d100_roll < 52:
      set_cr += 1
    elif d100_roll < 79:
      set_cr += 2
    elif d100_roll < 93:
      set_cr += 3
    else:
      set_cr += 4

  else:
    # Overpowering
    d100_roll = randint(0, 99)
    if d100_roll < 55:
      set_cr += 5
    elif d100_roll < 84:
      set_cr += 6
    else:
      set_cr += 7

  if set_cr < 1:
    if set_cr == 0:
      set_cr = '1/2'
    elif set_cr == -1:
      set_cr = '1/3'
    elif set_cr == -2:
      set_cr = '1/4'
    elif set_cr == -3:
      set_cr = '1/6'
    else:
      set_cr = '1/8'

  print "\nThe CR for this encounter is %s" % set_cr
  return set_cr

def trans_to_weird_same_cr_table(total_creatures):
  if total_creatures < 5:
    return total_creatures - 2
  elif total_creatures < 7:
    return 3
  elif total_creatures < 10:
    return 4
  else:
    return 5

def get_weird_same_cr(set_cr, total_creatures):
  # Pulled out of DMG pg. 49
  total_creatures = trans_to_weird_same_cr_table(total_creatures)

  # Need to have total creatures conform to list
  # Janky as fuck but it works

  creature_cr = dmg_tables.weird_same_cr[set_cr][total_creatures]
  # For conistency's sake. The flip should set the other
  # result to the new cr
  if isinstance(creature_cr, list):
    flip_result = coin_flip()
    new_set_cr = creature_cr[flip_result]
    del creature_cr[flip_result]
    creature_cr = creature_cr[0]
  else:
    new_set_cr = creature_cr

  return creature_cr, new_set_cr

def get_creature_list(db_cursor, creature_cr, set_creature_type=''):
  proper_cr_monsters = []

  #Get type and subtype ids

  db_cursor.execute('SELECT id FROM creature WHERE cr = ?', (creature_cr,))
  
  for creature_id in [x[0] for x in db_cursor.fetchall()]:
    type_match = True
    if set_creature_type:
      # Weed out type mismatch
      if set_creature_type['type_id']:
        db_cursor.execute('SELECT creature_id FROM creature_type\
          WHERE creature_id = ? AND type_id = ? LIMIT 1',
          (creature_id, set_creature_type['type_id']))
        if not db_cursor.fetchone():
          type_match = False

      if set_creature_type['subtype_id']:
        for subtype_id in set_creature_type['subtype_id']:
          db_cursor.execute('SELECT creature_id FROM creature_subtype\
            WHERE creature_id = ? AND subtype_id = ? LIMIT 1', (creature_id, subtype_id))

          if not db_cursor.fetchone():
            type_match = False

    if type_match:
      proper_cr_monsters.append(creature_id)

  return proper_cr_monsters

def random_creature_by_cr(db_cursor, creature_cr, set_creature_type=''):
  
  """
  TODO: More concise type enforcing
  Try exact type
  Keep only element, alignment, type
  Drop type
  Drop alignment
  Try fucking anything (though try and keep in mind want alignment they usually are)
  """

  alignment = []

  # Type matching
  if set_creature_type:
    # Try exact type
    proper_cr_monsters = get_creature_list(db_cursor, creature_cr, set_creature_type)

    #Drop everying element, alignment, type
    if not proper_cr_monsters:
      new_subtype_list = []
      for subtype_id in set_creature_type['subtype_id']:
        db_cursor.execute('SELECT subtype_id FROM element WHERE subtype_id = ? LIMIT 1', 
          (subtype_id,))
        if db_cursor.fetchone():
          new_subtype_list.append(subtype_id)
          continue

        db_cursor.execute('SELECT subtype_id FROM alignment WHERE subtype_id = ? LIMIT 1', 
          (subtype_id,))
        if db_cursor.fetchone():
          new_subtype_list.append(subtype_id)
      
      set_creature_type['subtype_id'] = new_subtype_list
      proper_cr_monsters = get_creature_list(db_cursor, creature_cr, set_creature_type)

    # Drop type
    if not proper_cr_monsters:
      set_creature_type['type_id'] = 0
      proper_cr_monsters = get_creature_list(db_cursor, creature_cr, set_creature_type)

    # Drop alignment but store it for later
    if not proper_cr_monsters:
      new_subtype_list = []
      for subtype_id in set_creature_type['subtype_id']:
        db_cursor.execute('SELECT subtype_id FROM element WHERE subtype_id = ? LIMIT 1', 
          (subtype_id,))
        if db_cursor.fetchone():
          new_subtype_list.append(subtype_id)
        else:
          alignment.append(subtype_id)
      
      set_creature_type['subtype_id'] = new_subtype_list
      proper_cr_monsters = get_creature_list(db_cursor, creature_cr, set_creature_type)

    if not proper_cr_monsters:
      set_creature_type = ''

  # Try anything
  # TODO: Once we store alignment types, try and keep alignment the same
  if not set_creature_type:
    db_cursor.execute('SELECT id FROM creature WHERE cr = ?', (creature_cr,))
    proper_cr_monsters = [x[0] for x in db_cursor.fetchall()]



  # Now momment of truth: Pick a random monster
  if proper_cr_monsters:
    return proper_cr_monsters[randint(0, len(proper_cr_monsters) - 1)]
  else:
    print "\nError: You have hit parameters that no monster can be generated for."
    print "Please double check your settings and try again."
    quit()

def get_creature_data(db_cursor, creature_id):
  # Let's pull all of the storecd data for that creature
  creature_data = {'id': creature_id}
  
  db_cursor.execute('SELECT name, cr FROM creature WHERE id = ? LIMIT 1', (creature_id,))
  creature_data['name'], creature_data['cr'] = db_cursor.fetchone()

  db_cursor.execute('SELECT book_id, page FROM creature_book WHERE creature_id = ? LIMIT 1',
    (creature_id,))
  book_id, page_num = db_cursor.fetchone()

  db_cursor.execute('SELECT name FROM book WHERE id = ? LIMIT 1', (book_id,))
  creature_data['book'] = [db_cursor.fetchone()[0], page_num]

  creature_data['type'] = {
    'type_id' : 0,
    'subtype_id' : [],
  }
  db_cursor.execute('SELECT type_id FROM creature_type WHERE creature_id = ? LIMIT 1',
    (creature_id,))
  creature_data['type']['type_id']= db_cursor.fetchone()[0]

  db_cursor.execute('SELECT subtype_id FROM creature_subtype WHERE creature_id = ?',
    (creature_id,))
  creature_data['type']['subtype_id'] = [x[0] for x in db_cursor.fetchall()]

  return creature_data

def get_type_ids(db_cursor, creature_type):
  type_ids = {
    'type_id' : 0,
    'subtype_id' : [],
  }

  for type_name in creature_type:
    db_cursor.execute('SELECT id FROM type WHERE name = ? LIMIT 1', (type_name,))
    type_id = db_cursor.fetchone()
    if type_id:
      type_ids['type_id'] = type_id[0]
      continue
    else:
      db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (type_name,))
      subtype_id = db_cursor.fetchone()
      if subtype_id:
        type_ids['subtype_id'].append(subtype_id[0])
      else:
        print "Type not found: %s" % type_name

  return type_ids

def get_party_exp(db_cursor, party_levels, encounter_creatures):
  party_size = len(party_levels)
  party_levels = list(set(party_levels))

  low_cr_found = False
  high_cr_found = False

  for character_level in party_levels:
    #Calculate xp and divide by number of party members
    character_xp = 0
    for creature in encounter_creatures:
      creature_data = creature[0]
      creature_cr = creature_data['cr']
      if '/' not in creature_cr:
        creature_cr = int(creature_cr)
      divisor = party_size
      # Need to catch CRs less than 1
      if isinstance(creature_cr, str):
        cr_ecl_diff = 1 - character_level
      else:
        cr_ecl_diff = creature_cr - character_level

      # Check if CR is too high or too low
      if cr_ecl_diff < -7:
        low_cr_found = True
        creature_xp = 0
      elif cr_ecl_diff > 7:
        high_cr_found = True
        creature_xp = 0
      else:
        if not isinstance(creature_cr, str):
          creature_xp = dmg_tables.xp_table[character_level][int(creature_cr)]
        else:
          creature_xp = dmg_tables.xp_table[character_level][1]
          divisor *= int(creature_cr.split('/')[1])

      character_xp += (creature_xp * creature[1]) / divisor

    print "Characters with level %s gain %sxp" % (character_level, character_xp)

  if low_cr_found:
    print "\n    Note: Some of these creature have a CR less than 8 the character's level"
    print "    and thus aren't awarded xp."

  if high_cr_found:
    print "\n    Note: some of these creatures have a CR greater than 8 the character's level"
    print "    and thus aren't awarded xp."

  print ""

def break_up_encounter_cr(set_cr, number_of_creature_types):
  number_of_creature_types_left = number_of_creature_types
  creature_group_cr = []
  for x in range(0, number_of_creature_types):
    # We can't break anything into smaller that CR 1/8
    if set_cr == '1/8':
      creature_group_cr.append(set_cr)
      continue

    if x !=  number_of_creature_types - 1:
      # Mixed level type
        # Mixed type and same type are the exact same operation for when you have more
        # than 2 creatures
        # DMG doesn't say how to split apart anything less than CR 1 when it's the same.
      if coin_flip() or isinstance(set_cr, str) or number_of_creature_types - x != 2:
        if set_cr in dmg_tables.weird_mix_cr:
          mixed_cr = dmg_tables.weird_mix_cr[set_cr]
        else:
          mixed_cr = [set_cr - 1, set_cr - 3]
        # We flip again because it can go either way
        # This also handles mix/same for anything with more than 2 creatures
        flip_result = coin_flip()
        creature_cr = mixed_cr[flip_result]
        del mixed_cr[flip_result]
        set_cr = mixed_cr[0]

      # Same level type
        # This should really only be reached with 2 creatuers left.
      else:
        if set_cr < 7:
          creature_cr, set_cr = get_weird_same_cr(set_cr, number_of_creature_types_left)
        else:
          creature_cr = set_cr - number_of_creature_types_left
          set_cr += number_of_creature_types_left - 4

      number_of_creature_types_left -= 1
      creature_group_cr.append(creature_cr)
    else:
      creature_group_cr.append(set_cr)

  return creature_group_cr

def get_encouter_creatures(creature_group_cr, number_of_creatures, set_creature_type, type_enforcement):
  encounter_creatures = []
  # Randomly select number of creatures, try and conform to type
  for creature_cr in creature_group_cr:
    #Select number of creatures:
    num_of_creature_in_group = 1
    if number_of_creatures < max_creatures and isinstance(creature_cr, int):
      if coin_flip():
        # Lower bound is 0 because it shouldn't count itself.
        #num_of_creature_in_group += randint(0, max_creatures - number_of_creatures)
        num_of_creature_in_group += randint(1, max_creatures - number_of_creatures)

        #There isn't really a way to split this into a smaller encounter.
        # Also, this should never be triggered.
        if num_of_creature_in_group > 12:
          print "You shouldn't have more than 12 creatures in an encounter. Setting to 12...."
          num_of_creature_in_group = 12
        # Need to update number of creatures otherwise you don't cap at 5
        number_of_creatures += num_of_creature_in_group - 1

        if num_of_creature_in_group > 1:
          # Have to handle those weird cases where it can be two cr
          if creature_cr < 7:
            new_cr = get_weird_same_cr(creature_cr, num_of_creature_in_group)[0]
          else:
            #Have to call the method anyways since large groups can group the cr together
            new_cr = creature_cr - trans_to_weird_same_cr_table(num_of_creature_in_group) - 2
          creature_cr = new_cr

    creature_id = random_creature_by_cr(db_cursor, creature_cr, set_creature_type)
    creature_data = get_creature_data(db_cursor, creature_id)
    if type_enforcement and not set_types:
      set_creature_type = creature_data['type']
    
    #Combine repeat creatures
    repeat_creature = False
    for x in range(0, len(encounter_creatures)):
      if creature_data['name'] == encounter_creatures[x][0]['name']:
        encounter_creatures[x][1] += num_of_creature_in_group
        repeat_creature = True
    if not repeat_creature:
      encounter_creatures.append([creature_data, num_of_creature_in_group])

  return encounter_creatures

####################################################################################
#                                  DATBASE SETUP                                   #
####################################################################################
db_conn, db_cursor = db_setup()

####################################################################################
#                                 ARGUMENT PARSING                                 #
####################################################################################
parser = argparse.ArgumentParser()

parser.add_argument('-c', '--cr', default='1', dest='requested_cr',
  help="Set random encounter CR")
parser.add_argument('-m', '--max-creatures', default='5',
  dest='max_creatures', help="Set max number of creatures in an encounter")
parser.add_argument('-k', '--max-creature-kinds', default='3',
  dest='number_of_creature_types', help="Set max number of creature kinds in an encounter")
parser.add_argument('-e', '--type-enforcement', action='store_true',
  default=False, dest='type_enforcement',
  help='Attempt to enforce same type for all monsters in encounter')
parser.add_argument('-p', '--party-level', nargs='*', dest='party_levels',
  help="Level of each party member")
parser.add_argument('-V', '--no-varience', action='store_true',
  default=False, dest='no_varience',
  help="Hard set CR, do not vary based off varience tables")
parser.add_argument('-t', '--set-types', nargs='*', dest='set_types',
  help="Set types that you want. Please comment separate these.")
parser.add_argument('-n', '---encounters', default='1',
  dest='max_encounters', help="Set max number of encounters to generate")
parser.add_argument('--pokemon-mode', default=False, dest='pokemon_mode',
  help='Set pokemon style vs. mode with CR')

# TODO: Option for setting types you want

args=parser.parse_args()

#Support pokemon mode
if args.pokemon_mode:
  set_cr = int(args.pokemon_mode)
  max_encounters = 2
  max_creatures = 1
  number_of_creature_types = 1
  set_types = ''
  type_enforcement = False
  party_levels = []

else:
  set_cr = int(args.requested_cr)

  

  if args.set_types:
    set_types = " ".join(args.set_types).split(", ")
  else:
    set_types = ''

  max_creatures = int(args.max_creatures)
  type_enforcement = args.type_enforcement
  party_levels = args.party_levels
  number_of_creature_types = int(args.number_of_creature_types)
  max_encounters = int(args.max_encounters)

####################################################################################
#                                 CSV PROCESSING                                   #
####################################################################################

# TODO: Turn this into a sqlite db.

number_of_creature_types = randint(1, number_of_creature_types)

if number_of_creature_types > max_creatures:
  number_of_creature_types = max_creatures

for encounter in range(0, max_encounters):

  if not args.pokemon_mode:
    print "Encounter #%s" % (encounter + 1)
    if args.no_varience:
      print "The CR for this encounter is %s" % set_cr
    else:
      set_cr = encounter_var(set_cr)

  creature_group_cr = break_up_encounter_cr(set_cr, number_of_creature_types)
  # This should handle all 12 (I think it's 12, could be more) possible distribution cases for 
  # 1 - 3 groups of subtypes. Technically should be able to do 1 - n

  set_creature_type = ''
  if set_types:
    set_creature_type = get_type_ids(db_cursor, set_types)
    type_enforcement = True
  encounter_creatures = get_encouter_creatures(creature_group_cr, number_of_creature_types,
    set_creature_type, type_enforcement)

  if args.pokemon_mode:
    creature_data = encounter_creatures[0][0]
    if not encounter:
      print "\nFight set!\n"
    print "%s; see %s, pg. %s CR: %s\n" % (creature_data['name'],
        creature_data['book'][0], creature_data['book'][1],
        creature_data['cr'])
    if not encounter:
      print "VS.\n"
    continue

  print "\nOh joy! Your players are fighting:"
  for creature in encounter_creatures:
    creature_data = creature[0]
    number_of_creatures = creature[1]
    if number_of_creatures == 1:
      print "%s; see %s, pg. %s CR: %s" % (creature_data['name'],
        creature_data['book'][0], creature_data['book'][1],
        creature_data['cr'])
    else:
      print "%s %s; see %s, pg. %s CR: %s" % (number_of_creatures,
        creature_data['name'], creature_data['book'][0],
        creature_data['book'][1], creature_data['cr'])
  print "May the dice be ever in your favor.\n"

  if party_levels:
    print "And should they succeed:"
    party_levels = map(int, party_levels)
    get_party_exp(db_cursor, party_levels, encounter_creatures)

db_conn.commit()
db_conn.close()