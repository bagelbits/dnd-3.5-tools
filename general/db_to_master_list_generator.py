#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
    Spell Database Checker and Master List generator
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

import sqlite3
from sys import stdout
from os import remove


class colorz:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


def spell_name_sort(spell_info):
    roman_numerals = {
        "i": 1,
        "ii": 2,
        "iii": 3,
        "iv": 4,
        "v": 5,
        "vi": 6,
        "vii": 7,
        "viii": 8,
        "ix": 9
    }
    name = spell_info[1].lower()
    name = name.replace(",", "\t")

    #Because fuck you roman numerals
    name = name.split(" ")
    if name[-1] in roman_numerals:
        name[-1] = str(roman_numerals[name[-1]])
    name = " ".join(name)
    return name


def test_file_generator(db_cursor, all_spells, alt_spells, test_master_file):
    line_count = 0
    for spell in all_spells:
        line_count += 1
        per = line_count / float(len(all_spells)) * 100
        stdout.write("%s\rGenerating: %d%%%s" % (colorz.PURPLE, per, colorz.ENDC))
        stdout.flush()

        # Handle alt spells
        if alt_spells:
            while True:
                if spell_name_sort(alt_spells[0]) < spell_name_sort(spell):
                    db_cursor.execute("SELECT name FROM spell WHERE id = ?", (alt_spells[0][0],))
                    alt_spell_name = db_cursor.fetchone()[0]
                    test_master_file.write("    %s\n" % alt_spells[0][1])
                    test_master_file.write("See \"%s\"\n" % alt_spell_name)
                    test_master_file.write("\n")
                    alt_spells.pop(0)
                    if not alt_spells:
                        break
                else:
                    break

    #################
    # Name and Book #
    #################
        spell_id = spell[0]
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
        test_master_file.write("    %s [%s]\n" % (spell[1], ", ".join(spell_books)))

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
        test_master_file.write("/".join(spell_schools))

        db_cursor.execute("SELECT subschool_id FROM spell_subschool WHERE spell_id = ?", (spell_id,))
        subschool_meta_info = db_cursor.fetchall()
        if subschool_meta_info:
            spell_subschools = []
            for subschool in subschool_meta_info:
                subschool_id = subschool[0]
                db_cursor.execute("SELECT name FROM subschool WHERE id = ?", (subschool_id,))
                spell_subschools.append(db_cursor.fetchone()[0])
            test_master_file.write(" (%s)" % ", ".join(spell_subschools))

        db_cursor.execute("SELECT descriptor_id FROM spell_descriptor WHERE spell_id = ?", (spell_id,))
        descriptor_meta_info = db_cursor.fetchall()
        if descriptor_meta_info:
            spell_descriptors = []
            for descriptor in descriptor_meta_info:
                descriptor_id = descriptor[0]
                db_cursor.execute("SELECT name FROM descriptor WHERE id = ?", (descriptor_id,))
                spell_descriptors.append(db_cursor.fetchone()[0])
            test_master_file.write(" [%s]" % ", ".join(spell_descriptors))
        test_master_file.write("\n")

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
        test_master_file.write("Level: %s\n" % ", ".join(spell_classes))

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
            test_master_file.write("Components: %s\n" % ", ".join(spell_components))


    #####################
    # Spell Description #
    #####################
        db_cursor.execute("SELECT * FROM spell WHERE id = ?", (spell_id,))
        spell_meta_info = db_cursor.fetchone()
        if spell_meta_info[2]:
            test_master_file.write("Casting Time: %s\n" % spell_meta_info[2])
        if spell_meta_info[3]:
            test_master_file.write("Range: %s\n" % spell_meta_info[3])
        if spell_meta_info[4]:
            test_master_file.write("Target: %s\n" % spell_meta_info[4])
        if spell_meta_info[5]:
            test_master_file.write("Effect: %s\n" % spell_meta_info[5])
        if spell_meta_info[6]:
            test_master_file.write("Area: %s\n" % spell_meta_info[6])
        if spell_meta_info[7]:
            test_master_file.write("Duration: %s\n" % spell_meta_info[7])
        if spell_meta_info[8]:
            test_master_file.write("Saving Throw: %s\n" % spell_meta_info[8])
        if spell_meta_info[9]:
            test_master_file.write("Spell Resistance: %s\n" % spell_meta_info[9])
        if spell_meta_info[10]:
            test_master_file.write("    %s\n" % spell_meta_info[10])

        test_master_file.write("\n")

    print "%s COMPLETE%s" % (colorz.PURPLE, colorz.ENDC)

db_conn = sqlite3.connect('spells.db')
db_conn.text_factory = str
db_cursor = db_conn.cursor()

db_cursor.execute("SELECT spell_id, alt_spell_name FROM alt_spell ORDER BY alt_spell_name")
alt_spells = list(db_cursor.fetchall())
alt_spells = sorted(alt_spells, key=spell_name_sort)
db_cursor.execute("SELECT id, name FROM spell ORDER BY name")

test_master_file = open('data/test-all-spells.txt', 'w')

all_spells = list(db_cursor.fetchall())
all_spells = sorted(all_spells, key=spell_name_sort)
test_file_generator(db_cursor, all_spells, alt_spells, test_master_file)
test_master_file.close()

#Check for differences!
mismatch_found = False
test_master_file = list(open('data/test-all-spells.txt', 'r'))
master_file = list(open('data/all-spells.txt', 'r'))
mismatch_file = open('data/mismatch.txt', 'w')
if len(test_master_file) != len(master_file):
    print len(test_master_file)
    print len(master_file)
    mismatch_file.write("Mismatch file length\n")
    mismatch_found = True

if len(test_master_file) < len(master_file):
    file_lines = len(test_master_file)
else:
    file_lines = len(master_file)

for x in range(file_lines):
    if test_master_file[x] != master_file[x]:
        mismatch_file.write("MISMATCH! On line %s\n" % str(x + 1))
        mismatch_found = True
print "Mismatch check COMPLETE!"
if mismatch_found:
    print "Mismatches found. Please check data/mismatch.txt!"
else:
    all_spells = open('data/all-spells.txt', 'w')
    temp_spells = open('data/test-all-spells.txt', 'r')
    for line in temp_spells:
        all_spells.write(line)
    remove('data/test-all-spells.txt')
