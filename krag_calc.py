from random import randint

def roll_dice(dice=1, sides=6):
    try: return [randint(1, sides) for x in range(dice)]
    except: return []

def general_dc_roll(dc_name, num_of_dice=1, num_of_sides=20, total_mod=0):
    global auto_roll

    total_dc_roll = 0

    print "%s roll: %dd%d + %d" % (dc_name, num_of_dice, num_of_sides, total_mod)
    if auto_roll:
        base_dc_roll = sum(roll_dice(1, 20))
    else:
        print "Roll now. (Don't add in any mods)"
        base_dc_roll = int(raw_input('What did you roll? ').strip())

    print "Base roll: %d\n" % base_dc_roll

    while base_dc_roll == 20:
        total_dc_roll += base_dc_roll
        print "Exploding dice! Roll again"
        print "%s roll: %dd%d + %d" % (dc_name, num_of_dice, num_of_sides, total_mod)
        if auto_roll:
            base_dc_roll = sum(roll_dice(1, 20))
        else:
            print "Roll now. (Don't add in any mods)"
            base_dc_roll = int(raw_input('What did you roll? ').strip())
        print "Base roll: %d\n" % base_dc_roll

    if base_dc_roll == 1:
        print "Critical Failure!"

    total_dc_roll += total_mod

    print "Total %s roll result: %d" % (dc_name, total_dc_roll)

    return total_dc_roll
    

def attack_roll(total_attack_bonus=0, range_penalty=0):
    global auto_roll

    multiplier = 1
    print "Attack roll: d20 + %d - %d" % (total_attack_bonus, range_penalty)
    if auto_roll:
        base_attack_roll = sum(roll_dice(1, 20))
    else:
        print "Roll now. (Don't add in any mods)"
        base_attack_roll = int(raw_input('What did you roll? ').strip())

    print "Base roll: %d\n" % base_attack_roll

    while base_attack_roll == 20:
        multiplier += 1
        print "Gotta crit! Roll to confirm!"
        print "Attack roll: d20 + %d - %d" % (total_attack_bonus, range_penalty)
        if auto_roll:
            base_attack_roll = sum(roll_dice(1, 20))
        else:
            print "Roll now. (Don't add in any mods)"
            base_attack_roll = int(raw_input('What did you roll? ').strip())
        print "Base roll: %d\n" % base_attack_roll

    if base_attack_roll == 1:
        print "Critical Failure!"
        
    roll_mod += total_attack_bonus
    roll_mod -= range_penalty

    total_attack = base_attack_roll + roll_mod

    print "Total Attack roll result: %d" % total_attack
    if multiplier > 1:
        "Total multiplier: %dx" % multiplier

    return total_attack, multiplier


def damage_roll(num_of_dice=1, num_of_sides=6, total_mod=0, damage_doubling=1, multiplier=1):
    global auto_roll

    num_of_dice *= damage_doubling
    total_mod *= damage_doubling

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


def shield_attack(item_mod=0, charging=False, power_attack=0, cleave=False):
    global STR_mod
    global base_attack_bonus
    global STR_check_size_mod
    global size_mod
    global shield_enhancement_bonus
    global auto_roll

    
    dice_to_roll = 2
    damage_doubling = 1

    raw_input('Mighty swing used. Please pick 3 adjacent squares.')

    ####Attack roll####
    shield_attack_bonus = base_attack_bonus + STR_mod + size_mod + shield_enhancement_bonus
    shield_attack_bonus -= power_attack #Power attack penalty
    if charging:
        shield_attack_bonus += 2

    total_attack_roll, multiplier = attack_roll(shield_attack_bonus)
    hit = int(raw_input('How many things were hit?'))
    if hit == 0:
        if cleave:
            return cleave_damage
        return total_damage, cleave_damage
    
    if charging:
        multiplier *= 2
        damage_doubling += 1

    #Damage roll with mighty swing, shield charge, shield slam, knockback... yay for fun times
    damage_mod = STR_mod*1.5 + power_attack* 2 + shield_enhancement_bonus

    targets = {}

    for target in range(1, hits + 1):
        target_name = 'target_%d' % target
        cleave_damage = 0
        total_damage = 0

        if cleave:
            cleave_damage = damage_roll(2, 6, damage_mod, damage_doubling, multiplier)
        else:
            total_damage = damage_roll(2, 6, damage_mod, damage_doubling, multiplier)

        #Trip attempt
        if charging:
            can_trip = raw_input('Enemy bigger than huge? (y|n) ')
            if can_trip.lower().startswith('n'):
                touch_attack_roll = general_dc_roll("Touch attack", 1, 20, STR_mod + base_attack_bonus)
                
                touch_success = raw_input('Did touch attack succeeed? (y|n) ')
                if tripped.lower().startswith('y'):
                    print "Strength check to beat: %d" STR_mod + STR_check_size_mod + 4
                    
                    tripped = raw_input('Did you trip it? (y|n) ')
                    if tripped.lower().startswith('y'):
                        #+4 because they're prone
                        throw_away, free_attack_multiplier = attack_roll(shield_attack_bonus + 4)
                        hit = raw_input('Did it hit? (y|n) ')
                        if hit.lower().startswith('y'):
                            if cleave:
                                cleave_damage += damage_roll(2, 6, damage_mod, damage_doubling, free_attack_multiplier)
                            else:
                                total_damage += damage_roll(2, 6, damage_mod, damage_doubling, free_attack_multiplier)

        #Shield daze
        fort_save = 10 + hd_level//2 + STR_mod
        print "Target: %s must make Fort save and beat %d" % (target_name)
        raw_input("Press Enter to continue...")

        #Knockback with bull rush check
        print "Bull rush check roll:"
        bull_rush_mod = STR_check_size_mod + STR_mod + 4 #+4 for Improved Bull Rush
        bull_rush_check = general_dc_roll("Bull rush", 1, 20, )

        opposing_bull_rush_check = int(raw_input("Opposing bull rush check? "))
        if bull_rush_check > opposing_bull_rush_check:
            knockback_distance = 5
            br_check_diff = bull_rush_check - opposing_bull_rush_check
            while br_check_diff > 5:
                knockback_distance += 5
                br_check_diff -= 5

        print "Target knocked back %d feet" % knockback_distance

        hit = raw_input("Did target hit a wall/solid object? (y|n) ")
        if hit.lower().startswith('y'):
            if cleave:
                cleave_damage += damage_roll(4, 6, STR_mod*2)
            else:
                total_damage += damage_roll(4, 6, STR_mod*2)

        targets[target_name] = total_damage
    
    
    if cleave:
        return cleave_damage

    cleave = ("Did it cleave?")
    if cleave.lower().startswith('y'):
        cleave_damage = shield_attack(item_mod, charging, power_attack, True)
        
    return total_damage, cleave_damage

def gore_attack(charging=False, power_attack=0, cleave=False):
    global STR_mod
    global base_attack_bonus
    global size_mod
    global auto_roll

    total_damage = 0

    ####Attack roll####
    gore_attack_bonus = base_attack_bonus + STR_mod + size_mod
    gore_attack_bonus -= 5     #Natural off hand weapon penalty
    gore_attack_bonus -= power_attack #Power attack penalty
    if charging:
        gore_attack_bonus += 2

    total_attack_roll, multiplier = attack_roll(gore_attack_bonus)
    hit = raw_input('Did it hit? (y|n) ')
    if hit.lower().startswith('n'):
        if cleave:
            return total_damage
        return total_damage, 0
    
    ####Damage roll####
    damage_mod = STR_mod//2 + power_attack
    total_damage = damage_roll(1, 8, damage_mod, 1, multiplier)

    #Dealing with cleave
    if cleave:
        return total_damage
        
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
    hit = raw_input('Did it hit? (y|n) ')
    if hit.lower().startswith('n'):
        return total_damage

    #Damage roll
    total_damage = damage_roll(4, 8, STR_mod, multiplier)
    
    return total_damage


hd_level = 11
STR_mod = 16
base_attack_bonus = 5
STR_check_size_mod = 4
size_mod = -1
shield_enhancement_bonus = 1
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
