#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
    Confusion roller
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

from random import randint

#For making text all colorful and easier to read.
class colorz:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def roll_dice(dice=1, sides=6):
    try:
        return [randint(1, sides) for x in range(dice)]
    except:
        return []

confusion_roll = sum(roll_dice(1, 100))
print "%sRolled %s on d100%s" % (colorz.PURPLE, confusion_roll, colorz.YELLOW)
if confusion_roll in range(11, 21):
  print "Act normally%s" % colorz.ENDC
elif confusion_roll in range(71, 101):
  print "Attack nearest creature%s" % colorz.ENDC
else:
  print "Do nothing but babble incoherently.%s" % colorz.ENDC
