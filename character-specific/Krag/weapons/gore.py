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

###############
# GORE ATTACK #
###############


def gore_attack(char_stats, cleave=False):

    total_damage = 0
    cleave_damage = 0

    ####Attack roll####
    gore_attack_bonus = char_stats['BAB'] + char_stats['StrMod'] + char_stats['AttackSizeMod']
    gore_attack_bonus -= 5     # Natural off hand weapon penalty
    gore_attack_bonus -= char_stats['PowerAttack']  # Power attack penalty
    gore_attack_bonus += char_stats['MoraleAttack']
    if char_stats['Charging']:
        gore_attack_bonus += 2

    total_attack_roll, multiplier = attack_roll(char_stats, gore_attack_bonus)
    hit = raw_input('Did it hit? (y|n) ')
    if hit.lower().startswith('n'):
        if cleave:
            return cleave_damage
        return total_damage, cleave_damage

    ####Damage roll####
    damage_mod = char_stats['StrMod'] // 2 + char_stats['PowerAttack'] + char_stats['MoraleDmg']
    damage_dice = {
        'num_of_dice': 1,
        'num_of_sides': 8,
        'total_mod': damage_mod,
        'multiplier': multiplier
    }
    total_damage = damage_roll(char_stats, damage_dice)

    #Dealing with cleave
    if cleave:
        return total_damage

    print colorz.YELLOW
    cleave = raw_input("Did it cleave? (y|n) ")
    if cleave.lower().startswith('y'):
        print "%sCleaving....\n%s" % (colorz.PURPLE, colorz.GREEN)
        cleave_damage += gore_attack(True)

    return total_damage, cleave_damage