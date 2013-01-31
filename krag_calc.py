from random import randint

def roll_dice(dice=1, sides=6):
    try: return [randint(1, sides) for x in range(dice)]
    except: return []

def attack_roll(total_attack_bonus=0, range_penalty=0):
    global auto_roll

    multiplier = 1
    print "Attack roll: d20 + %d - %d" % (boulder_attack_bonus, range_penalty)
    if auto_roll:
        total_attack = sum(roll_dice(1, 20))
    else:
        print "Roll now. (Don't add in any mods)"
        total_attack = int(raw_input('What did you roll? ').strip())

    if total_attack = 20:
        multiplier = 2
        print "Gotta crit! Roll to confirm!"
        print "Attack roll: d20 + %d - %d" % (boulder_attack_bonus, range_penalty)
        if auto_roll:
            total_attack = sum(roll_dice(1, 20))
        else:
            print "Roll now. (Don't add in any mods)"
            total_attack = int(raw_input('What did you roll? ').strip())
        
    total_attack += boulder_attack_bonus
    total_attack -= range_penalty

    print "Attack roll result: %d" % total_attack

    return total_attack, multiplier

def damage_roll(num_of_dice=1, num_of_sides=6, total_mod=0, multiplier=1):
    global auto_roll

    if multiplier > 1:
        print "Damage roll: %dd%d + %d X%d" % (num_of_dice, num_of_sides,
            STR_mod, multiplier)
    else:
        print "Damage roll: %dd%d + %d" % (num_of_dice, num_of_sides, STR_mod)

    if auto_roll:
        total_damage = sum(roll_dice(num_of_dice, num_of_sides))
    else:
        print "Roll now. (Don't add in any mods)"
        total_damage = raw_input('What did you roll? ')
        total_damage = total_damage.split(",")
        total_damage = sum(int(x.strip()) for x in total_damage)

    #Last minute mods
    total_damage += total_mod
    total_damage *= multiplier

    print "Damage roll result: %d" % total_damage_roll

    return total_damage

def shield_attack(charging=False, power_attack=0, cleave=False):
    global STR_mod
    global base_attack_bonus
    global size_mod
    global auto_roll
    #+2 attack when charging
    
    #So, here's the full chain.

    #When you charge, you roll to hit. That's
    #Str bonus + BAB +2 +Enhancement Bonus (currently +1 for your shield) - Power Attack

    #Then you do damage. Because you deal double damage (Valorous Shield),
    #that's 3*Str Mod + 2* Shield damage (so, 2d8 I think?)
    # + 4* Power Attack Penalty +2 (Enhancement Bonus doubled).

    #Now, you get the free trip (note: only works on enemies no more than huge).
    #This is Str bonus + size mod (+4 for large) +4 for Improved Trip, opposed
    #by their trip check. If that works, roll to hit again, at +4 because they're prone.


    #Now, you get to Shield Slam them (the daze effect). They just have to
    #roll a save due to this:
    #http://dndtools.eu/feats/complete-warrior--61/shield-slam--2592/
    #So that's currently 10+ 1/2 character level (5) + str mod, and
    #they fort save against that or they can't act next round

    #Now you knock them back. Bull rush check,
    #1d20+Size mod + str bonus + 4 for Improved Bull Rush,
    #so same as trip check, and they go flying back if they fail to oppose. Whee!

    #And then if they hit a wall or solid object during the knockback
    #they take 4d6 + 2x str mod

    return total_damage, cleave_damage

def gore_attack(charging=False, power_attack=0, cleave=False):
    global STR_mod
    global base_attack_bonus
    global size_mod
    global auto_roll

    cleave_damage = 0
    total_damage = 0

    ####Attack roll####
    gore_attack_bonus = base_attack_bonus + STR_mod + size_mod
    gore_attack_bonus -= 5     #Natural off hand weapon penalty
    gore_attack_bonus -= power_attack #Power attack penalty
    if charging:
        gore_attack_bonus += 2

    total_attack_roll, multiplier = attack_roll(gore_attack_bonus)
    hit = raw_input('Did it hit?')
    if hit.lower().startswith('n'):
        if cleave:
            return cleave_damage
        return total_damage, cleave_damage
    
    ####Damage roll####
    damage_mod = STR_mod//2 + power_attack
    if cleave:
        cleave_damage = damage_roll(1, 8, damage_mod, multiplier)
        return cleave_damage
    else:
        total_damage = damage_roll(1, 8, damage_mod, multiplier)


    cleave = ("Did it cleave?")
    if cleave.lower().startswith('y'):
        cleave_damage = gore_attack(charging, power_attack, True)
        
    return total_damage, cleave_damage


def throw_boulder(boulder_range):
    global STR_mod
    global base_attack_bonus
    global size_mod
    global auto_roll
    
    total_damage = 0
    boulder_attack_bonus = base_attack_bonus + STR_mod + size_mod
    

    #Range mod
    distance = int(raw_input('How far away is the target? (in feet) '))
    if distance >= boulder_range * 5:
        print "Target too far away"
        return total_damage

    range_penalty = 0
    while distance >= boulder_range:
        distance -= boulder_range
        range_penalty += 1

    #Attack roll
    total_attack_roll, multiplier = attack_roll(boulder_attack_bonus, range_penalty)
    print "Attack roll result: %d" % total_attack_roll
    hit = raw_input('Did it hit?')
    if hit.lower().startswith('n'):
        return total_damage

    #Damage roll
    total_damage = damage_roll(4, 8, STR_mod, multiplier)
    
    return total_damage



STR_mod = 16
base_attack_bonus = 5
size_mod = -1
boulder_range = 50
total_damage = {'boulder': 0, 'gore': 0, 'shield': 0}
cleave_damage = {'gore': 0, 'shield': 0}

#Auto roll?
auto_roll = raw_input('Auto roll dice? ')
if auto_roll.lower().startswith('y'):
    auto_roll = True
else:
    auto_roll = False

#Charging?
charging = raw_input('Are you charging? ')
if charging.lower().startswith('y'):
    charging = True
else:
    charging = False

#Power attack?
power_attack = int(raw_input('How many points to power attack? (Max %d) '
    % base_attack_bonus))
if power_attack > base_attack_bonus:
    print "Too many points!"
    quit()

while(True):
    attack =  raw_input('What is your attack? ')
    if attack.lower() == 'shield':
        total_damage['shield'], cleave_damage['shield'] = shield_attack(charging, power_attack)

    if attack.lower() == 'gore' or attack.lower() == 'horns':
        total_damage['gore'], cleave_damage['gore'] = gore_attack(charging, power_attack)

    if attack.lower() == 'boulder' or attack.lower() == 'rock':
        total_damage['boulder'] = throw_boulder(boulder_range)

    again = raw_input('Another attack? ')
    if again.lower().startswith('n'):
        break


print "Damage done this round:"
print total_damage
print cleave_damage
