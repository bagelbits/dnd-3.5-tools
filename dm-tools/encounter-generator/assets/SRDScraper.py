#Monster Data Scraper

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import csv
import sys
import time
from time import strftime
import traceback
import re


debug = False
driver = webdriver.Firefox()
siteURL = "http://www.d20srd.org/indexes/monsters.htm"
typeList = ["animal", "humanoid", "monstrous humanoid", "giant", "aberration", "magical beast", "outsider", "construct", "dragon", "elemental", "fey", "ooze", "plant", "undead", "vermin", "deathless"]
skillList = [u'\u2014', 'gather information', 'diplomacy', 'profession', 'jump', 'disguise', 'use rope', 'disable device', 'concentration', 'truenaming', 'hide', 'knowledge', 'perform', 'escape artist', 'open lock', 'handle animal', 'forgery', 'survival', 'decipher script', 'listen', 'swim', 'spellcraft', 'martial lore', 'heal', 'spot', 'move silently', 'craft', 'iaijutsu focus', 'bluff', 'lucid dreaming', 'autohypnosis', 'use psionic device', 'tumble', 'search', 'use magic device', 'speak language', 'intimidate', 'ride', 'sense motive', 'control shape', 'sleight of hand', 'climb', 'balance', 'handle humanoid', 'appraise']
featList = [u'\u2014', 'weapon finesse', 'athletic', 'empower spell', 'extra turning', 'shield proficiency', 'toughness', 'deceitful', 'agile', 'improved unarmed strike', 'great fortitude', 'trample', 'improved disarm', 'exotic weapon proficiency', 'whirlwind attack', 'combat reflexes', 'widen spell', 'dodge', 'greater weapon specialization', 'quick draw', 'heighten spell', 'lightning reflexes', 'improved overrun', 'magical aptitude', 'multiattack', 'armor proficiency (medium)', 'investigator', 'natural spell', 'greater two-weapon fighting', 'improved sunder', 'deft hands', 'improved familiar', 'greater spell penetration', 'mounted archery', 'spring attack', 'spell penetration', 'improved critical', 'power attack', 'weapon focus', 'negotiator', 'spell mastery', 'spirited charge', 'ride-by attack', 'improved trip', 'far shot', 'stealthy', 'improved two-weapon fighting', 'alertness', 'run', 'great cleave', 'shot on the run', 'skill focus', 'improved initiative', 'leadership', 'improved shield bash', 'greater weapon focus', 'cleave', 'manyshot', 'diligent', 'eschew materials', 'diehard', 'improved feint', 'spell focus', 'stunning fist', 'mobility', 'improved counterspell', 'self-sufficient', 'greater spell focus', 'craft wondrous item', 'two-weapon defense', 'quicken spell', 'craft magic arms and armor', 'silent spell', 'two-weapon fighting', 'snatch arrows', 'scribe scroll', 'enlarge spell', 'nimble fingers', 'brew potion', 'craft staff', 'tower shield proficiency,', 'rapid shot', 'still spell', 'blind-fight', 'improved bull rush', 'mounted combat', 'point blank shot', 'improved grapple', 'acrobatic', 'extend spell', 'animal affinity', 'improved turning', 'endurance', 'simple weapon proficiency', 'combat casting', 'armor proficiency (light)', 'forge ring', 'rapid reload', 'deflect arrows', 'track', 'craft rod', 'armor proficiency (heavy)', 'improved precise shot', 'augment summoning', 'craft wand', 'martial weapon proficiency', 'persuasive', 'combat expertise', 'iron will', 'weapon specialization', 'precise shot', 'maximize spell']
environmentList = ['warm plains', 'warm mountains', 'a chaos-aligned plane', 'weapon finesse', 'cold hills', 'temperate hills', 'a lawful evil plane', 'cold plains', 'temperate forest', 'warm forests', 'a lawful evil-aligned plane', 'cold forests', 'any', 'ethereal plane', 'an evil-aligned plane', 'any good-aligned plane', 'a chaotic good-aligned plane',  'toughness', 'cold mountains', 'temperate marshes', 'a chaotic evil plane', 'a lawful good-aligned plane', 'warm deserts', 'elemental plane of fire', 'a chaotic evil-aligned plane', 'temperate plains', 'elemental plane of earth', 'temperate mountains', 'mountains', 'elemental plane of air', 'warm forest', 'cold marshes', 'temperate aquatic', 'a chaotic good plane', 'underground', 'cold aquatic', 'plane of shadow', 'warm hills', 'a good-aligned plane.', 'a neutral evil plane', 'cold mountains (scrag: cold aquatic)', 'a chaotic-aligned plane', 'warm aquatic', 'temperate', 'a lawful good plane', 'a lawful-aligned plane', 'temperate deserts', 'cold desert', 'temperate forests', 'a evil-aligned plane', 'warm marshes', 'plane of limbo', 'positive energy plane', 'any aquatic', 'any land', 'elemental plane of water']
organizationList = ['any', 'tribe', 'patrol', 'crowd', 'guardian detail', 'colony', 'cluster', 'gang', 'mob', 'flock', 'domesticated', 'hunting/raiding party', 'cloud', 'buzz', 'solitary', 'brood', 'group', 'family', 'platoon', 'cete', 'click', 'swarm', 'squad', 'fright', 'hunting/raiding/trading party', 'terror', 'pride', 'nest', 'flight', 'company', 'eyrie', 'herd', 'band', 'plague', 'tomb guard', 'pair', 'troupe', 'mounted', 'grace', 'infestation', 'clan', 'school', 'hunting party', 'heard', 'grove', 'clutch', 'covey', 'hive', 'mass', 'troop', 'team', 'mixed patch', 'warden squad', 'pod', 'slaver brood', 'wing', 'pack'] 
CRList = ["1/10", "1/8", "1/6", u'\xbc', "1/3", u'\xbd', "4 (5 with irresistible dance)", "4 (normal); 6 (pyro- or cryo-)", "5 (normal); 7 (pyro- or cryo-)", "6 (normal); 8 (pyro- or cryo-)", "7 (normal); 9 (pyro- or cryo-)", "8 (normal); 10 (pyro- or cryo-)", "9 (normal); 11 (pyro- or cryo-)", "10 (normal); 12 (pyro- or cryo-)", "11 (normal); 13 (pyro- or cryo-)", "8 (elder 9)", "5 (noble 8)", "1 (see text)", "2 (without pipes) or 4 (with pipes)"]
treasureList = [u'\u2014', "standard", "Standard", "none", "coins", "goods", "items", "shirt"]
alignmentList = ["lawful", "neutral", "chaotic", "good", "evil", "(same as creator)", u'\u2014']
advancementList = [u'\u2014', "by character class", "hd", "special", "huge", "gargantuan", "none"]
inputFile = "SRDMonsters.csv"
outputFile = "SRDMonsters"+strftime("%Y-%m-%d %H:%M:%S")+".csv"
for i in range(1, 31):
  CRList.append(str(i))

#Grabs all relevant data from a single monster, given a link name (monster_data[0]).  Then outputs 
#the data to a line in a file given in OutputFile
def scrape_a_monster(monster_data, outputFile):
  tableNumber = str(monster_data[1])
  sideNumber = str(monster_data[2])
  numVersions = str(monster_data[3])
  monster = []
  element_skips = 0
  if tableNumber != "0":
    driver.get(siteURL)
    if monster_data[0] == "Will-O'-Wisp":
      driver. get("http://www.d20srd.org/srd/monsters/willOWisp.htm")
    else:
      try:
        driver.find_element_by_link_text(monster_data[0]).click()
      except:
        print "Unable to click on "+monster_data[0]+", " +str(sys.exc_info()[0])
    for versions in range(int(numVersions)):
      if monster_data[0] == "Will-O'-Wisp":
        monster = ["Will-O'-Wisp"]
      else:
        if int(sideNumber) > 0:
          try:
            monster = [driver.find_element_by_xpath("//body/table["+tableNumber+"]/tbody/tr[1]/th["+str(int(sideNumber)+1+int(versions))+"]").text]
          except NoSuchElementException:
            monster = ["No Such Element:  //body/table["+tableNumber+"]/tbody/tr[1]/th["+str(int(sideNumber)+1+int(versions))+"]"]
        else:
          monster = [monster_data[0]]
      for i in range(1,23):
        if int(sideNumber) > 0:
          try:
            stat = driver.find_element_by_xpath("//body/table["+tableNumber+"]/tbody/tr["+str(i+element_skips+1)+"]/td["+sideNumber+"]").text
            stepIncrease = verify_stat(i+element_skips, stat)
            if stepIncrease == 0:
              monster.append(stat)
            else:
              print monster[0]
              element_skips = element_skips + stepIncrease
              for i in range(stepIncrease+1):
                monster.append("")
              monster.append(stat)
          except NoSuchElementException:
            if i == 1:
              element_skips = 1
              monster.append(driver.find_element_by_xpath("//body/table["+tableNumber+"]/tbody/tr["+str(i+element_skips+1)+"]/td["+sideNumber+"]").text)
            #else:
              #monster.append("No Such Element: //body/table["+tableNumber+"]/tbody/tr["+str(i+1)+"]/td["+sideNumber+"]")
        else:
          try:
            stat = driver.find_element_by_xpath("//body/table["+tableNumber+"]/tbody/tr["+str(i)+"]/td").text
            stepIncrease = verify_stat(i+element_skips, stat)
            if stepIncrease == 0:
              monster.append(stat)
            else:
              print monster[0]
              element_skips = element_skips + stepIncrease
              for i in range(stepIncrease):
                monster.append("")
              monster.append(stat)
          except NoSuchElementException:
            pass
            #monster.append("No Such Element:  //body/table["+tableNumber+"]/tbody/tr["+str(i)+"]/td")
      if debug:
        print monster
      monster = [stat.replace(u'\u2014', '-') for stat in monster]
      monster = [stat.replace(u'\xd8', '-') for stat in monster]
      monster = [stat.replace(u'\xd7' , 'X') for stat in monster]
      monster = [stat.replace(u'\xbd' , '1/2') for stat in monster]
      monster = [stat.replace(u'\u2019', "'") for stat in monster]
      monster = [stat.replace(u'\xbc', "1/4") for stat in monster]
      monster = [stat.replace(u'\u2026', "...") for stat in monster]
      outputFile.writerow(monster)
      element_skips = 0
  else:
    outputFile.writerow([monster_data[0]])

#Switch statement used to verify that the correct stats are going in the correct fields.
def verify_stat(position, stat_field):
  try:
    stat = stat_field.lower()
  except AttributeError:
    stat = stat_field.replace(u'\u2014', '-').replace(u'\xbd' , '1/2').replace(u'\xbc', "1/4").replace(u'\xe2', "-")
  if position == 1:
    for type in typeList:
      if type in stat:
        return 0
    print stat+ " is not a size/type"
    return -1 + verify_stat(position-1, stat)
  if position == 2:
    if "hp)" in stat:
      return 0
    else:
      print stat+ " is not hit dice"
      return -1 + verify_stat(position-1, stat)
  if position == 3:
    if "+" in stat or "-" in stat:
      return 0
    else:
      print stat+ " is not an initiative bonus"
      return -1 + verify_stat(position-1, stat)
  if position == 4:
    if "ft." in stat:
      return 0
    else:
      print stat+ " is not a speed"
      return -1 + verify_stat(position-1, stat) 
  if position == 5:
    if "touch" in stat or "natural" in stat:
      return 0
    else:
      print stat+ " is not an AC"
      return -1 + verify_stat(position-1, stat) 
  if position == 6:
    if "/" in stat:
      return 0
    else:
      print stat+ " is not a base attack/grapple"
      return -1 + verify_stat(position-1, stat) 
  if position == 7:
    if "melee" in stat or "ranged" in stat or "swarm" in stat or u'\u2014' in stat:
      return 0
    else:
      print stat+ " is not an attack"
      return -1 + verify_stat(position-1, stat) 
  if position == 8:
    if "melee" in stat or "ranged" in stat or "swarm" in stat or u'\u2014' in stat:
      return 0
    else:
      print stat+ " is not a full attack"
      return -1 + verify_stat(position-1, stat) 
  if position == 9:
    if "ft." in stat:
      return 0
    else:
      print stat+ " is not a space/reach"
      return -1 + verify_stat(position-1, stat)
  if position == 10:
    if "ft." in stat:
      print stat+ " is not a list of Special Attacks"
      return -1 + verify_stat(position-1, stat)
    else:
      return 0
  if position == 11:
    if "fort" in stat and "ref" in stat and "will" in stat:
      print stat+ " is not a list of Special Qualities"
      return -1 + verify_stat(position-1, stat)
    else:
      return 0
  if position == 12:
    if "fort" in stat and "ref" in stat and "will" in stat:
      return 0
    else:
      print stat+ " is not a list of saves"
      return -1 + verify_stat(position-1, stat) 
  if position == 13:
    if "str" in stat and "dex" in stat and "con" in stat and "int" in stat:
      return 0
    else:
      print stat+ " is not a list of abilities"
      return -1 + verify_stat(position-1, stat)
  if position == 14:
    for skill in skillList:
      if skill in stat:
        return 0
    print stat+ " is not a skill list"
    return +1 + verify_stat(position+1, stat)
  if position == 15:
    for feat in featList:
      if feat in stat:
        return 0
    print stat+ " is not a feat list"
    return +1 + verify_stat(position+1, stat) 
  if position == 16:
    for environment in environmentList:
      if environment in stat:
        return 0
    print stat+ " is not an environment"
    return +1 + verify_stat(position+1, stat) 
  if position == 17:
    for organization in organizationList:
      if organization in stat:
        return 0
    print stat+ " is not an organization type"
    return +1 + verify_stat(position+1, stat) 
  if position == 18:
    if stat in CRList:
      return 0
    else:
      print stat+ " is not a valid CR!"
      return +1 + verify_stat(position+1, stat)
  if position == 19:
    for treasure in treasureList:
      if treasure in stat:
        return 0
    print stat+ " is not a treasure list"
    return 1 + verify_stat(position+1, stat)  
  if position == 20:
    for alignment in alignmentList:
      if alignment in stat:
        return 0
    print stat+ " is not an alignment"
    return 1 + verify_stat(position+1, stat)  
  if position == 21:
    for advancement in advancementList:
      if advancement in stat:
        return 0
    print stat+ " is not an advancement type"
    return 1 + verify_stat(position+1, stat)  
  if position == 22:
    if "+" in stat or u'\u2014' in stat:
      return 0
    else:
      print stat+" is not a level adjustment"
      return +1 + verify_stat(position+1, stat)
  if position == 23:
    return 0
  print "Position in verify_stat out of bounds! "+str(position)+", "+stat_field
  return -10





#Main Body Starts here
#Grabs a list of monster names from "SRDMonsters.csv", scrapes the data, and writes a new file
#with a date of all the monsters.
#try:
with open(inputFile, "rU") as csvfile:
  monsterReader = csv.reader(csvfile)
  with open(outputFile, 'wb') as csvfile:
    monsterWriter = csv.writer(csvfile, delimiter=',', quotechar='"')
    monsterWriter.writerow(["Name", "Size/Type", "Hit Dice", "Initiative", "Speed", "Armor Class", "Base Attack/Grapple", "Attack", "Full Attack", "Space/Reach", "Special Attacks", "Special Qualities", "Saves", "Abilities", "Skills", "Feats", "Environment", "Organization", "Challenge Rating", "Treasure", "Alignment", "Advancement", "Level Adjustment"])
    for data in monsterReader:
      #try:
      scrape_a_monster(data, monsterWriter)
      #except:
        #print data[0]+" Didn't work."
        #print traceback.print_exc()
print "Scraping complete."
      
#except:
  #print "Unexpected error while loading monster data file:", sys.exc_info()[0]
  #print traceback.print_exc()
  #print "Please make sure MonsterNames.csv is located in the same folder as this program"
  #print sys.exc_info()[0]
driver.quit()