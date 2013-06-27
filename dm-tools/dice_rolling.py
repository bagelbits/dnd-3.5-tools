#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
    Damage Calculator for my character, Krag
    Written by Christopher Durien Ward

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

from random import randint


#For making text all colorful and easier to read.
class colorz:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


########################################################
#                   DICE ROLLERS                       #
# Subroutines for General DC, Attack, and Damage rolls #
########################################################

def roll_dice(dice=1, sides=6):
    try:
        return [randint(1, sides) for x in range(dice)]
    except:
        return []


####################
# GENEREAL DC ROLL #
####################

def general_dc_roll(char_stats, dc_name, total_mod=0):
    num_of_dice = 1
    num_of_sides = 20
    total_dc_roll = 0
    result_color = colorz.YELLOW

    if char_stats['AutoRoll']:
        base_dc_roll = sum(roll_dice(num_of_dice, num_of_sides))
    else:
        print "%s%s roll: 1d20 + %d" % (colorz.PURPLE, dc_name, total_mod)
        print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
        base_dc_roll = raw_input('What did you roll? ')
        base_dc_roll = base_dc_roll.split(",")
        base_dc_roll = sum(int(x) for x in base_dc_roll)

    #print "%sBase roll: %d" % (colorz.PURPLE, base_dc_roll)

    #EXPLODING DICE
    while base_dc_roll == 20:
        result_color = colorz.PURPLE
        total_mod += base_dc_roll

        if char_stats['AutoRoll']:
            base_dc_roll = sum(roll_dice(num_of_dice, num_of_sides))
        else:
            print "%s roll: 1d20 + %d" % (dc_name, total_mod)
            print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
            base_dc_roll = raw_input('What did you roll? ')
            base_dc_roll = base_dc_roll.split(",")
            base_dc_roll = sum(int(x) for x in base_dc_roll)

        #print "%sBase roll: %d" % (colorz.PURPLE, base_dc_roll)

    if base_dc_roll == 1:
        result_color = colorz.RED

    total_dc_roll += total_mod + base_dc_roll
    print "%s%s: %d%s" \
        % (result_color, dc_name, total_dc_roll, colorz.GREEN)
    return total_dc_roll
