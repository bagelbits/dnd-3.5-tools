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

from dice_rolling.py import attack_roll, damage_roll, general_dc_roll


#For making text all colorful and easier to read.
class colorz:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

#################
# SHIELD ATTACK #
#################


def shield_attack(char_stats, cleave=False):
    global char_stats

    cleave_targets = {}
    targets = {}
    damage_doubling = 1

    print '\nMighty swing used. Please pick 3 adjacent squares.'
    raw_input('(Press enter to continue)')

    ####Attack roll####
    shield_attack_bonus = char_stats['BAB'] + char_stats['StrMod'] + char_stats['AttackSizeMod']
    shield_attack_bonus += char_stats['ShieldEnchance']
    shield_attack_bonus -= char_stats['PowerAttack']  # Power attack penalty
    shield_attack_bonus += char_stats['MoraleAttack']
    if char_stats['Charging']:
        shield_attack_bonus += 2
        damage_doubling += 1

    total_attack_roll, multiplier = attack_roll(char_stats, shield_attack_bonus)
    hits = int(raw_input('How many things were hit? '))
    if hits == 0:
        if cleave:
            return cleave_targets
        return targets, cleave_targets

    # Damage roll with mighty swing, shield charge,
    # shield slam, knockback... yay for fun times
    damage_mod = char_stats['StrMod'] * 1.5 + char_stats['PowerAttack'] * 2 + char_stats['ShieldEnchance']
    damage_mod += char_stats['MoraleDmg']

    for target in range(1, hits + 1):
        target_name = 'Target %d' % target
        print "\n####%s####" % target_name
        damage_dice = {
            'num_of_dice': 2,
            'num_of_sides': 6,
            'total_mod': damage_mod,
            'multiplier': multiplier,
            'damage_doubling': damage_doubling
        }
        total_damage = damage_roll(char_stats, damage_dice)

        if char_stats['Charging']:
            #Free Trip attempt
            print "\n%s++Free Trip attempt++" % colorz.YELLOW
            total_damage += trip_attempt(char_stats, target_name, shield_attack_bonus, damage_mod, damage_doubling)

        #Shield daze
        shield_daze(char_stats, target_name)

        #Knockback with bull rush check
        if char_stats['PowerAttack']:
            total_damage += knockback(char_stats)

        targets[target_name] = total_damage

    if cleave:
        return targets

    print colorz.RED
    for target in targets.keys():
        print "Total damage for %s: %d" % (target, targets[target])

    print colorz.YELLOW
    cleave = raw_input("\n\nDid it cleave? (y|n) ")
    if cleave.lower().startswith('y'):
        print "%sCleaving....\n%s" % (colorz.PURPLE, colorz.GREEN)
        cleave_targets = shield_attack(True)

    return targets, cleave_targets


def shield_daze(char_stats, target_name):
    print "\n%s++Shield daze++" % colorz.PURPLE
    fort_save = 10 + char_stats['HD'] // 2 + char_stats['StrMod']
    print "%s must make Fort save and beat %d or be Dazed for one round" \
        % (target_name, fort_save)
    raw_input("Press Enter to continue..." + colorz.GREEN)


def trip_attempt(char_stats, target_name, attack_bonus, damage_bonus, damage_doubling=1):
    can_trip = raw_input('Enemy bigger than huge? (y|n) ')
    if can_trip.lower().startswith('n'):
        general_dc_roll(char_stats, "Touch attack", char_stats['StrMod'] + char_stats['BAB'])
        print colorz.YELLOW
        touch_success = raw_input('Did touch attack succeeed? (y|n) ')

        if touch_success.lower().startswith('y'):
            #+4 for Improved Trip
            trip_str_mod = char_stats['StrMod'] + char_stats['StrSizeMod'] + 4
            trip_str_check = general_dc_roll(char_stats, "Strength check", trip_str_mod)
            print "\nStrength check to beat: %d" % trip_str_check
            tripped = raw_input('Did you trip it? (y|n) ')

            if tripped.lower().startswith('y'):
                print "\n++Free attack!++"
                #+4 because they're prone
                throw_away, multiplier = attack_roll(char_stats, attack_bonus + 4)
                print colorz.YELLOW
                hit = raw_input('Did it hit? (y|n) ')
                if hit.lower().startswith('y'):
                    damage_dice = {
                        'num_of_dice': 2,
                        'num_of_sides': 6,
                        'total_mod': damage_bonus,
                        'multiplier': multiplier,
                        'damage_doubling': damage_doubling
                    }
                    total_damage = damage_roll(char_stats, damage_dice)
                    #Free Attack Shield Daze
                    shield_daze(target_name)
                    return total_damage
    return 0


def knockback(char_stats):
    print "\n%s++Knockback++" % colorz.BLUE
    print "Bull rush check roll:"
    #+4 for Improved Bull Rush
    bull_rush_mod = char_stats['StrSizeMod'] + char_stats['StrMod'] + 4
    bull_rush_check = general_dc_roll(char_stats, "Bull rush", bull_rush_mod)
    knockback_distance = 0
    print colorz.BLUE
    opposing_bull_rush_check = int(raw_input("Opposing bull rush check? "))
    if bull_rush_check > opposing_bull_rush_check:
        knockback_distance += 5
        br_check_diff = bull_rush_check - opposing_bull_rush_check
        while br_check_diff > 5:
            knockback_distance += 5
            br_check_diff -= 5

    print "\nTarget knocked back %d feet%s" \
        % (knockback_distance, colorz.GREEN)
    if knockback_distance > 0:
        hit = raw_input("Did target hit a wall/solid object? (y|n) ")
        if hit.lower().startswith('y'):
            damage_dice = {
                'num_of_dice': 4,
                'num_of_sides': 6,
                'total_mod': char_stats['StrMod'] * 2,
            }
            total_damage = damage_roll(char_stats, damage_dice)
            return total_damage
    return 0
