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
  d100_roll = randint(0, 99)
  # Distribution pulled from DMG pg. 49

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
    print "You may want to reroll this.... also bug Chris"

  print "\nThe CR for this encounter is %s" % set_cr
  return set_cr

def get_weird_same_cr(set_cr, total_creatures):
  # Pulled out of DMG pg. 49
  # Only goes up to 5 creatures because I'm not dealing with any more yet.
  weird_same_cr = {
    1 : ['1/2', '1/3', '1/4', '1/6'],
    2 : [1, ['1/2', 1], '1/2', '1/3'],
    3 : [[1, 2], 1, ['1/2', 1], '1/2'],
    4 : [2, [1, 2], 1, ['1/2', 1]],
    5 : [3, 2, [1, 2], 1],
    6 : [4, 3, 2, [1,2]],
  }
  # Need to have total creatures conform to list
  # Janky as fuck but it works

  total_creatures -= 2

  creature_cr = weird_same_cr[set_cr][total_creatures]
  if isinstance(creature_cr, list):
    creature_cr = creature_cr[coin_flip()]

  new_set_cr = creature_cr
  if total_creatures:
    for el in weird_same_cr:
      comparable_cr = weird_same_cr[el][total_creatures - 1]
      if isinstance(comparable_cr, list):
        comparable_cr = comparable_cr[coin_flip()]
      if comparable_cr == creature_cr:
        new_set_cr = comparable_cr

  return creature_cr, new_set_cr

#Yeah... this'll be way better with a db. Oh well. That's for v 1.1
def random_creature_by_cr(creature_cr, monsters, set_creature_type=''):
  creature_cr = str(creature_cr)
  proper_cr_monsters = []

  for monster_name in monsters:
    if monsters[monster_name]['cr'] == creature_cr:
      if set_creature_type in monsters[monster_name]['type']:
        proper_cr_monsters.append(monster_name)

  #Now momment of truth: Pick a random monster
  if proper_cr_monsters:
    return proper_cr_monsters[randint(0, len(proper_cr_monsters) - 1)]
  else:
    return random_creature_by_cr(creature_cr, monsters)

def get_party_exp(party_levels, encounter_creatures, xp_table, monsters):
  party_size = len(party_levels)
  party_levels = list(set(party_levels))

  for character_level in party_levels:
    #Calculate xp and divide by number of party members
    low_cr_found = False
    character_xp = 0
    for creature in encounter_creatures:
      creature_cr = monsters[creature[0]]['cr']
      if '/' not in creature_cr:
        creature_xp = xp_table[character_level][int(creature_cr)]
        divisor = party_size
      else:
        creature_xp = xp_table[character_level][1]
        divisor = int(creature_cr.split('/')[1]) * party_size

      if creature_xp == 0:
        low_cr_found = True

      character_xp += (creature_xp * creature[1]) / divisor

    print "Characters with level %s gain %sxp" % (character_level, character_xp)

    if low_cr_found:
      print "Note: Some of these creature have a CR less than 8 the character's level"
      print "and thus aren't awarded xp."

####################################################################################
#                                 ARGUMENT PARSING                                 #
####################################################################################
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--random', nargs=2, dest='random_cr_range',
  help="Range for random CR")
parser.add_argument('-c', '--cr', default='1', dest='requested_cr',
  help="Set random encounter CR")
parser.add_argument('-m', '--max-creatures', default='5',
  dest='max_creatures', help="Set max number of creatures in an encounter")
parser.add_argument('-t', '--type-enforcement', action='store_true',
  default=False, dest='type_enforcement',
  help='Attempt to enforce same type for all monsters in encounter')
parser.add_argument('-p', '--party-level', nargs='*', dest='party_levels',
  help="Level of each party member")

# TODO: I know there is a lower limit for the encounter level. Won't find
# until after testing.

args=parser.parse_args()
set_cr = 1
if args.random_cr_range:
  cr_range = map(int, args.random_cr_range)
  set_cr = randint(cr_range[0], cr_range[1])
else:
  set_cr = int(args.requested_cr)

set_cr = encounter_var(set_cr)
max_creatures = int(args.max_creatures)
type_enforcement = args.type_enforcement
party_levels = args.party_levels

####################################################################################
#                                 CSV PROCESSING                                   #
####################################################################################

# TODO: Turn this into a sqlite db.
books = {}
book_list = csv.reader(open('assets/books.csv', 'rb'),
  delimiter=',', quotechar='"')
for line in book_list:
  books[line[0]] = line[1]

monsters = {}
monster_list = csv.reader(open('assets/monsters_by_cr.csv', 'rb'),
  delimiter=',', quotechar='"')
for line in monster_list:
  monster_name = line[0]
  monsters[monster_name] = {}
  monsters[monster_name]['book'] = "%s, pg. %s" % (books[line[1]], line[2])
  monsters[monster_name]['type'] = line[3]
  monsters[monster_name]['cr'] = line[4]



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
    if line[x] == '*':
      xp_table[line[0]][xp_cr] = 0
    xp_cr += 1

#This is pulled out of DMG pg. 49
weird_mix_cr = {
  1 : ['1/3', '1/2'],
  2 : ['1/2', 1],
  3 : [1, 2],
}


number_of_creature_types = randint(1, 3)
number_of_creature_types_left = number_of_creature_types
number_of_creatures = number_of_creature_types
creature_group_cr = []
# This should handle all 12 (I think it's 12, could be more) possible distribution cases for 
# 1 - 3 groups of subtypes. Technically should be able to do 1 - n
for x in range(0, number_of_creature_types):
  # Because fuck you I'm not dealing with CR's smaller than 1
  # You'll get an encounter slightly easier. So what.
  if isinstance(set_cr, str):
    creature_group_cr.append(set_cr)
    continue

  if x != number_of_creature_types - 1:
    if coin_flip():
      # Mixed level type
      # We flip again because it can go either way
      if set_cr in weird_mix_cr:
        mixed_cr = weird_mix_cr[set_cr]
      else:
        mixed_cr = [set_cr - 1, set_cr - 3]
      flip_result = coin_flip()
      creature_cr = mixed_cr[flip_result]
      del mixed_cr[flip_result]
      set_cr = mixed_cr[0]
      creature_group_cr.append(creature_cr)
      number_of_creature_types_left -= 1
      test_bool = False
    else:
      # Same level type
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
# TODO: Breaking up might not work
for creature_cr in creature_group_cr:
  #Select number of creatures:
  num_of_creature_in_group = 1
  if number_of_creatures < max_creatures and isinstance(creature_cr, int):
    if coin_flip():
      # Lower bound is 0 because it shouldn't count itself.
      num_of_creature_in_group += randint(0, max_creatures - number_of_creatures)
      if num_of_creature_in_group > 1:
        # Have to handle those weird cases where it can be two cr
        if creature_cr < 7:
          new_cr = get_weird_same_cr(creature_cr, num_of_creature_in_group)[0]
        else:
          new_cr = creature_cr - num_of_creature_in_group
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
    print "%s; see %s" % (creature[0],
      monsters[creature[0]]['book'])
  else:
    print "%s %s; see %s" % (creature[1],
      creature[0],
      monsters[creature[0]]['book'])
print "May the dice be ever in your favor.\n"

if party_levels:
  print "And should they succeed:"
  party_levels = map(int, party_levels)
  get_party_exp(party_levels, encounter_creatures, xp_table, monsters)

