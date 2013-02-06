#!/usr/bin/env python -3
# -*- coding: utf8 -*- 

from random import randint

#For making text all colorful and easier to read.
class colorz:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

########################################################
#                   DICE ROLLERS                       #
# Subroutines for General DC, Attack, and Damage rolls #
########################################################

def roll_dice(dice=1, sides=6):
    try: return [randint(1, sides) for x in range(dice)]
    except: return []

#TODO Give rollers a dice list of [num_of_dice, num_of_sides]
####################
# GENEREAL DC ROLL #
####################

def general_dc_roll(dc_name, num_of_dice=1, num_of_sides=20, total_mod=0):
    global auto_roll

    total_dc_roll = 0

    print "\n%s%s roll: %dd%d + %d" \
        % (colorz.PURPLE, dc_name, num_of_dice, num_of_sides, total_mod)
    
    if auto_roll:
        base_dc_roll = sum(roll_dice(num_of_dice, num_of_sides))
    else:
        print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
        base_dc_roll = raw_input('What did you roll? ')
        base_dc_roll = base_dc_roll.split(",")
        base_dc_roll = sum(int(x) for x in base_dc_roll)

    print "\n%sBase roll: %d\n" % (colorz.PURPLE, base_dc_roll)

    #EXPLODING DICE
    while base_dc_roll == 20:
        total_mod += base_dc_roll
        print "%s\nExploding dice! Roll again%s" % (colorz.RED, colorz.PURPLE)
        print "%s roll: %dd%d + %d" \
            % (dc_name, num_of_dice, num_of_sides, total_mod)
        
        if auto_roll:
            base_dc_roll = sum(roll_dice(num_of_dice, num_of_sides))
        else:
            print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
            base_dc_roll = raw_input('What did you roll? ')
            base_dc_roll = base_dc_roll.split(",")
            base_dc_roll = sum(int(x) for x in base_dc_roll)

        print "\n%sBase roll: %d\n" % (colorz.PURPLE, base_dc_roll)

    if base_dc_roll == 1:
        print "%s\nCritical Failure!%s" % (colorz.RED, colorz.PURPLE)

    total_dc_roll += total_mod + base_dc_roll
    print "Total %s roll result: %d%s\n" \
        % (dc_name, total_dc_roll, colorz.GREEN)
    return total_dc_roll
    

###############
# ATTACK ROLL #
###############

def attack_roll(total_attack_bonus=0, range_penalty=0):
    global auto_roll

    multiplier = 1
    print "\n%sAttack roll: 1d20 + %d - %d" \
        % (colorz.BLUE, total_attack_bonus, range_penalty)
    
    if auto_roll:
        base_attack_roll = sum(roll_dice(1, 20))
    else:
        print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
        base_attack_roll = int(raw_input('What did you roll? '))

    print "\n%sBase roll: %d\n" % (colorz.BLUE, base_attack_roll)

    while base_attack_roll == 20:
        multiplier += 1
        print "%s\nGotta crit! Roll to confirm!%s" % (colorz.RED, colorz.BLUE)
        print "\nAttack roll: 1d20 + %d - %d" \
            % (total_attack_bonus, range_penalty)
        
        if auto_roll:
            base_attack_roll = sum(roll_dice(1, 20))
        else:
            print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
            base_attack_roll = int(raw_input('What did you roll? '))

        print "\n%sBase roll: %d\n" % (colorz.BLUE, base_attack_roll)

    if base_attack_roll == 1:
        print "%sCritical Failure!%s" % (colorz.RED, colorz.BLUE)
        
    #Addin in mods
    roll_mod = total_attack_bonus
    roll_mod -= range_penalty
    total_attack = base_attack_roll + roll_mod

    print "Total Attack roll result: %d" % total_attack
    if multiplier > 1:
        print "Total multiplier: %dx" % multiplier

    print colorz.GREEN
    return total_attack, multiplier


###############
# DAMAGE ROLL #
###############

def damage_roll(num_of_dice=1, num_of_sides=6, total_mod=0, multiplier=1, damage_doubling=1):
    global auto_roll
    num_of_dice *= damage_doubling
    total_mod *= damage_doubling
    print colorz.RED

    if multiplier > 1:
        print "Damage roll: %dd%d + %d X%d" \
            % (num_of_dice, num_of_sides, total_mod, multiplier)
    else:
        print "Damage roll: %dd%d + %d" % (num_of_dice, num_of_sides, total_mod)

    if auto_roll:
        total_damage = sum(roll_dice(num_of_dice, num_of_sides))
    else:
        print "%sRoll now. (Don't add in any mods)" % colorz.GREEN
        total_damage = raw_input('What did you roll? ')
        total_damage = total_damage.split(",")
        total_damage = sum(int(x.strip()) for x in total_damage)

    print "%sBase roll: %d\n" % (colorz.RED, total_damage)

    #Last minute mods
    total_damage += total_mod
    total_damage *= multiplier

    #TOTAL
    print "Damage roll result: %d%s\n" % (total_damage, colorz.GREEN)
    return total_damage

######################################################
#              WEAPON ATTACK METHODS                 #
# Fully automized methods for each of Krag's attacks #
######################################################

#TODO Package up multipliers and mods where you can.

#################
# SHIELD ATTACK #
#################

def shield_attack(item_mod=0, charging=False, power_attack=0, cleave=False):
    global STR_mod
    global base_attack_bonus
    global attack_based_size_mod
    global auto_roll
    global morale_attack_bonus
    global morale_damage_bonus

    cleave_targets = {}
    targets = {}
    dice_to_roll = 2
    damage_doubling = 1

    print '\nMighty swing used. Please pick 3 adjacent squares.'
    raw_input('(Press enter to continue)')

    ####Attack roll####
    shield_attack_bonus = base_attack_bonus + STR_mod + attack_based_size_mod 
    shield_attack_bonus += item_mod
    shield_attack_bonus -= power_attack #Power attack penalty
    shield_attack_bonus += morale_attack_bonus
    if charging:
        shield_attack_bonus += 2

    total_attack_roll, multiplier = attack_roll(shield_attack_bonus)
    hits = int(raw_input('How many things were hit? '))
    if hits == 0:
        if cleave:
            return cleave_targets
        return targets, cleave_targets
    
    
    #Damage roll with mighty swing, shield charge, 
    #shield slam, knockback... yay for fun times
    damage_mod = STR_mod*1.5 + power_attack*2 + item_mod 
    damage_mod += morale_damage_bonus

    if charging:
        damage_doubling += 1

    for target in range(1, hits + 1):
        target_name = 'Target %d' % target
        print "\n####%s####" % target_name
        total_damage = damage_roll(2, 6, damage_mod, multiplier, damage_doubling)

        if charging:
            #Free Trip attempt
            print "\n%s++Free Trip attempt++" % colorz.YELLOW
            total_damage += trip_attempt(target_name, shield_attack_bonus, damage_mod, damage_doubling)
            
        #Shield daze
        shield_daze(target_name)
        
        #Knockback with bull rush check
        if power_attack:
            total_damage += knockback()


        targets[target_name] = total_damage

    
    if cleave:
        return targets

    print colorz.RED
    for target in targets.keys():
        print "Total damage for %s: %d" % (target, targets[target])
    
    print colorz.YELLOW
    cleave = raw_input("\n\nDid it cleave? (y|n) ")
    if cleave.lower().startswith('y'):
        print  "%sCleaving....\n%s" % (colorz.PURPLE, colorz.GREEN)
        cleave_targets = shield_attack(item_mod, charging, power_attack, True)
        
    return targets, cleave_targets

def shield_daze(target_name):
    global hd_level
    global STR_mod

    print "\n%s++Shield daze++" % colorz.PURPLE
    fort_save = 10 + hd_level//2 + STR_mod
    print "%s must make Fort save and beat %d or be Dazed for one round" \
        % (target_name, fort_save)
    raw_input("Press Enter to continue..." + colorz.GREEN)

def trip_attempt(target_name, attack_bonus, damage_bonus, damage_doubling=1):
    global STR_mod
    global base_attack_bonus
    global STR_check_size_mod

    can_trip = raw_input('Enemy bigger than huge? (y|n) ')
    if can_trip.lower().startswith('n'):
        touch_attack_roll = general_dc_roll("Touch attack", 1, 20, STR_mod + base_attack_bonus)
        print colorz.YELLOW
        touch_success = raw_input('Did touch attack succeeed? (y|n) ')

        if touch_success.lower().startswith('y'):
            #+4 for Improved Trip
            trip_str_mod = STR_mod + STR_check_size_mod + 4
            trip_str_check = general_dc_roll("Strength check", 1, 20, trip_str_mod)
            print "\nStrength check to beat: %d" % trip_str_check
            tripped = raw_input('Did you trip it? (y|n) ')

            if tripped.lower().startswith('y'):
                print "\n++Free attack!++"
                #+4 because they're prone
                throw_away, multiplier = attack_roll(attack_bonus + 4)
                print colorz.YELLOW
                hit = raw_input('Did it hit? (y|n) ')
                if hit.lower().startswith('y'):
                    total_damage = damage_roll(2, 6, damage_bonus, multiplier, damage_doubling)
                    #Free Attack Shield Daze
                    shield_daze(target_name)
                    return total_damage
    return 0

def knockback():
    global STR_mod
    global base_attack_bonus
    global STR_check_size_mod

    print "\n%s++Knockback++" % colorz.BLUE
    print "Bull rush check roll:"
    #+4 for Improved Bull Rush
    bull_rush_mod = STR_check_size_mod + STR_mod + 4
    bull_rush_check = general_dc_roll("Bull rush", 1, 20, bull_rush_mod)
    knockback_distance = 0
    print colorz.BLUE
    opposing_bull_rush_check = int(raw_input("Opposing bull rush check? "))
    if bull_rush_check > opposing_bull_rush_check:
        knockback_distance += 5
        br_check_diff = bull_rush_check - opposing_bull_rush_check
        while br_check_diff > 5:
            knockback_distance += 5
            br_check_diff -= 5

    print "\nTarget knocked back %d feet%s" \
        % (knockback_distance, colorz.GREEN)
    if knockback_distance > 0:
        hit = raw_input("Did target hit a wall/solid object? (y|n) ")
        if hit.lower().startswith('y'):
            total_damage = damage_roll(4, 6, STR_mod*2)
            return total_damage
    return 0

###############
# GORE ATTACK #
###############

def gore_attack(charging=False, power_attack=0, cleave=False):
    global STR_mod
    global base_attack_bonus
    global attack_based_size_mod
    global auto_roll
    global morale_attack_bonus
    global morale_damage_bonus

    total_damage = 0
    cleave_damage = 0

    ####Attack roll####
    gore_attack_bonus = base_attack_bonus + STR_mod + attack_based_size_mod
    gore_attack_bonus -= 5     #Natural off hand weapon penalty
    gore_attack_bonus -= power_attack #Power attack penalty
    gore_attack_bonus += morale_attack_bonus
    if charging:
        gore_attack_bonus += 2

    total_attack_roll, multiplier = attack_roll(gore_attack_bonus)
    hit = raw_input('Did it hit? (y|n) ')
    if hit.lower().startswith('n'):
        if cleave:
            return cleave_damage
        return total_damage, cleave_damage
    
    ####Damage roll####
    damage_mod = STR_mod//2 + power_attack + morale_damage_bonus
    total_damage = damage_roll(1, 8, damage_mod, multiplier)

    #Dealing with cleave
    if cleave:
        return total_damage
        
    print colorz.YELLOW
    cleave = raw_input("Did it cleave? (y|n) ")
    if cleave.lower().startswith('y'):
        print  "%sCleaving....\n%s" % (colorz.PURPLE, colorz.GREEN)
        cleave_damage += gore_attack(charging, power_attack, True)
        
    return total_damage, cleave_damage

#################
# THROW BOULDER #
#################

def throw_boulder(boulder_range):
    global STR_mod
    global base_attack_bonus
    global attack_based_size_mod
    global auto_roll
    global morale_attack_bonus
    global morale_damage_bonus
    
    total_damage = 0
    boulder_attack_bonus = base_attack_bonus + STR_mod + attack_based_size_mod
    boulder_attack_bonus += morale_attack_bonus
    

    #Range mod
    distance = int(raw_input('\n\nHow far away is the target? (in feet) '))
    if distance >= boulder_range * 5:
        print "Target too far away"
        return total_damage

    range_penalty = 0
    while distance >= boulder_range:
        distance -= boulder_range
        range_penalty += 1

    #Attack roll
    total_attack_roll, multiplier = attack_roll(boulder_attack_bonus, range_penalty)
    hit = raw_input('Did it hit? (y|n) ')
    if hit.lower().startswith('n'):
        return total_damage

    #Damage roll
    damage_mod = STR_mod + morale_damage_bonus
    total_damage = damage_roll(2, 8, damage_mod, multiplier)
    
    return total_damage


###############
# MAIN METHOD #
###############

#TODO: These should be pulled from the xml
hd_level = 11
STR_mod = 16
base_attack_bonus = 5

#Use a dict for these
STR_check_size_mod = 4
attack_based_size_mod = -1

shield_enhancement_bonus = 1
boulder_range = 50
morale_attack_bonus = 0
morale_damage_bonus = 0

total_damage = {}
cleave_damage = {}

print colorz.PURPLE
print "############################################"
print "#      WELCOME! TO KRAG'S DAMAGE CALC!     #"
print "############################################"

round_num = 1

while True:
    print "\n%sCombat round #%d%s" % (colorz.BLUE, round_num, colorz.YELLOW)
    #Auto roll?
    auto_roll = raw_input('Auto roll dice?(y|n) ')
    if auto_roll.lower().startswith('y'):
        auto_roll = True
    else:
        auto_roll = False

    #Charging?
    charging = raw_input('Are you charging? (y|n) ')
    if charging.lower().startswith('y'):
        charging = True
    else:
        charging = False

    #Power attack?
    power_attack = int(raw_input('How many points to power attack? (Max %d) '
        % base_attack_bonus))
    if power_attack > base_attack_bonus:
        print  "%sToo many points!%s" % (colorz.RED, colorz.ENDC)
        quit()


    #Choose your attacks!
    while(True):
        print colorz.GREEN
        attack =  raw_input('\nWhat is your attack? (shield|gore|boulder|death move|none) ')
        if attack.lower() == 'shield':
            total_damage['shield'], cleave_damage['shield'] \
                = shield_attack(shield_enhancement_bonus, charging, power_attack)

        elif attack.lower() == 'gore':
            total_damage['gore'], cleave_damage['gore'] \
                = gore_attack(charging, power_attack)

        elif attack.lower() == 'boulder':
            if charging:
                print "%sCan't throw boulder while charging.\n" % colorz.RED
            else:
                total_damage['boulder'] = throw_boulder(boulder_range)
            
        elif attack.lower() == 'death move': 
            str_roll = general_dc_roll("STR check", total_mod=STR_mod)
            if str_roll > STR_mod + 1:
                print "%sDeath move successful!%s" % (colorz.RED, colorz.YELLOW)
                if morale_attack_bonus < 1:
                    morale_attack_bonus = 1
                if morale_damage_bonus < 1:
                    morale_damage_bonus = 1

        elif attack.lower() == 'none':
            break

        print colorz.YELLOW
        again = raw_input('\nAnother attack? (y|n) ')
        if again.lower().startswith('n'):
            break

    #Print out damage summary!
    print "\n\n%s####Damage done this round####" % colorz.RED
    if total_damage:
        print "\nRegular Damage: "
        if 'shield' in total_damage:
            print "-Shield:"
            for target in total_damage['shield'].keys():
                print "--%s: %d" % (target, total_damage['shield'][target])

            if not total_damage['shield']:
                print "-- None"

        if 'gore' in total_damage:
            print "-Gore: %d" % total_damage['gore']

        if 'boulder' in total_damage:
            print "-Boulder: %d" % total_damage['boulder']

    if cleave_damage:
        print "\nCleave Damage: "
        if 'shield' in cleave_damage:
            print "-Shield:"
            for target in cleave_damage['shield'].keys():
                print "--%s: %d" % (target, cleave_damage['shield'][target])

            if not cleave_damage['shield']:
                print "-- None"

        if 'gore' in cleave_damage:
            print "-Gore: %d" % cleave_damage['gore']
    print colorz.YELLOW
    
    again = raw_input('Continue? (y|n) ')
    if again.lower().startswith('n'):
        break

print colorz.ENDC
