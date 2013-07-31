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
    GREY = '\033[90m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
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

    print "\n%s%s roll: %dd%d + %d" \
        % (colorz.PURPLE, dc_name, num_of_dice, num_of_sides, total_mod)

    if char_stats['AutoRoll']:
        base_dc_roll = sum(roll_dice(num_of_dice, num_of_sides))
    else:
        print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
        base_dc_roll = raw_input('What did you roll? ')
        base_dc_roll = base_dc_roll.split(",")
        base_dc_roll = sum(int(x) for x in base_dc_roll)

    print "\n%sBase roll: %d\n" % (colorz.PURPLE, base_dc_roll)

    #EXPLODING DICE
    while base_dc_roll == 20:
        total_mod += base_dc_roll
        print "%s\nExploding dice! Roll again%s" % (colorz.RED, colorz.PURPLE)
        print "%s roll: %dd%d + %d" \
            % (dc_name, num_of_dice, num_of_sides, total_mod)

        if char_stats['AutoRoll']:
            base_dc_roll = sum(roll_dice(num_of_dice, num_of_sides))
        else:
            print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
            base_dc_roll = raw_input('What did you roll? ')
            base_dc_roll = base_dc_roll.split(",")
            base_dc_roll = sum(int(x) for x in base_dc_roll)

        print "\n%sBase roll: %d\n" % (colorz.PURPLE, base_dc_roll)

    if base_dc_roll == 1:
        print "%s\nCritical Failure!%s" % (colorz.RED, colorz.PURPLE)

    total_dc_roll += total_mod + base_dc_roll
    print "Total %s roll result: %d%s\n" \
        % (dc_name, total_dc_roll, colorz.GREEN)
    return total_dc_roll


###############
# ATTACK ROLL #
###############

def attack_roll(char_stats, total_attack_bonus=0, range_penalty=0):

    multiplier = 1
    print "\n%sAttack roll: 1d20 + %d - %d" \
        % (colorz.BLUE, total_attack_bonus, range_penalty)

    if char_stats['AutoRoll']:
        base_attack_roll = sum(roll_dice(1, 20))
    else:
        print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
        base_attack_roll = int(raw_input('What did you roll? '))

    print "\n%sBase roll: %d\n" % (colorz.BLUE, base_attack_roll)

    while base_attack_roll == 20:
        multiplier += 1
        print "%s\nGotta crit! Roll to confirm!%s" % (colorz.RED, colorz.BLUE)
        print "\nAttack roll: 1d20 + %d - %d" \
            % (total_attack_bonus, range_penalty)

        if char_stats['AutoRoll']:
            base_attack_roll = sum(roll_dice(1, 20))
        else:
            print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
            base_attack_roll = int(raw_input('What did you roll? '))

        print "\n%sBase roll: %d\n" % (colorz.BLUE, base_attack_roll)

    if base_attack_roll == 1:
        print "%sCritical Failure!%s" % (colorz.RED, colorz.BLUE)

    #Addin in mods
    roll_mod = total_attack_bonus
    roll_mod -= range_penalty
    total_attack = base_attack_roll + roll_mod

    print "Total Attack roll result: %d" % total_attack
    if multiplier > 1:
        print "Total multiplier: %dx" % multiplier

    print colorz.GREEN
    return total_attack, multiplier


###############
# DAMAGE ROLL #
###############

def damage_roll(char_stats, dice):
    if 'damage_doubling' in dice:
        dice['num_of_dice'] *= dice['damage_doubling']
        dice['total_mod'] *= dice['damage_doubling']
    print colorz.RED

    if 'multiplier' in dice and dice['multiplier'] > 1:
        print "Damage roll: %dd%d + %d X%d" \
            % (dice['num_of_dice'], dice['num_of_sides'], dice['total_mod'], dice['multiplier'])
    else:
        print "Damage roll: %dd%d + %d" \
            % (dice['num_of_dice'], dice['num_of_sides'], dice['total_mod'])

    if char_stats['AutoRoll']:
        total_damage = sum(roll_dice(dice['num_of_dice'], dice['num_of_sides']))
    else:
        print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
        total_damage = raw_input('What did you roll? ')
        total_damage = total_damage.split(",")
        total_damage = sum(int(x.strip()) for x in total_damage)

    print "%sBase roll: %d\n" % (colorz.RED, total_damage)

    #Last minute mods
    total_damage += dice['total_mod']
    if 'multiplier' in dice:
        total_damage *= dice['multiplier']

    #TOTAL
    print "Damage roll result: %d%s\n" % (total_damage, colorz.GREEN)
    return total_damage
