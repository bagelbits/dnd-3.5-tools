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
import xml.etree.ElementTree as ET
import re


#For making text all colorful and easier to read.
class colorz:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


def stat_grabber(character_sheet):
    relevent_stats = {}
    character_sheet = ET.parse(character_sheet)
    root = character_sheet.getroot()
    for node in root.findall("./data/node"):
        #Calc HD and ECL
        if node.attrib['name'] == "Class":
            class_to_parse = node.text
            class_to_parse = class_to_parse.split("/")
            relevent_stats['hd'] = 0
            for class_name in class_to_parse:
                result = re.search("(\d+)$", class_name)
                if result.group(1):
                    relevent_stats['hd'] += int(result.group(1))
            continue

        if node.attrib['name'] == "Level":
            relevent_stats['level'] = node.text
            continue

        if node.attrib['name'] == "HP":
            relevent_stats['hp'] = node.text
            continue

        if node.attrib['name'].endswith("AC"):
            relevent_stats[node.attrib['name']] = node.text
            continue

        if node.attrib['name'] == "Fort":
            relevent_stats['fort'] = node.text
            continue

        if node.attrib['name'] == "Reflex":
            relevent_stats['reflex'] = node.text
            continue

        if node.attrib['name'] == "Will":
            relevent_stats['will'] = node.text
            continue

        if node.attrib['name'] == "Size":
            relevent_stats['size'] = node.text
            continue

        if node.attrib['name'].endswith("Mod"):
            relevent_stats[node.attrib['name']] = node.text
            continue

        if node.attrib['name'] == "MABBase":
            relevent_stats['bab'] = node.text
            break

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


###############
# MAIN METHOD #
###############

# TODO: Shift this into stat grabber
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

character_sheet = "../../character-sheets/Krag.xml"
relevent_stats = stat_grabber(character_sheet)
print relevent_stats

char_stats = {}

#Offesnive stats
char_stats['HD'] = int(relevent_stats['hd'])
char_stats['StrMod'] = int(relevent_stats['StrMod'])
char_stats['ConMod'] = int(relevent_stats['ConMod'])
if relevent_stats['StrTempMod']:
    char_stats['StrMod'] = int(relevent_stats['StrTempMod'])
char_stats['BAB'] = int(relevent_stats['bab'])

char_stats['StrSizeMod'] = int(STR_check_size[relevent_stats['size']])
char_stats['AttackSizeMod'] = int(attack_based_size[relevent_stats['size']])

char_stats['ShieldEnchance'] = 1
char_stats['BoulderRange'] = 50
char_stats['MoraleAttack'] = 0
char_stats['MoraleDmg'] = 0

char_stats['PowerAttack'] = 0
char_stats['Charging'] = False

#Defensive stats
char_stats['HP'] = int(relevent_stats['hp'])
char_stats['Level'] = int(relevent_stats['level'])
char_stats['AC'] = int(relevent_stats['AC'])
char_stats['TouchAC'] = int(relevent_stats['TouchAC'])
char_stats['FFAC'] = int(relevent_stats['FFAC'])
char_stats['Fort'] = int(relevent_stats['fort'])
char_stats['Reflex'] = int(relevent_stats['reflex'])
char_stats['Will'] = int(relevent_stats['will'])

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
    print "Current HP: %s" % char_stats['HP']
    print "AC stats:\nAC: %s\tTouch AC: %s\tFlatfooted AC: %s" \
        % (char_stats['AC'], char_stats['TouchAC'], char_stats['FFAC'])
    print "Save stats:\nFort: %s\tReflex: %s\tWill: %s" \
        % (char_stats['Fort'], char_stats['Reflex'], char_stats['Will'])

    hp_loss = raw_input('HP lossed since turn ended? (Negative numbers heal): ')
    char_stats['HP'] -= int(hp_loss)

    print "HP is now: %s" % char_stats['HP']

    #Charging?
    if not fatigued:
        char_stats['Charging'] = raw_input('Are you charging? (y|n) ')
        if char_stats['Charging'].lower().startswith('y'):
            char_stats['Charging'] = True

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
            char_stats['StrMod'] += 2
            char_stats['ConMod'] += 2
            char_stats['Will'] += 2
            char_stats['HP'] += 2 * int(relevent_stats['level'])
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
            char_stats['StrMod'] -= 3
            char_stats['ConMod'] -= 2
            char_stats['Will'] -= 2
            char_stats['AC'] += 2
            char_stats['TouchAC'] += 2
            char_stats['FFAC'] += 2
            char_stats['HP'] -= 2 * int(relevent_stats['level'])
            fatigued = True

    damage_summary(total_damage, cleave_damage)

    again = raw_input('Continue? (y|n) ')
    if again.lower().startswith('n'):
        break

    round_num += 1

print colorz.ENDC
