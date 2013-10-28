#!/usr/bin/env python
# -*- coding: utf8 -*

from random import randint
import re


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


maneuvers = [
  "Foehammer",
  "Crusader's Strike",
  "Shield Block",
  "Battle Leader's Charge",
  "Mountain Hammer"
]
maneuvers_at_start = 3
readied_maneuvers = []
expended_maneuvers = []
retry_input_flag = False

print "%sWhen prompted, please enter maneuver number used." % colorz.RED
print "Enter 0 or nothing if none are used. Enter 'exit' if finished."
print "Enter reset to reset everything."

while True:

  if not retry_input_flag:
    # If all maneuvers are up, please reset all
    if len(readied_maneuvers) == len(maneuvers):
      del readied_maneuvers[:]
      del expended_maneuvers[:]

    # At beginning of combat or reset, ready two additional maneuvers
    # Otherwise, only ready one
    if not readied_maneuvers:
      maneuvers_to_ready = maneuvers_at_start
    else:
      maneuvers_to_ready = 1

    for x in range(0, maneuvers_to_ready):
      while True:
        maneuver = randint(0, len(maneuvers) - 1)
        if maneuver not in readied_maneuvers:
          readied_maneuvers.append(maneuver)
          break

    readied_maneuvers = sorted(readied_maneuvers)

  retry_input_flag = False

  # Now list current maneuvers
  print "%sAvailable maneuvers:" % colorz.YELLOW
  for maneuver in readied_maneuvers:
    if maneuver not in expended_maneuvers:
      print "%s: %s" % (maneuver + 1, maneuvers[maneuver])

  used_maneuver = raw_input("Manuever used? ")

  if used_maneuver == '0' or not used_maneuver:
    continue

  if used_maneuver.lower() == 'exit':
    print "%sThank you for playing!%s" % (colorz.PURPLE, colorz.ENDC)
    break

  if used_maneuver.lower() == 'reset':
    del readied_maneuvers[:]
    del expended_maneuvers[:]
    print "%sResetting..." % (colorz.PURPLE)

  if not re.match('\d+', used_maneuver):
    print "%sOkay smart ass. That's not a valid input, please retry" % colorz.RED
    retry_input_flag = True
    continue

  used_maneuver = int(used_maneuver) - 1

  if len(maneuvers) < used_maneuver:
    print "%sThat's not a valid number, please retry" % colorz.RED
    retry_input_flag = True
    continue

  if used_maneuver not in readied_maneuvers:
    print "%sThat maneuver is not readied, please retry" % colorz.RED
    retry_input_flag = True
    continue

  if used_maneuver in expended_maneuvers:
    print "%sThat manuver has been expended, please retry" % colorz.RED
    retry_input_flag = True
    continue

  expended_maneuvers.append(used_maneuver)
  sorted(expended_maneuvers)
