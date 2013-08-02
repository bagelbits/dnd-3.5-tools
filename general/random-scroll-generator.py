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
    header_color = colorz.BLUE
    text_color = colorz.WHITE

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
    stdout.write("    %s%s %s[%s]%s\n" % (text_color, spell_name, colorz.GREY, ", ".join(spell_books), colorz.ENDC))

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
    stdout.write("%s%s%s" % (text_color, "/".join(spell_schools), colorz.GREY))

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
    stdout.write("\n%s" % (colorz.ENDC))

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
    stdout.write("%sLevel:%s %s%s\n" % (header_color, text_color, ", ".join(spell_classes), colorz.ENDC))

    #####################
    # Spell Componentes #
    #####################
    db_cursor.execute("SELECT component_id FROM spell_component WHERE spell_id = ?", (spell_id,))
    component_meta_info = db_cursor.fetchall()
    spell_components = []
    if component_meta_info:
        for component_id in component_meta_info:
            component_id = component_id[0]
            db_cursor.execute("SELECT short_hand FROM component WHERE id = ?", (component_id,))
            spell_components.append(db_cursor.fetchone()[0])
        stdout.write("%sComponents:%s %s%s\n" % (header_color, text_color, ", ".join(spell_components), colorz.ENDC))


    #####################
    # Spell Description #
    #####################
    db_cursor.execute("SELECT * FROM spell WHERE id = ?", (spell_id,))
    spell_meta_info = db_cursor.fetchone()
    if spell_meta_info[2]:
        stdout.write("%sCasting Time:%s %s%s\n" % (header_color, text_color, spell_meta_info[2], colorz.ENDC))
    if spell_meta_info[3]:
        stdout.write("%sRange:%s %s%s\n" % (header_color, text_color, spell_meta_info[3], colorz.ENDC))
    if spell_meta_info[4]:
        stdout.write("%sTarget:%s %s%s\n" % (header_color, text_color, spell_meta_info[4], colorz.ENDC))
    if spell_meta_info[5]:
        stdout.write("%sEffect:%s %s%s\n" % (header_color, text_color, spell_meta_info[5], colorz.ENDC))
    if spell_meta_info[6]:
        stdout.write("%sArea:%s %s%s\n" % (header_color, text_color, spell_meta_info[6], colorz.ENDC))
    if spell_meta_info[7]:
        stdout.write("%sDuration:%s %s%s\n" % (header_color, text_color, spell_meta_info[7], colorz.ENDC))
    if spell_meta_info[8]:
        stdout.write("%sSaving Throw:%s %s%s\n" % (header_color, text_color, spell_meta_info[8], colorz.ENDC))
    if spell_meta_info[9]:
        stdout.write("%sSpell Resistance:%s %s%s\n" % (header_color, text_color, spell_meta_info[9], colorz.ENDC))
    if spell_meta_info[10]:
        stdout.write("    %s%s%s\n" % (text_color, spell_meta_info[10], colorz.ENDC))

    stdout.write("\n")


def random_spell(db_cursor, choice_weights, spell_level, spell_type):
    frequency_weights = choice_weights['frequency_weights']
    general_class_weights = choice_weights['general_class_weights']
    domain_class_weights = choice_weights['domain_class_weights']
    domain_feat_weights = choice_weights['domain_feat_weights']

    print "%sPicking random spell....%s" % (colorz.PURPLE, colorz.ENDC)
    # Select either Common, Uncommon, or Rare
    select_freq = weighted_choice(frequency_weights)
    #print select_freq

    # Select class in that frequency category
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

    # Select if normal spells or domain/feats
    select_class_domain = weighted_choice(domain_class_weights)

    # Now select the spell
    if select_class_domain == 'class':
        db_cursor.execute("SELECT spell_id FROM spell_class\
                           WHERE class_id = ? AND level = ?", (select_class, spell_level))
        class_spells = db_cursor.fetchall()
        select_spell = random.choice(class_spells)[0]
    else:
        #Class specific should be more likely than any class.
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

        #Now pick the spell
        db_cursor.execute("SELECT spell_id FROM spell_domain_feat\
                           WHERE domain_feat_id = ? AND level = ?",
                          (select_domain_feat, spell_level))
        domain_feat_spells = db_cursor.fetchall()
        select_spell = random.choice(domain_feat_spells)[0]
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

spell_level = raw_input("%sSpell level for scroll? %s" % (colorz.CYAN, colorz.ENDC))
spell_type = raw_input("%sArcane or Divine? %s" % (colorz.CYAN, colorz.ENDC))
if spell_type.lower().startswith('a'):
    spell_type = 'arcane'
elif spell_type.lower().startswith('d'):
    spell_type = 'divine'
else:
    print "%sThat's not a valid type.%s" % (colorz.RED, colorz.ENDC)
    system.exit()

db_conn = sqlite3.connect('spells.db')
db_conn.text_factory = str
db_cursor = db_conn.cursor()

random_spell(db_cursor, choice_weights, spell_level, spell_type)
