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
#import csv

db_conn = sqlite3.connect('spells.db')
db_conn.text_factory = str
db_cursor = db_conn.cursor()

db_cursor.execute("SELECT * FROM spell ORDER BY name")

test_master_file = open('data/test-all-spells.txt', 'w')

for spell in db_cursor.fetchall():
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
            book[1] = "(pg " + book[1] + ")"
        else:
            book[1] = ''
        book = " ".join(book).strip()
        spell_books.append(book)
    test_master_file.write("    " + spell[1] + " [" + ", ".join(spell_books) + "]\n")

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
        test_master_file.write(" (" + ", ".join(spell_subschools) + ")")

    db_cursor.execute("SELECT descriptor_id FROM spell_descriptor WHERE spell_id = ?", (spell_id,))
    descriptor_meta_info = db_cursor.fetchall()
    if descriptor_meta_info:
        spell_descriptors = []
        for descriptor in descriptor_meta_info:
            descriptor_id = descriptor[0]
            db_cursor.execute("SELECT name FROM descriptor WHERE id = ?", (descriptor_id,))
            spell_descriptors.append(db_cursor.fetchone()[0])
        test_master_file.write(" [" + ", ".join(spell_descriptors) + "]")
    test_master_file.write("\n")

    test_master_file.write("\n")

"""
        db_cursor.execute("CREATE TABLE spell\
            (id INTEGER PRIMARY KEY, name TINYTEXT,\
            cast_time TINYTEXT, range TINYTEXT,\
            target TINYTEXT, effect TINYTEXT, area TINYTEXT, duration TINYTEXT,\
            saving_throw TINYTEXT, description TINYTEXT, components TINYTEXT)")
"""
