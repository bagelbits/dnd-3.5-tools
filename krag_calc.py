from random import randint

def roll_dice(dice=1, sides=6):
    try: return [randint(1, sides) for x in range(dice)]
    except: return []

def shield_attack(total_damage, cleave_damage, cleave=False):
    return total_damage, cleave_damage

def gore_attack(total_damage, cleave_damage, cleave=False):
    return total_damage, cleave_damage

def throw_boulder(total_damage, cleave_damage, cleave=False):
    global STR_mod
    global melee_TAB
    global auto_roll
    
    distance = raw_input('How far away is the target? (in feet) ')
    #TODO Distance mod
    #Attack roll
    print "Attack roll: d20+" + str(melee_TAB)
    if auto_roll:
        attack_roll = roll_dice(1, 20) + melee_TAB
    else:
        attack_roll = raw_input('What did you roll? ')
    
    hit = raw_input('Did it hit?')
    if hit.lower().startswith('n'):
        return total_damage, cleave_damage
    
    #Damage roll
    print "Damage roll: 4d8+" + str(STR_mod)
    if auto_roll:
        damage_roll = roll_dice(4, 8) + STR_mod
    else:
        damage_roll = raw_input('What did you roll? ')
    
    if cleave:
        cleave_damage['boulder'] = damage_roll
    else:
        total_damage['boulder'] = damage_roll

    if not cleave:
        cleave = ("Did it cleave?")
        if cleave.lower().startswith('y'):
            return throw_boulder(total_damage, cleave_damage, True)
        
    return total_damage, cleave_damage
    


STR_mod = 16
melee_TAB = 20
total_damage = {'boulder': 0, 'gore': 0, 'shield': 0}
cleave_damage = {'boulder': 0, 'gore': 0, 'shield': 0}

auto_roll = raw_input('Auto roll dice? ')
if auto_roll.lower().startswith('y'):
    auto_roll = True
else:
    auto_roll = False

#TODO Implement Power Attack

attack =  raw_input('What is your attack? ')
if attack.lower() == 'shield':
    total_damage, cleave_damage = shield_attack(total_damage, cleave_damage)

if attack.lower() == 'gore' or attack.lower() == 'horns':
    total_damage, cleave_damage = gore_attack(total_damage, cleave_damage)

if attack.lower() == 'boulder' or attack.lower() == 'rock':
    total_damage, cleave_damage = throw_boulder(total_damage, cleave_damage)


print total_damage
print cleave_damage
