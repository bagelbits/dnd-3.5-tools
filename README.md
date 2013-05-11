D&amp;D 3.5 Tools
================

Consists of:  
* Damage calculator for D&amp;D character
* General skill roller with xml importer
* GUI version of skill roller
* Spell database populater
* Random magic scroll generator (Coming soon)

TO DO:  
================

character/specific/krag_calc.py:
* Rage feat/Bear form bonus feat
* 2nd look over to clean up code
* GUI version

general/spell_db_populater.py:
* Populate spell_class and spell_domain tables
* Import files for book, class, school, subtype, and component tables
* General code clean up
* Allow for the DM to set % for class. May want to just use types like Core, Uncommon, Rare, Nonexistant.

general/scroll_generator.py
* Interface with spell.db
* Deal with special case classes like All, Sanctified, and Corrupt
* Randomly pick arcane or divine if both options are there.
* Generally just write it.
