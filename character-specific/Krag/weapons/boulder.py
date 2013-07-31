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

from dice_rolling import damage_roll, attack_roll


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

#################
# THROW BOULDER #
#################


def throw_boulder(char_stats):

    total_damage = 0
    boulder_attack_bonus = char_stats['BAB'] + char_stats['StrMod'] + char_stats['AttackSizeMod']
    boulder_attack_bonus += char_stats['MoraleAttack']

    #Range mod
    distance = int(raw_input('\n\nHow far away is the target? (in feet) '))
    if distance >= char_stats['BoulderRange'] * 5:
        print "Target too far away"
        return total_damage

    range_penalty = 0
    while distance >= char_stats['BoulderRange']:
        distance -= char_stats['BoulderRange']
        range_penalty += 1

    #Attack roll
    total_attack_roll, multiplier = attack_roll(char_stats, boulder_attack_bonus, range_penalty)
    hit = raw_input('Did it hit? (y|n) ')
    if hit.lower().startswith('n'):
        return total_damage

    #Damage roll
    damage_mod = char_stats['StrMod'] + char_stats['MoraleDmg']
    damage_dice = {
        'num_of_dice': 2,
        'num_of_sides': 8,
        'total_mod': damage_mod,
        'multiplier': multiplier
    }
    total_damage = damage_roll(char_stats, damage_dice)

    return total_damage
