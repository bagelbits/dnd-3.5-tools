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
from sys import stdout


def weighted_choice(freq_weights):
    total = sum(freq_weights[freq] for freq in freq_weights)
    rand_choice = random.uniform(0, total)
    upto = 0
    for freq in freq_weights:
        upto += freq_weights[freq]
        if upto > rand_choice:
            return freq
    assert False, "Shouldn't get here"


def full_spell_description(db_cursor, spell_id):
#################
# Name and Book #
#################
    db_cursor.execute("SELECT name FROM spell WHERE id = ?", (spell_id, ))
    spell_name = db_cursor.fetchone()[0]
    db_cursor.execute("SELECT book_id, page FROM spell_book WHERE spell_id = ?", (spell_id,))
    book_meta_info = db_cursor.fetchall()
    spell_books = []
    for book in book_meta_info:
        book = list(book)
        db_cursor.execute("SELECT name FROM book WHERE id = ?", (book[0],))
        book[0] = db_cursor.fetchone()[0]
        if book[1]:
            book[1] = str(book[1])
            book[1] = "(pg %s)" % book[1]
        else:
            book[1] = ''
        book = " ".join(book).strip()
        spell_books.append(book)
    stdout.write("    %s [%s]\n" % (spell_name, ", ".join(spell_books)))

#####################################
# School, subschool, and descriptor #
#####################################
    db_cursor.execute("SELECT school_id FROM spell_school WHERE spell_id = ?", (spell_id,))
    school_meta_info = db_cursor.fetchall()
    spell_schools = []
    for school in school_meta_info:
        school_id = school[0]
        db_cursor.execute("SELECT name FROM school WHERE id = ?", (school_id,))
        spell_schools.append(db_cursor.fetchone()[0])
    stdout.write("/".join(spell_schools))

    db_cursor.execute("SELECT subschool_id FROM spell_subschool WHERE spell_id = ?", (spell_id,))
    subschool_meta_info = db_cursor.fetchall()
    if subschool_meta_info:
        spell_subschools = []
        for subschool in subschool_meta_info:
            subschool_id = subschool[0]
            db_cursor.execute("SELECT name FROM subschool WHERE id = ?", (subschool_id,))
            spell_subschools.append(db_cursor.fetchone()[0])
        stdout.write(" (%s)" % ", ".join(spell_subschools))

    db_cursor.execute("SELECT descriptor_id FROM spell_descriptor WHERE spell_id = ?", (spell_id,))
    descriptor_meta_info = db_cursor.fetchall()
    if descriptor_meta_info:
        spell_descriptors = []
        for descriptor in descriptor_meta_info:
            descriptor_id = descriptor[0]
            db_cursor.execute("SELECT name FROM descriptor WHERE id = ?", (descriptor_id,))
            spell_descriptors.append(db_cursor.fetchone()[0])
        stdout.write(" [%s]" % ", ".join(spell_descriptors))
    stdout.write("\n")

############################
# Classes and spell levels #
############################
    # Class #
    db_cursor.execute("SELECT class_id, level, subtype FROM spell_class WHERE spell_id = ?", (spell_id,))
    class_meta_info = db_cursor.fetchall()
    spell_classes = []
    for character_class in class_meta_info:
        class_id = character_class[0]
        db_cursor.execute("SELECT name FROM class WHERE id = ?", (class_id,))
        if character_class[2]:
            spell_classes.append(" ".join([db_cursor.fetchone()[0], "(%s)" % character_class[2], str(character_class[1])]))
        else:
            spell_classes.append(" ".join([db_cursor.fetchone()[0], str(character_class[1])]))
    # Domain #
    db_cursor.execute("SELECT domain_feat_id, level FROM spell_domain_feat WHERE spell_id = ?", (spell_id,))
    class_meta_info = db_cursor.fetchall()
    for character_class in class_meta_info:
        class_id = character_class[0]
        db_cursor.execute("SELECT name FROM domain_feat WHERE id = ?", (class_id,))
        spell_classes.append(" ".join([db_cursor.fetchone()[0], str(character_class[1])]))
    spell_classes = sorted(spell_classes)
    stdout.write("Level: %s\n" % ", ".join(spell_classes))

#####################
# Spell Componentes #
#####################
    #print spell[1]
    db_cursor.execute("SELECT component_id FROM spell_component WHERE spell_id = ?", (spell_id,))
    component_meta_info = db_cursor.fetchall()
    spell_components = []
    if component_meta_info:
        for component_id in component_meta_info:
            component_id = component_id[0]
            db_cursor.execute("SELECT short_hand FROM component WHERE id = ?", (component_id,))
            spell_components.append(db_cursor.fetchone()[0])
        stdout.write("Components: %s\n" % ", ".join(spell_components))


#####################
# Spell Description #
#####################
    db_cursor.execute("SELECT * FROM spell WHERE id = ?", (spell_id,))
    spell_meta_info = db_cursor.fetchone()
    if spell_meta_info[2]:
        stdout.write("Casting Time: %s\n" % spell_meta_info[2])
    if spell_meta_info[3]:
        stdout.write("Range: %s\n" % spell_meta_info[3])
    if spell_meta_info[4]:
        stdout.write("Target: %s\n" % spell_meta_info[4])
    if spell_meta_info[5]:
        stdout.write("Effect: %s\n" % spell_meta_info[5])
    if spell_meta_info[6]:
        stdout.write("Area: %s\n" % spell_meta_info[6])
    if spell_meta_info[7]:
        stdout.write("Duration: %s\n" % spell_meta_info[7])
    if spell_meta_info[8]:
        stdout.write("Saving Throw: %s\n" % spell_meta_info[8])
    if spell_meta_info[9]:
        stdout.write("Spell Resistance: %s\n" % spell_meta_info[9])
    if spell_meta_info[10]:
        stdout.write("    %s\n" % spell_meta_info[10])

    stdout.write("\n")


class colorz:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

frequency_weights = {
    'Common': 89,
    'Uncommon': 20,
    'Rare': 1,
    'None': 0
}

domain_class_weights = {
    'domain': 1,
    'class': 20
}

domain_feat_weights = {
    'class': 3,
    'any': 1
}

db_conn = sqlite3.connect('spells.db')
db_conn.text_factory = str
db_cursor = db_conn.cursor()

for x in range(1):
#for x in range(100):
    print "%sPicking random spell....%s" % (colorz.PURPLE, colorz.ENDC)
    # Select either Common, Uncommon, or Rare
    select_freq = weighted_choice(frequency_weights)
    #print select_freq

    # Select class in that frequency category
    db_cursor.execute("SELECT id, more_common FROM class WHERE frequency = ?", (select_freq, ))
    class_weights = {}
    for returned_class in db_cursor.fetchall():
        if returned_class[1] == 0:
            class_weights[returned_class[0]] = 1
        else:
            class_weights[returned_class[0]] = 10
    select_class = weighted_choice(class_weights)
    db_cursor.execute("SELECT name FROM class WHERE id = ?", (select_class, ))
    class_name = db_cursor.fetchone()[0]
    print "%s%s Spell%s" % (colorz.YELLOW, class_name, colorz.ENDC)

    # Select if normal spells or domain/feats
    select_class_domain = weighted_choice(domain_class_weights)

    # Now select the spell
    if select_class_domain == 'class':
        db_cursor.execute("SELECT spell_id FROM spell_class WHERE class_id = ?", (select_class, ))
        class_spells = db_cursor.fetchall()
        select_spell = random.choice(class_spells)[0]
    else:
        #Class specific should be more likely than any class.
        if weighted_choice(domain_feat_weights) == 'class':
            db_cursor.execute("SELECT domain_feat_id FROM class_domain_feat\
                           WHERE class_id = ?", (select_class, ))
        else:
            db_cursor.execute("SELECT domain_feat_id FROM class_domain_feat\
                           WHERE class_id = 0")

        domain_feat = db_cursor.fetchall()
        if not domain_feat:
            db_cursor.execute("SELECT domain_feat_id FROM class_domain_feat\
                           WHERE class_id = 0")
            domain_feat = db_cursor.fetchall()
        select_domain_feat = random.choice(domain_feat)[0]

        db_cursor.execute("SELECT name FROM domain_feat WHERE id = ?", (select_domain_feat, ))
        #print db_cursor.fetchone()[0]

        db_cursor.execute("SELECT spell_id FROM spell_domain_feat WHERE domain_feat_id = ?", (select_domain_feat, ))
        domain_feat_spells = db_cursor.fetchall()
        select_spell = random.choice(domain_feat_spells)[0]
    full_spell_description(db_cursor, select_spell)
