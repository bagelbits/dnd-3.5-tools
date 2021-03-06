#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
    General Skill Check Roller
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


"""
This will do any skill rolls for the xml that you can
grab from thetangledweb.net
"""


from random import randint
import xml.etree.ElementTree as ET
import re


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


def roll_dice(dice=1, sides=6):
    try:
        return [randint(1, sides) for x in range(dice)]
    except:
        return []


def general_skill_roll(total_mod=0):
    total_dc_roll = 0

    print "%sRoll: 1d20 + %d" % (colorz.PURPLE, total_mod)

    base_dc_roll = sum(roll_dice(1, 20))

    print "%sBase roll: %d" % (colorz.PURPLE, base_dc_roll)

    #EXPLODING DICE
    while base_dc_roll == 20:
        total_mod += base_dc_roll
        print "%sExploding dice! Roll again%s" % (colorz.RED, colorz.PURPLE)
        print "Roll: 1d20 + %d" % (total_mod)

        base_dc_roll = sum(roll_dice(1, 20))

        print "%sBase roll: %d" % (colorz.PURPLE, base_dc_roll)

    if base_dc_roll == 1:
        print "%sCritical Failure!%s" % (colorz.RED, colorz.PURPLE)

    total_dc_roll += total_mod + base_dc_roll
    print "Total roll result: %d%s\n" \
        % (total_dc_roll, colorz.GREEN)


def skill_grabber(file_name):
    xml_skill_table = {}
    tree = ET.parse(file_name)
    root = tree.getroot()
    for node in root.findall("./data/node"):
        if node.attrib['name'].startswith("Skill"):
            result = re.match("Skill(\d\d)(.*)$", node.attrib['name'])
            if not result.group(2):
                xml_skill_table[int(result.group(1))] = {'name': node.text}
            else:
                xml_skill_table[int(result.group(1))][result.group(2)] = node.text

    skill_table = {}
    for key in sorted(xml_skill_table):
        skill_table[xml_skill_table[key]['name']] \
            = int(xml_skill_table[key]['Mod'])

    return skill_table

print colorz.GREEN
name = raw_input("Enter character's name: ")
#name = "Krag"
file_name = "../character-sheets/" + name + ".xml"
skill_table = skill_grabber(file_name)

print "\n%sRemember to add in situational mods to results!!!" % colorz.RED

while True:
    print colorz.BLUE
    skill_to_roll \
        = raw_input("Enter a partial or full skill name or 'quit' to exit: ")
    if skill_to_roll == 'quit':
        break
    for key in sorted(skill_table):
        if skill_to_roll.lower() in key.lower():
            print "%s%s" % (colorz.BLUE, key)
            general_skill_roll(skill_table[key])

print colorz.ENDC
