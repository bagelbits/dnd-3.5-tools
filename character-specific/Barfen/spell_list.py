#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
    Shadow Mage Spell List generator
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


def spell_list_generator(db_cursor, all_spells, bar_fen_list):
    line_count = 0
    for spell_id in all_spells:
        line_count += 1
        per = line_count / float(len(all_spells)) * 100
        stdout.write("\rGenerating: %d%%" % per)
        stdout.flush()

    #################
    # Name and Book #
    #################
        db_cursor.execute("SELECT name FROM spell WHERE id = ?", (spell_id,))
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
                book[1] = "(pg " + book[1] + ")"
            else:
                book[1] = ''
            book = " ".join(book).strip()
            spell_books.append(book)
        bar_fen_list.write("    " + spell_name + " [" + ", ".join(spell_books) + "]\n")

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
        bar_fen_list.write("/".join(spell_schools))

        db_cursor.execute("SELECT subschool_id FROM spell_subschool WHERE spell_id = ?", (spell_id,))
        subschool_meta_info = db_cursor.fetchall()
        if subschool_meta_info:
            spell_subschools = []
            for subschool in subschool_meta_info:
                subschool_id = subschool[0]
                db_cursor.execute("SELECT name FROM subschool WHERE id = ?", (subschool_id,))
                spell_subschools.append(db_cursor.fetchone()[0])
            bar_fen_list.write(" (" + ", ".join(spell_subschools) + ")")

        db_cursor.execute("SELECT descriptor_id FROM spell_descriptor WHERE spell_id = ?", (spell_id,))
        descriptor_meta_info = db_cursor.fetchall()
        if descriptor_meta_info:
            spell_descriptors = []
            for descriptor in descriptor_meta_info:
                descriptor_id = descriptor[0]
                db_cursor.execute("SELECT name FROM descriptor WHERE id = ?", (descriptor_id,))
                spell_descriptors.append(db_cursor.fetchone()[0])
            bar_fen_list.write(" [" + ", ".join(spell_descriptors) + "]")
        bar_fen_list.write("\n")

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
        db_cursor.execute("SELECT domain_id, level FROM spell_domain_feat WHERE spell_id = ?", (spell_id,))
        class_meta_info = db_cursor.fetchall()
        for character_class in class_meta_info:
            class_id = character_class[0]
            db_cursor.execute("SELECT name FROM domain_feat WHERE id = ?", (class_id,))
            spell_classes.append(" ".join([db_cursor.fetchone()[0], str(character_class[1])]))
        spell_classes = sorted(spell_classes)
        bar_fen_list.write("Level: " + ", ".join(spell_classes) + "\n")

    #####################
    # Spell Description #
    #####################
        db_cursor.execute("SELECT * FROM spell WHERE id = ?", (spell_id,))
        spell_meta_info = db_cursor.fetchone()
        if spell_meta_info[11]:
            bar_fen_list.write("Components: " + spell_meta_info[11] + "\n")
        if spell_meta_info[2]:
            bar_fen_list.write("Casting Time: " + spell_meta_info[2] + "\n")
        if spell_meta_info[3]:
            bar_fen_list.write("Range: " + spell_meta_info[3] + "\n")
        if spell_meta_info[4]:
            bar_fen_list.write("Target: " + spell_meta_info[4] + "\n")
        if spell_meta_info[5]:
            bar_fen_list.write("Effect: " + spell_meta_info[5] + "\n")
        if spell_meta_info[6]:
            bar_fen_list.write("Area: " + spell_meta_info[6] + "\n")
        if spell_meta_info[7]:
            bar_fen_list.write("Duration: " + spell_meta_info[7] + "\n")
        if spell_meta_info[8]:
            bar_fen_list.write("Saving Throw: " + spell_meta_info[8] + "\n")
        if spell_meta_info[9]:
            bar_fen_list.write("Spell Resistance: " + spell_meta_info[9] + "\n")
        if spell_meta_info[10]:
            bar_fen_list.write("    " + spell_meta_info[10] + "\n")

        bar_fen_list.write("\n")

    print " COMPLETE!"


def reformat_return(answer):
    for x in range(len(answer)):
        answer[x] = answer[x][0]
    return answer

spells_to_check = []
spell_level = 6

db_conn = sqlite3.connect('../../general/spells.db')
db_conn.text_factory = str
db_cursor = db_conn.cursor()

# Let's grab all relevent ids
db_cursor.execute("SELECT id FROM school WHERE name = 'Evocation'")
evoc_id = db_cursor.fetchone()[0]
db_cursor.execute("SELECT id FROM school WHERE name = 'Conjuration'")
conj_id = db_cursor.fetchone()[0]
db_cursor.execute("SELECT id FROM subschool WHERE name = 'Creation'")
creat_id = db_cursor.fetchone()[0]
db_cursor.execute("SELECT id FROM subschool WHERE name = 'Summoning'")
summon_id = db_cursor.fetchone()[0]
db_cursor.execute("SELECT id FROM class WHERE name = 'Wizard'")
wiz_id = db_cursor.fetchone()[0]
db_cursor.execute("SELECT id FROM class WHERE name = 'Sorcerer'")
sorc_id = db_cursor.fetchone()[0]


db_cursor.execute("SELECT spell_id FROM spell_school WHERE school_id = ?", (evoc_id,))
spells_to_check.extend(reformat_return(db_cursor.fetchall()))
db_cursor.execute("SELECT spell_id FROM spell_school\
                   WHERE school_id = ?", (conj_id,))
conj_spells = reformat_return(db_cursor.fetchall())
line_count = 0
for x in range(len(conj_spells)):
    line_count += 1
    per = line_count / float(len(conj_spells)) * 100
    stdout.write("\rChecking conjuration: %d%%" % per)
    stdout.flush()
    creat_or_summon = False
    db_cursor.execute("SELECT id FROM spell_subschool\
                       WHERE subschool_id = ? AND spell_id = ?",
                      (creat_id, conj_spells[x]))
    if db_cursor.fetchone():
        creat_or_summon = True
    db_cursor.execute("SELECT id FROM spell_subschool\
                       WHERE subschool_id = ? AND spell_id = ?",
                      (summon_id, conj_spells[x]))
    if db_cursor.fetchone():
        creat_or_summon = True
    if not creat_or_summon:
        conj_spells[x] = ''
print " COMPLETE!"
spells_to_check.extend(filter(None, conj_spells))
spells_to_check = sorted(list(set(spells_to_check)))

#Now to see which are Wizard or Sorcerer spells
line_count = 0
for x in range(len(spells_to_check)):
    line_count += 1
    per = line_count / float(len(spells_to_check)) * 100
    stdout.write("\rChecking classes: %d%%" % per)
    stdout.flush()
    wiz_or_sorc = False
    db_cursor.execute("SELECT id FROM spell_class\
                       WHERE class_id = ? AND spell_id = ? AND level <= ?",
                      (wiz_id, spells_to_check[x], spell_level))
    if db_cursor.fetchone():
        wiz_or_sorc = True
    db_cursor.execute("SELECT id FROM spell_class\
                       WHERE class_id = ? AND spell_id = ? AND level <= ?",
                      (sorc_id, spells_to_check[x], spell_level))
    if db_cursor.fetchone():
        wiz_or_sorc = True
    if not wiz_or_sorc:
        spells_to_check[x] = ''
print " COMPLETE!"
spells_to_check = filter(None, spells_to_check)
print spells_to_check

bar_fen_list = open('Bar-fen-spell-list.txt', 'w')
spell_list_generator(db_cursor, spells_to_check, bar_fen_list)