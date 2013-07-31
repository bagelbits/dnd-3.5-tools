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

from weapons.shield import shield_attack
from weapons.gore import gore_attack
from weapons.boulder import throw_boulder
from dice_rolling import general_dc_roll
from math import floor
import xml.etree.ElementTree as ET
import re


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


#It's a lot fucking easier if I just load it all and pick out what I need.
def stat_grabber(character_sheet):
    relevent_stats = {}
    character_sheet = ET.parse(character_sheet)
    root = character_sheet.getroot()
    for node in root.findall("./data/node"):
        #Calc HD and ECL
        if node.attrib['name'] == "Class":
            class_to_parse = node.text
            class_to_parse = class_to_parse.split("/")
            relevent_stats['HD'] = 0
            for class_name in class_to_parse:
                result = re.search("(\d+)$", class_name)
                if result.group(1):
                    relevent_stats['HD'] += int(result.group(1))

        relevent_stats[node.attrib['name']] = node.text

    return relevent_stats


def damage_summary(total_damage, cleave_damage):
    #Print out damage summary!
    print "\n\n%s####Damage done this round####" % colorz.RED
    if total_damage:
        print "\nRegular Damage: "
        if 'shield' in total_damage:
            print "-Shield:"
            for target in total_damage['shield'].keys():
                print "--%s: %d" % (target, total_damage['shield'][target])

            if not total_damage['shield']:
                print "-- None"

        if 'gore' in total_damage:
            print "-Gore: %d" % total_damage['gore']

        if 'boulder' in total_damage:
            print "-Boulder: %d" % total_damage['boulder']

    if cleave_damage:
        print "\nCleave Damage: "
        if 'shield' in cleave_damage:
            print "-Shield:"
            for target in cleave_damage['shield'].keys():
                print "--%s: %d" % (target, cleave_damage['shield'][target])

            if not cleave_damage['shield']:
                print "-- None"

        if 'gore' in cleave_damage:
            print "-Gore: %d" % cleave_damage['gore']
    print colorz.YELLOW


def adjust_all_mods(char_stats):
    ability_stats = [
        'Str',
        'Dex',
        'Con',
        'Int',
        'Wis',
        'Cha']

    #We also need to readjust HP for con changes and AC for dex changes
    old_con_mod = char_stats['ConMod']
    old_dex_mod = char_stats['DexMod']
    for ability_stat in ability_stats:
        stat_to_calc = char_stats[ability_stat]
        mod_result = int(floor((stat_to_calc - 10) / 2.0))
        char_stats[ability_stat + 'Mod'] = mod_result

    #Auto adjust saves but only if initialized
    char_stats = adjust_all_saves(char_stats)

    #Now adjust HP
    hp_adjust = char_stats['ConMod'] - old_con_mod
    char_stats['HP'] += hp_adjust * char_stats['Level']

    #Now adjust Touch and Normal AC
    ac_adjust = char_stats['DexMod'] - old_dex_mod
    char_stats['TouchAC'] += ac_adjust
    char_stats['AC'] += ac_adjust
    return char_stats


def adjust_all_saves(char_stats):
    saves = ['Fort', 'Will', 'Reflex']
    for save in saves:
        char_stats[save] = char_stats[save + "Base"]
        if save == 'Fort':
            char_stats[save] += char_stats['ConMod']
        if save == 'Reflex':
            char_stats[save] += char_stats['DexMod']
        if save == 'Will':
            char_stats[save] += char_stats['WisMod']
        char_stats[save] += char_stats[save + "Magic"]
        char_stats[save] += char_stats[save + "Misc"]
        char_stats[save] += char_stats[save + "Temp"]

    return char_stats


def defensive_round(char_stats):
    defensive = True
    while defensive:
        print colorz.GREEN
        print "Current HP: %s" % char_stats['HP']
        print "AC stats:\nAC: %s\tTouch AC: %s\tFlatfooted AC: %s" \
            % (char_stats['AC'], char_stats['TouchAC'], char_stats['FFAC'])
        print "Save stats:\nFort: %s\tReflex: %s\tWill: %s%s" \
            % (char_stats['Fort'], char_stats['Reflex'], char_stats['Will'], colorz.YELLOW)

        hp_loss = raw_input('HP lossed since turn ended? (Positive numbers heal): ')
        char_stats['HP'] += int(hp_loss)

        print "%sHP is now: %s%s\n" % (colorz.GREEN, char_stats['HP'], colorz.YELLOW)

        ability_dmg = raw_input('Ability damage? (e.g. Str -4) ')
        ability_dmg = ability_dmg.split(" ")
        ability_dmg[1] = int(ability_dmg[1])
        char_stats[ability_dmg[0]] += int(ability_dmg[1])
        while ability_dmg:
            ability_dmg = raw_input('More? ')
            ability_dmg = ability_dmg.split(" ")
            ability_dmg[1] = int(ability_dmg[1])
            char_stats[ability_dmg[0]] += int(ability_dmg[1])
        char_stats = adjust_all_mods(char_stats)

        defensive_answer = raw_input('Your turn yet? ')
        if defensive_answer.lower().startswith('y'):
            defensive = False


def init_char_stats(relevent_stats):
    char_stats = {}
    STR_check_size = {
        'Fine': -16,
        'Diminutive': -12,
        'Tiny': -8,
        'Small': -4,
        'Medium': 0,
        'Large': 4,
        'Huge': 8,
        'Gargantuan': 12,
        'Colossal': 16}
    attack_based_size = {
        'Fine': 8,
        'Diminutive': 4,
        'Tiny': 2,
        'Small': 1,
        'Medium': 0,
        'Large': -1,
        'Huge': -2,
        'Gargantuan': -4,
        'Colossal': -8}
    ability_stats = [
        'Str',
        'Dex',
        'Con',
        'Int',
        'Wis',
        'Cha']

    #Offesnive stats
    char_stats['HD'] = int(relevent_stats['HD'])

    #Calculate out all mods, for kicks. Don't forget temps
    for ability_stat in ability_stats:
        char_stats[ability_stat] = int(relevent_stats[ability_stat])
        if ability_stat + 'Temp' in relevent_stats:
            char_stats[ability_stat] = int(relevent_stats[ability_stat + 'Temp'])
        stat_to_calc = char_stats[ability_stat]
        mod_result = int(floor((stat_to_calc - 10) / 2.0))
        char_stats[ability_stat + 'Mod'] = mod_result

    print char_stats
    char_stats['BAB'] = int(relevent_stats['MABBase'])

    char_stats['StrSizeMod'] = int(STR_check_size[relevent_stats['Size']])
    char_stats['AttackSizeMod'] = int(attack_based_size[relevent_stats['Size']])

    char_stats['ShieldEnchance'] = 1
    char_stats['ShieldEnchance'] = 5
    char_stats['BoulderRange'] = 50
    char_stats['MoraleAttack'] = 0
    char_stats['MoraleDmg'] = 0

    # Marrions Spells
    char_stats['MoraleAttack'] += 3
    char_stats['MoraleDmg'] += 3

    char_stats['PowerAttack'] = 0
    char_stats['Charging'] = False

    # Defensive stats
    char_stats['HP'] = int(relevent_stats['HP'])
    char_stats['Level'] = int(relevent_stats['Level'])
    char_stats['AC'] = int(relevent_stats['AC'])
    char_stats['TouchAC'] = int(relevent_stats['TouchAC'])
    char_stats['FFAC'] = int(relevent_stats['FFAC'])

    # Saves
    char_stats['Fort'] = int(relevent_stats['Fort'])
    char_stats['Reflex'] = int(relevent_stats['Reflex'])
    char_stats['Will'] = int(relevent_stats['Will'])
    char_stats['FortBase'] = int(relevent_stats['FortBase'])
    char_stats['ReflexBase'] = int(relevent_stats['ReflexBase'])
    char_stats['WillBase'] = int(relevent_stats['WillBase'])
    char_stats['FortMagic'] = int(relevent_stats['FortMagic'])
    char_stats['ReflexMagic'] = int(relevent_stats['ReflexMagic'])
    char_stats['WillMagic'] = int(relevent_stats['WillMagic'])
    char_stats['FortMisc'] = int(relevent_stats['FortMisc'])
    char_stats['ReflexMisc'] = int(relevent_stats['ReflexMisc'])
    char_stats['WillMisc'] = int(relevent_stats['WillMisc'])
    char_stats['FortTemp'] = int(relevent_stats['FortTemp'])
    char_stats['ReflexTemp'] = int(relevent_stats['ReflexTemp'])
    char_stats['WillTemp'] = int(relevent_stats['WillTemp'])

    # Magic Tattoo
    char_stats['MoraleAttack'] += 2
    char_stats['AC'] += 1
    char_stats['FortMagic'] += 2
    char_stats['ReflexMagic'] += 2
    char_stats['WillMagic'] += 2
    char_stats = adjust_all_saves(char_stats)

    return char_stats


###############
# MAIN METHOD #
###############

# TODO: Shift this into stat grabber

character_sheet = "../../character-sheets/Krag.xml"
relevent_stats = stat_grabber(character_sheet)
char_stats = init_char_stats(relevent_stats)

rage_used = False
rage_started = False
rage_rounds = -1
fatigued = False

total_damage = {}
cleave_damage = {}

print colorz.PURPLE
print "############################################"
print "#      WELCOME! TO KRAG'S DAMAGE CALC!     #"
print "############################################"

print colorz.YELLOW
char_stats['AutoRoll'] = False
char_stats['AutoRoll'] = raw_input('Auto roll dice?(y|n) ')
if char_stats['AutoRoll'].lower().startswith('y'):
    char_stats['AutoRoll'] = True

round_num = 1

while True:
    char_stats['Charging'] = False

    print "\n%sCombat round #%d%s" % (colorz.BLUE, round_num, colorz.YELLOW)
    if rage_started:
        print "\n%sRounds of rage left: %s%s" % (colorz.RED, rage_rounds, colorz.YELLOW)

    #print AC, Current HP, save bonuses
    char_stats = defensive_round(char_stats)

    #Charging?
    if not fatigued:
        char_stats['Charging'] = raw_input('\nAre you charging? (y|n) ')
        if char_stats['Charging'].lower().startswith('y'):
            char_stats['Charging'] = True
        else:
            char_stats['Charging'] = False

    #Power attack?
    char_stats['PowerAttack'] = int(raw_input('How many points to power attack? (Max %s) '
                                    % char_stats['BAB']))
    if char_stats['PowerAttack'] > char_stats['BAB']:
        print "%sToo many points!%s" % (colorz.RED, colorz.ENDC)
        quit()

    #Let's rage!
    print colorz.YELLOW
    if not rage_used:
        answer = raw_input('Would you like to rage? (y|n) ')
        if answer.lower().startswith('y'):
            rage_started = True
            rage_used = True
            char_stats['Str'] += 4
            char_stats['Con'] += 4
            char_stats = adjust_all_mods(char_stats)
            char_stats['WillMisc'] += 2
            char_stats = adjust_all_saves(char_stats)
            char_stats['AC'] -= 2
            char_stats['TouchAC'] -= 2
            char_stats['FFAC'] -= 2
            rage_rounds = 3 + char_stats['ConMod']
            print "\n%sRAGE MODE ACTIVATED~!" % colorz.RED

    # TODO: Implement Bear Mode
    if rage_started:
        pass

    #Choose your attacks!
    while(True):

        print colorz.GREEN
        attack = raw_input('\nWhat is your attack? (shield|gore|boulder|death move|none) ')
        if attack.lower() == 'shield':
            total_damage['shield'], cleave_damage['shield'] \
                = shield_attack(char_stats)

        elif attack.lower() == 'gore':
            total_damage['gore'], cleave_damage['gore'] \
                = gore_attack(char_stats)

        elif attack.lower() == 'boulder':
            if char_stats['Charging']:
                print "%sCan't throw boulder while charging.\n" % colorz.RED
            else:
                total_damage['boulder'] = throw_boulder(char_stats)

        elif attack.lower() == 'death move':
            str_roll = general_dc_roll("STR check", total_mod=char_stats['StrMod'])
            if str_roll > char_stats['StrMod'] + 1:
                print "%sDeath move successful!%s" % (colorz.RED, colorz.YELLOW)
                if char_stats['MoraleAttack'] < 1:
                    char_stats['MoraleAttack'] = 1
                if char_stats['MoraleDmg'] < 1:
                    char_stats['MoraleDmg'] = 1

        elif attack.lower() == 'none':
            break

        print colorz.YELLOW
        again = raw_input('\nAnother attack? (y|n) ')
        if again.lower().startswith('n'):
            break

    # Decrement my rage counter
    if rage_started:
        rage_rounds -= 1
        if rage_rounds == 0:
            rage_started = False
            print "%sRage is over!" % colorz.RED
            print "You are now fatigued!%s" % colorz.YELLOW
            char_stats['Str'] -= 6
            char_stats['Dex'] -= 2
            char_stats['Con'] -= 4
            char_stats = adjust_all_mods(char_stats)
            char_stats['WillMisc'] -= 2
            char_stats = adjust_all_saves(char_stats)
            char_stats['AC'] += 2
            char_stats['TouchAC'] += 2
            char_stats['FFAC'] += 2
            fatigued = True

    damage_summary(total_damage, cleave_damage)

    again = raw_input('Continue? (y|n) ')
    if again.lower().startswith('n'):
        break

    round_num += 1

print colorz.ENDC
