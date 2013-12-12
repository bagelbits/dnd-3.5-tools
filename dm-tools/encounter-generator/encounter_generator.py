#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    Hacked together random CR encounter generator.
    No GUI planned.

    By Chris Ward
"""

import argparse
import csv
from random import randint

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

  weird_same_cr = {
    1 : ['1/2', '1/3', '1/4', '1/6', '1/8', '1/8'],
    2 : [1, ['1/2', 1], '1/2', '1/3', '1/4', '1/8'],
    3 : [[1, 2], 1, ['1/2', 1], '1/2', '1/3', '1/4'],
    4 : [2, [1, 2], 1, ['1/2', 1], '1/2', '1/3'],
    5 : [3, 2, [1, 2], 1, '1/2', '1/2'],
    6 : [4, 3, 2, [1,2], 1, '1/2'],
  }
  # Need to have total creatures conform to list
  # Janky as fuck but it works

  creature_cr = weird_same_cr[set_cr][total_creatures]
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

#Yeah... this'll be way better with a db. Oh well. That's for v 1.1
def random_creature_by_cr(creature_cr, monsters, set_creature_type=''):
  creature_cr = str(creature_cr)
  proper_cr_monsters = []

  for monster_name in monsters:
    if monsters[monster_name]['cr'] == creature_cr:
      if set_creature_type in monsters[monster_name]['type']:
        proper_cr_monsters.append(monster_name)

  # Now momment of truth: Pick a random monster
  if proper_cr_monsters:
    return proper_cr_monsters[randint(0, len(proper_cr_monsters) - 1)]
  else:
    # Need to catch the recursion loop that can occur here
    if not set_creature_type:
      print "\nError: You have hit parameters that no monster can be generated for."
      print "Please double check your settings and try again."
      quit()
    else:
      return random_creature_by_cr(creature_cr, monsters)

def get_party_exp(party_levels, encounter_creatures, xp_table, monsters):
  party_size = len(party_levels)
  party_levels = list(set(party_levels))

  low_cr_found = False
  high_cr_found = False

  for character_level in party_levels:
    #Calculate xp and divide by number of party members
    character_xp = 0
    for creature in encounter_creatures:
      creature_cr = monsters[creature[0]]['cr']
      if '/' not in creature_cr:
        creature_xp = xp_table[character_level][int(creature_cr)]
        divisor = party_size
      else:
        creature_xp = xp_table[character_level][1]
        divisor = int(creature_cr.split('/')[1]) * party_size

      if creature_xp == '*':
        low_cr_found = True
        creature_xp = 0

      if creature_xp == '**':
        high_cr_found = True
        creature_xp

      character_xp += (creature_xp * creature[1]) / divisor

    print "Characters with level %s gain %sxp" % (character_level, character_xp)

  if low_cr_found:
    print "    Note: Some of these creature have a CR less than 8 the character's level"
    print "    and thus aren't awarded xp."

  if high_cr_found:
    print "    Note: some of these creatures have a CR greater than 8 the character's level"
    print "    and thus aren't awarded xp."

  print ""

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
parser.add_argument('-t', '--type-enforcement', action='store_true',
  default=False, dest='type_enforcement',
  help='Attempt to enforce same type for all monsters in encounter')
parser.add_argument('-p', '--party-level', nargs='*', dest='party_levels',
  help="Level of each party member")

# TODO: Option for no encounter varience

args=parser.parse_args()

set_cr = int(args.requested_cr)

set_cr = encounter_var(set_cr)
max_creatures = int(args.max_creatures)
type_enforcement = args.type_enforcement
party_levels = args.party_levels
number_of_creature_types = int(args.number_of_creature_types)

####################################################################################
#                                 CSV PROCESSING                                   #
####################################################################################

# TODO: Turn this into a sqlite db.

# Load book abbrev.
books = {}
book_list = csv.reader(open('assets/books.csv', 'rb'),
  delimiter=',', quotechar='"')
for line in book_list:
  books[line[0]] = line[1]

# Load monster list
monsters = {}
monster_list = csv.reader(open('assets/monsters_by_cr.csv', 'rb'),
  delimiter=',', quotechar='"')
for line in monster_list:
  monster_name = line[0]
  monsters[monster_name] = {}
  monsters[monster_name]['book'] = "%s, pg. %s" % (books[line[1]], line[2])
  monsters[monster_name]['type'] = line[3]
  monsters[monster_name]['cr'] = line[4]

# Load xp table
xp_table = {}
xp_list = csv.reader(open('assets/xp_table.csv', 'rb'),
  delimiter=',', quotechar='"')
xp_list.next()
for line in xp_list:
  line[0] = int(line[0])
  xp_table[line[0]] = {}
  xp_cr = 1
  for x in range(1, len(line)):
    if '*' not in line[x]:
      xp_table[line[0]][xp_cr] = int(line[x])
    else:
      xp_table[line[0]][xp_cr] = line[x]
    xp_cr += 1

#This is pulled out of DMG pg. 49
weird_mix_cr = {
  '1/6' : ['1/8', '1/8'],
  '1/4' : ['1/6', '1/8'],
  '1/3' : ['1/4', '1/6'],
  '1/2' : ['1/3', '1/4'],
  1 : ['1/3', '1/2'],
  2 : ['1/2', 1],
  3 : [1, 2],
}


number_of_creature_types = randint(1, number_of_creature_types)

if number_of_creature_types > max_creatures:
  number_of_creature_types = max_creatures

number_of_creature_types_left = number_of_creature_types
number_of_creatures = number_of_creature_types
creature_group_cr = []
# This should handle all 12 (I think it's 12, could be more) possible distribution cases for 
# 1 - 3 groups of subtypes. Technically should be able to do 1 - n
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
      if set_cr in weird_mix_cr:
        mixed_cr = weird_mix_cr[set_cr]
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

set_creature_type = ''
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

  creature_name = random_creature_by_cr(creature_cr, monsters, set_creature_type)
  if type_enforcement:
    set_creature_type = monsters[creature_name]['type']
  #Combine repeat creatures
  repeat_creature = False
  for x in range(0, len(encounter_creatures)):
    if creature_name == encounter_creatures[x][0]:
      encounter_creatures[x][1] += num_of_creature_in_group
      repeat_creature = True
  if not repeat_creature:
    encounter_creatures.append([creature_name, num_of_creature_in_group])

print "\nOh joy! Your players are fighting:"
for creature in encounter_creatures:
  if creature[1] == 1:
    print "%s; see %s CR: %s" % (creature[0],
      monsters[creature[0]]['book'], monsters[creature[0]]['cr'])
  else:
    print "%s %s; see %s CR: %s" % (creature[1],
      creature[0],
      monsters[creature[0]]['book'], monsters[creature[0]]['cr'])
print "May the dice be ever in your favor.\n"

if party_levels:
  print "And should they succeed:"
  party_levels = map(int, party_levels)
  get_party_exp(party_levels, encounter_creatures, xp_table, monsters)

