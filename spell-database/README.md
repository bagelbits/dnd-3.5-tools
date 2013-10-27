TO DO:
================

* Scrape D&D Tools for all of it's spells and compare with what I currently have.
- Grab spell urls off of http://dndtools.eu/spells/, just do a simple scrape.
- Everything is contained with in the <table></table>
- Manually set pages for now to 203
- Make sure to store spell name with link
- Spell page starts with data like this: <h2>Aquatic Escape</h2>
- Ends with: <div class="nice-textile"></div>

* domain_feet and class tables should eventually have their book columns correspond to a book id instead of a piece of text.
* Ability to add spells directly into the database, potentially as a form. Actually..... I could told set-up a quick and dirty form on fuzzybitproductions.com and give it out, then I could format the data nicely! Will probably start out with it just emailing it to myself. I can put together  the better way later



* General code clean up
* Split db insert code and spell print out into it's own class. Maybe
a general purpose CRUD class

general/random_scroll_generator.py
* Deal with special case classes like Sanctified, and Corrupt
* Randomly pick arcane or divine if both options are there.
