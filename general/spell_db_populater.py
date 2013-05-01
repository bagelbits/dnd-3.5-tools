#!/usr/bin/env python
# -*- coding: utf8 -*-
import sqlite3
import traceback
from sys import exit


def table_setup(name, db_cursor):
    if(name == 'spell'):
        db_cursor.execute("""CREATE TABLE spell
            (id INTEGER PRIMARY KEY, name TINYTEXT,
            book_id INT, cast_time TINYTEXT, range TINYTEXT,
            target TINYTEXT, duration TINYTEXT, saving_throw TINYTEXT,
            description TINYTEXT, verbal_component INT,
            somatic_component INT, material_component INT,
            focus_component INT, divine_focus_component INT,
            xp_component INT)""")

    elif(name == 'class'):
        db_cursor.execute("CREATE TABLE class (\
            id INTEGER PRIMARY KEY, name TINYTEXT, \
            probability INT, divine INT, arcane INT)")

    elif(name == 'class_spell'):
        db_cursor.execute("CREATE TABLE class_spell (\
            id INTEGER PRIMARY KEY, class_id INT, \
            spell_id INT, level INT)")

    elif(name == 'domain'):
        db_cursor.execute("CREATE TABLE domain (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'domain_spell'):
        db_cursor.execute("CREATE TABLE domain_spell (\
            id INTEGER PRIMARY KEY, domain_id INT, \
            spell_id INTEGER, level INT)")

    elif(name == 'book'):
        db_cursor.execute("CREATE TABLE book (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'type'):
        db_cursor.execute("CREATE TABLE type (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'spell_type'):
        db_cursor.execute("CREATE TABLE spell_type (\
            id INTEGER PRIMARY KEY, type_id INT, \
            spell_id INT)")

    elif(name == 'subtype'):
        db_cursor.execute("CREATE TABLE subtype (\
            id INTEGER PRIMARY KEY, name TINYTEXT)")

    elif(name == 'spell_subtype'):
        db_cursor.execute("CREATE TABLE spell_subtype (\
            id INTEGER PRIMARY KEY, subtype_id INT, \
            spell_id INT)")


tables = ['spell', 'class_spell', 'class', 'domain_spell', 'domain']
tables.extend(['book', 'type', 'spell_type', 'subtype', 'spell_subtype'])

db_conn = sqlite3.connect('spells.db')
db_conn.text_factory = str
db_cursor = db_conn.cursor()

db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_results = db_cursor.fetchall()
print table_results
for table in tables:
    if not any(table == result[0] for result in table_results):
        try:
            table_setup(table, db_cursor)
            db_conn.commit()
        except Exception, e:
            traceback.print_exc()
            db_cursor.close()
            db_conn.close()
            exit(1)

"""
Ignore spells like:
          Horizikaul's Boom
See "Sonic Blast"

          Horizikaul's Cough
See "Sonic Snap"

          Horizikaul's Versatile Vibration
See "Sonic Rumble"

.... Actually, create a separate table for spells that are the same and have
them referenceto general spell
"""

"""
Add Divine Bard as a separate class and to any
spell that has Bard as a class
"""

"""
Populate Classes, Book, Type, and Subtype tables as you run trough the txt file
Domain should be generated off the other pdf that Noah gave me.
"""
