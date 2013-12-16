#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
  Hacked together random CR encounter generator.
  No GUI planned.

  Written by Christopher Durien Ward
  With help from Noah Reson-Brown

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

from sys import stdout
import sqlite3
import csv
import traceback


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

def table_setup(name, db_cursor):
  if(name == 'creature'):
    db_cursor.execute("CREATE TABLE creature\
      (id INTEGER PRIMARY KEY, name TINYTEXT, cr TINYTEXT)")

  elif(name == 'book'):
    db_cursor.execute("CREATE TABLE book\
      (id INTEGER PRIMARY KEY, name TINYTEXT,\
        short_hand TINYTEXT)")

  elif(name == 'creature_book'):
    db_cursor.execute("CREATE TABLE creature_book\
      (creature_id INTEGER, book_id INTEGER, page INTEGER,\
        FOREIGN KEY (creature_id) REFERENCES creature(id),\
        FOREIGN KEY (book_id) REFERENCES book(id))")

  elif(name == 'type'):
    db_cursor.execute("CREATE TABLE type\
      (id INTEGER PRIMARY KEY, name TINYTEXT)")

  elif(name == 'creature_type'):
    db_cursor.execute("CREATE TABLE creature_type\
      (creature_id INTEGER, type_id INTEGER,\
        FOREIGN KEY (creature_id) REFERENCES creature(id),\
        FOREIGN KEY (type_id) REFERENCES type(id))")

  elif(name == 'subtype'):
    db_cursor.execute("CREATE TABLE subtype\
      (id INTEGER PRIMARY KEY, name TINYTEXT)")

  elif(name == 'creature_subtype'):
    db_cursor.execute("CREATE TABLE creature_subtype\
      (creature_id INTEGER, subtype_id INTEGER,\
        FOREIGN KEY (creature_id) REFERENCES creature(id),\
        FOREIGN KEY (subtype_id) REFERENCES subtype(id))")

  elif(name == 'alignment'):
    db_cursor.execute("CREATE TABLE alignment\
      (subtype_id INTEGER, opposing_id INTEGER,\
        FOREIGN KEY (subtype_id) REFERENCES subtype(id),\
        FOREIGN KEY (opposing_id) REFERENCES subtype(id))")

  elif(name == 'element'):
    db_cursor.execute("CREATE TABLE element\
      (subtype_id INTEGER,\
        FOREIGN KEY (subtype_id) REFERENCES subtype(id))")

def insert_creature(db_cursor, line):

  db_cursor.execute('SELECT id FROM creature WHERE name = ? LIMIT 1', (line[0],))
  if db_cursor.fetchone():
    db_cursor.execute('SELECT id FROM creature WHERE name = ? AND cr = ? LIMIT 1',
      (line[0],line[4]))
    if db_cursor.fetchone():
      return
    else:
      #TODO: Print these after progress tracker
      print "Potentially conflicting creatures: %s" % line[0]

  # Load in creature
  db_cursor.execute('INSERT INTO creature VALUES(NULL, ?, ?)', (line[0], line[4]))

  db_cursor.execute('SELECT id FROM creature WHERE name = ? AND cr = ? LIMIT 1',
    (line[0],line[4]))
  creature_id = db_cursor.fetchone()[0]

  # Link Books
  db_cursor.execute('SELECT id FROM book WHERE short_hand = ? LIMIT 1', (line[1],))
  book_id = db_cursor.fetchone()[0]

  db_cursor.execute('INSERT INTO creature_book VALUES(?, ?, ?)',
    (creature_id, book_id, line[2]))

  # Load main type
  main_type = line[3].split(' (')[0]

  db_cursor.execute('SELECT id FROM type WHERE name = ? LIMIT 1', (main_type,))
  if not db_cursor.fetchone():
    #print "%s" % (main_type,)
    db_cursor.execute('INSERT INTO type VALUES(NULL, ?)', (main_type,))
  db_cursor.execute('SELECT id FROM type WHERE name = ? LIMIT 1', (main_type,))
  maint_type_id = db_cursor.fetchone()[0]

  db_cursor.execute('INSERT INTO creature_type VALUES(?, ?)', (creature_id, maint_type_id))

  # Load secondary types
  subtypes = line[3].split(' (')
  if len(subtypes) > 1:
    subtypes = subtypes[1]
    subtypes = subtypes.replace(')', '')
    subtypes = subtypes.split(', ')

    for subtype in subtypes:
      db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (subtype,))
      if not db_cursor.fetchone():
        #print "%s" % (subtype)
        db_cursor.execute('INSERT INTO subtype VALUES (NULL, ?)', (subtype,))
      db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (subtype,))
      subtype_id = db_cursor.fetchone()[0]

      db_cursor.execute('INSERT INTO creature_subtype VALUES(?, ?)',
        (creature_id, subtype_id))

def preload_tables(db_cursor):
  alignments = [
    ['Evil', 'Good'],
    ['Lawful', 'Chaotic'],
    'Neutral',
  ]

  elements = [
    'Air',
    'Fire',
    'Cold',
    'Earth',
    'Water',
    'Electricity',
    'Shadow',
  ]

  for element in elements:
    db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (element,))
    if not db_cursor.fetchone():
      db_cursor.execute('INSERT INTO subtype VALUES(NULL, ?)', (element,))
      db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (element,))

      subtype_id = db_cursor.fetchone()[0]
      db_cursor.execute('INSERT INTO element VALUES(?)', (subtype_id,))

  for alignment in alignments:
    if isinstance(alignment, list):
      db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (alignment[0],))
      if not db_cursor.fetchone():
        db_cursor.execute('INSERT INTO subtype VALUES(NULL, ?)', (alignment[0],))
        db_cursor.execute('INSERT INTO subtype VALUES(NULL, ?)', (alignment[1],))

        subtype_ids = []
        db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (alignment[0],))
        subtype_ids.append(db_cursor.fetchone()[0])
        db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (alignment[1],))
        subtype_ids.append(db_cursor.fetchone()[0])

        db_cursor.execute('INSERT INTO alignment VALUES(?, ?)', (subtype_ids[0], subtype_ids[1]))
        db_cursor.execute('INSERT INTO alignment VALUES(?, ?)', (subtype_ids[1], subtype_ids[0]))


    else:
      db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (alignment,))
      if not db_cursor.fetchone():
        db_cursor.execute('INSERT INTO subtype VALUES(NULL, ?)', (alignment,))
        db_cursor.execute('SELECT id FROM subtype WHERE name = ? LIMIT 1', (alignment,))

        subtype_id = db_cursor.fetchone()[0]
        db_cursor.execute('INSERT INTO alignment VALUES(?, 0)', (subtype_id,))


def db_setup():
  tables = ['size', 'creature', 'book', 'creature_book', 'type']
  tables.extend(['creature_type', 'subtype', 'creature_subtype'])
  tables.extend(['alignment', 'element'])

  db_conn = sqlite3.connect('assets/creatures.db')
  db_conn.text_factory = str
  db_cursor = db_conn.cursor()

  db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
  table_results = db_cursor.fetchall()
  stdout.write("%sSetting up tables..." % colorz.BLUE)
  for table in tables:
    if not any(table == result[0] for result in table_results):
      try:
        table_setup(table, db_cursor)
        db_conn.commit()
      except Exception:
        traceback.print_exc()
        db_cursor.close()
        db_conn.close()
        exit(1)
  print " COMPLETE!%s" % colorz.ENDC

  stdout.write("%sPopulating tables..." % colorz.BLUE)
  preload_tables(db_cursor)
  print " COMPLETE!%s" % colorz.ENDC

  book_list = csv.reader(open('assets/books.csv', 'rb'),
    delimiter=',', quotechar='"')
  stdout.write("%sLoading books..." % colorz.BLUE)
  for line in book_list:
    db_cursor.execute("SELECT id FROM book WHERE short_hand = ? LIMIT 1", (line[0],))
    if not db_cursor.fetchone():
      db_cursor.execute("INSERT INTO book VALUES(NULL, ?, ?)", (line[1], line[0]))
  db_conn.commit()
  print " COMPLETE!%s" % colorz.ENDC

  monster_list = csv.reader(open('assets/monsters_by_cr.csv', 'rb'),
    delimiter=',', quotechar='"')
  monster_list = list(monster_list)
  monster_list_length = len(monster_list)
  line_count = 0
  for line in monster_list:
    line_count += 1
    per = line_count / float(monster_list_length) * 100
    stdout.write('\r%sLoading monsters... %d%%' % (colorz.BLUE, per))
    stdout.flush()
    insert_creature(db_cursor, line)
    db_conn.commit()

  print " COMPLETE!%s" % colorz.ENDC

  return db_conn, db_cursor
