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
  "Mountain Hammer",
]
maneuver_descriptions = {
  "Foehammer" : 
  """Initiation Action: 1 standard action
Range: Melee attack
Target: One creature
Your throw yourself behind your attack, lending your blow such great weight and force that you
leave injuries that even magical defenses cannot mend.
Your devotion to your cause gives you boundless energy that allows you to smash through
supernatural defenses. When you land an attack, you hit with such force that damage reduction
offers little resistance against you.
When you use this maneuver, you make a melee attack against a single foe. This attack
automatically overcomes the opponent’s damage reduction and deals an extra 2d6 points of damage.
""",
  "Crusader's Strike" : 
  """Initiation Action: 1 standard action Range: Melee attack
Target: One creature
Divine energy surrounds your weapon as you strike. This power washes over you as your weapon finds
its mark, mending your wounds and giving you the strength to fight on.
As part of initiating this strike, you must make a successful melee attack against an enemy whose
alignment has at least one component different from yours. This foe must pose a threat to you or
your allies in some direct, immediate way. If your attack hits, you or an ally within 10 feet of
you heals 1d6 points of damage + 1 point per initiator level (maximum +5).""",
  "Shield Block" : 
  """Initiation Action: 1 immediate action
Range: Personal
Target: You
Duration: Instantaneous
With a heroic burst of effort, you thrust your shield between your defenseless ally and your enemy.
As an immediate action, you can grant an AC bonus to an adjacent ally equal to your shield’s AC
bonus + 4. You apply this bonus in response to a single melee or ranged attack that targets your
ally. You can initiate this maneuver after an opponent makes his attack roll, but you must do so
before you know whether the attack was a success or a failure.""",
  "Battle Leader's Charge" : 
  """Initiation Action: 1 full-round action
Range: Melee attack
Target: One creature
You lead from the front, charging your enemies so that your allies can follow in your wake.
The White Raven discipline teaches that he who seizes the initiative also seizes victory. You have
learned to lead an attack with a mighty charge, the better to disrupt the enemy and inspire your
allies in battle.
As part of this maneuver, you charge an opponent. You do not provoke attacks of opportunity for
moving as part of this charge. If your charge attack hits, it deals an extra 10 points of damage.""",
  "Mountain Hammer" : 
  """Initiation Action: 1 standard action
Range: Melee attack
Target: One creature or unattended object
Like a falling avalanche, you strike with the weight and fury of the mountain.
As part of this maneuver, you make a single melee attack. This attack deals an extra 2d6 points of
damage and auto- matically overcomes damage reduction and hardness.""",
}
immediate_maneuvers = [
  "Shield Block",
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
  print "%sAvailable maneuvers:" % colorz.BLUE
  for maneuver in readied_maneuvers:
    if maneuver not in expended_maneuvers:
      print "%s: %s" % (maneuver + 1, maneuvers[maneuver])

  used_maneuver = raw_input("Manuever used? ")

  if used_maneuver == '0' or not used_maneuver:
    continue

  if used_maneuver.lower() == 'exit':
    print "%sThank you for playing!%s" % (colorz.RED, colorz.ENDC)
    break

  if used_maneuver.lower() == 'undo':
    print "%sUndoing previous maneuver...%s" % (colorz.BLUE, colorz.ENDC)
    if expended_maneuvers:
      expended_maneuvers.pop()
    else:
      print "%sYou haven't expended any maneuvers!" % colorz.RED
    retry_input_flag = True
    continue

  if used_maneuver.lower() == 'reset':
    del readied_maneuvers[:]
    del expended_maneuvers[:]
    print "%sResetting..." % (colorz.BLUE)

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
  print "%sUsed maneuver:\n%s%s\n%s" % \
    (colorz.BLUE, colorz.ENDC, maneuvers[used_maneuver], maneuver_descriptions[maneuvers[used_maneuver]])

  if maneuvers[used_maneuver] in immediate_maneuvers:
    retry_input_flag = True
    continue


