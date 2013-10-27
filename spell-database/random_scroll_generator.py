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
import random
import argparse
from sys import stdout, exit
from spell_db_controller import full_spell_description


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


##############################################################
#                WEIGHTED CHOICE ALGORITHM                   #
# Neat little algorithm that takes a dict of weighted keys.  #
# Values are the weight. Then adds them up a picks at random #
# Then figures out the corresponding key.                    #
##############################################################

def weighted_choice(freq_weights):
    total = sum(freq_weights[freq] for freq in freq_weights)
    rand_choice = random.uniform(0, total)
    upto = 0
    for freq in freq_weights:
        upto += freq_weights[freq]
        if upto > rand_choice:
            return freq
    assert False, "Shouldn't get here"


################################################################
#                      RANDOM SPELL PICKER                     #
# Picks a random spell based on choice weights and spell level #
################################################################

def random_spell(db_cursor, choice_weights, spell_level, spell_type):
    frequency_weights = choice_weights['frequency_weights']
    general_class_weights = choice_weights['general_class_weights']
    domain_class_weights = choice_weights['domain_class_weights']
    domain_feat_weights = choice_weights['domain_feat_weights']

    print "%sPicking random spell....%s" % (colorz.PURPLE, colorz.ENDC)

    #################################################
    # First select either Common, Uncommon, or Rare #
    #################################################

    select_freq = weighted_choice(frequency_weights)

    #################################################
    # Next, select class in that frequency category #
    # base on whether arcane or divine.             #
    #################################################

    if spell_type == 'arcane':
        db_cursor.execute("SELECT id, more_common FROM class \
                           WHERE frequency = ? AND arcane = 1", (select_freq, ))
    else:
        db_cursor.execute("SELECT id, more_common FROM class \
                           WHERE frequency = ? AND divine = 1", (select_freq, ))
    class_weights = {}
    for returned_class in db_cursor.fetchall():
        if returned_class[1] == 0:
            class_weights[returned_class[0]] = general_class_weights['regular']
        else:
            class_weights[returned_class[0]] = general_class_weights['more_common']
    select_class = weighted_choice(class_weights)
    db_cursor.execute("SELECT name FROM class WHERE id = ?", (select_class, ))
    class_name = db_cursor.fetchone()[0]
    print "%s%s Spell (%s)%s" % (colorz.YELLOW, class_name, spell_type, colorz.ENDC)

    #################################################
    # Then, select if normal spells or domain/feats #
    #################################################

    select_class_domain = weighted_choice(domain_class_weights)

    ###################################################
    # Finally, select the spell. Depending on whether #
    # it's a class spell or domain/feat spell         #
    ###################################################

    if select_class_domain == 'class':
        db_cursor.execute("SELECT spell_id FROM spell_class\
                           WHERE class_id = ? AND level = ?", (select_class, spell_level))
        class_spells = db_cursor.fetchall()
        select_spell = random.choice(class_spells)[0]
    else:
        ######################################################
        # Class specific domains/feats should be more likely #
        # to show than general class domain/feats.           #
        ######################################################

        db_cursor.execute("SELECT domain_feat_id FROM class_domain_feat\
                           WHERE class_id = ?", (select_class, ))
        any_domain_feat = db_cursor.fetchall()
        db_cursor.execute("SELECT domain_feat_id FROM class_domain_feat\
                           WHERE class_id = 0")
        class_domain_feat = db_cursor.fetchall()

        if weighted_choice(domain_feat_weights) == 'class' and class_domain_feat:
            select_domain_feat = random.choice(class_domain_feat)[0]
        else:
            select_domain_feat = random.choice(any_domain_feat)[0]

        ############################################
        # Now pick the domain/feat spell at random #
        ############################################

        db_cursor.execute("SELECT spell_id FROM spell_domain_feat\
                           WHERE domain_feat_id = ? AND level = ?",
                          (select_domain_feat, spell_level))
        domain_feat_spells = db_cursor.fetchall()
        select_spell = random.choice(domain_feat_spells)[0]

    ####################################
    # Print out full spell description #
    ####################################

    full_spell_description(db_cursor, select_spell)


##########################################################
# At some point these should be easily alterable and not #
# hardcoded                                              #
##########################################################

choice_weights = {
    'frequency_weights': {
        'Common': 89,
        'Uncommon': 20,
        'Rare': 1,
        'None': 0
    },
    'general_class_weights': {
        'more_common': 10,
        'regular': 1
    },
    'domain_class_weights': {
        'domain': 1,
        'class': 20
    },
    'domain_feat_weights': {
        'class': 3,
        'any': 1
    }
}

#######################
# ARGUMENT PROCESSING #
#######################

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--spell_level', nargs=1, dest='spell_level',
                    help='Set spell level')
parser.add_argument('-a', '--arcane', action='store_true', default=False,
                    dest='arcane', help='Set spell type to arcane')
parser.add_argument('-d', '--divine', action='store_true', default=False,
                    dest='divine', help='Set spell type to divine')

args = parser.parse_args()

###############
# Spell level #
###############

if args.spell_level:
    spell_level = int(args.spell_level[0])
else:
    spell_level = int(raw_input("%sSpell level for scroll? %s" % (colorz.CYAN, colorz.ENDC)))

if spell_level < 0 or spell_level > 9:
    print "%sSpell level is not between 0 or 9. Please retry!%s" % (colorz.RED, colorz.ENDC)
    exit()

##############
# Spell type #
##############

if args.arcane and args.divine:
    print "Please choose only arcane or divine, not both."

if args.arcane:
    spell_type = 'arcane'
if args.divine:
    spell_type = 'divine'

# TODO: This should randomly pick one instead
if not args.arcane and not args.divine:
    spell_type = raw_input("%sArcane or Divine? %s" % (colorz.CYAN, colorz.ENDC))
    if spell_type.lower().startswith('a'):
        spell_type = 'arcane'
    elif spell_type.lower().startswith('d'):
        spell_type = 'divine'
    else:
        print "%sThat's not a valid type.%s" % (colorz.RED, colorz.ENDC)
        exit()

####################################################
# Open your db connections and pick a random spell #
####################################################

db_conn = sqlite3.connect('spells.db')
db_conn.text_factory = str
db_cursor = db_conn.cursor()

random_spell(db_cursor, choice_weights, spell_level, spell_type)
