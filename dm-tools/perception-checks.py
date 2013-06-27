#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
    Rolls auto-search, Listen, and Spot for players
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

import pygame
import argparse
import dice_rolling


class colorz:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


def rolling_sound():
    pygame.mixer.init()
    dice_roll_sound = pygame.mixer.Sound('assets/dice_roll.wav')
    sound_channel = dice_roll_sound.play()
    while sound_channel.get_busy():
        pygame.time.delay(10)

characters = {
    'Warthic': {
        'Listen': 0,
        'Spot': 0,
        'Search': 9
    },
    'Grok': {
        'Listen': 1,
        'Spot': 1,
    },
    'Moonflower': {
        'Listen': 10,
        'Spot': 10,
        'Search': 10
    }
}
options = {
    'AutoRoll': True
}

parser = argparse.ArgumentParser()
parser.add_argument('-n', action='store_true', default=False, dest='ninja_mode',
                    help='Silent roll/ninja mode?')
parser.add_argument('-A', action='store_true', default=False, dest='no_auto_roll',
                    help='Deactivates auto roll')

args = parser.parse_args()
if args.no_auto_roll:
    options['AutoRoll'] = False

for char in characters:
    print "\t%s%s: " % (colorz.BLUE, char)
    for skill in characters[char]:
        dice_rolling.general_dc_roll(options, skill.ljust(6), characters[char][skill])
    print ""

if not args.ninja_mode:
    rolling_sound()
