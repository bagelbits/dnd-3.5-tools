#!/usr/bin/env python
# -*- coding: utf8 -*-

from sys import stdout
from os import remove
import re

def stitch_together_parens(level_lines):
    paran_sections = []
    for pos in range(len(level_lines)):
        if "(" in level_lines[pos] and ")" not in level_lines[pos]:
            paran_sections.append([pos])
        if "(" not in level_lines[pos] and ")" in level_lines[pos]:
            paran_sections[-1].append(pos)
    for section in reversed(paran_sections):
        level_lines[section[0]:section[1]+1] = [', '.join(level_lines[section[0]:section[1]+1])]
    return level_lines

all_spells = open('data/all-spells.txt', 'r')
temp_spells = open('data/temp-spells.txt', 'w')

all_spells = list(all_spells)
line_count = 0
for line in all_spells:
    line_count += 1
    per = line_count / float(len(all_spells)) * 100
    stdout.write("\rLoading: %d%%" % per)
    stdout.flush()

    if line.startswith("Level: "):
        line = line.strip()
        character_class = re.sub('Level: ', '', line, count=1)
        character_class = sorted(stitch_together_parens(character_class.split(", ")))
        temp_spells.write("Level: %s\n" % ", ".join(character_class))
    else:
        temp_spells.write(line)

all_spells = open('data/all-spells.txt', 'w')
temp_spells = open('data/temp-spells.txt', 'r')
for line in temp_spells:
    all_spells.write(line)
remove('data/temp-spells.txt')
print " Complete!"
