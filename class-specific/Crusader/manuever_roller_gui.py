#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
    Hacked together general purpose crusader maneuver roller.
    With GUI.

    By Chris Ward
"""

from assets.crusader_maneuvers import maneuver_descriptions
from math import ceil
from random import randint

from Tkinter import *
import tkMessageBox

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

class CrusaderManeuverApp:
  character_stats = {
    'level' : 0,
    'feat_taken' : 0,
    'maneuvers_readied' : 0,
    'maneuvers_granted' : 0,
    'maneuvers_known' : 0,
    'stances_known' : 0,}
  maneuver_types_learned = {'Devo' : 0, 'Stone' : 0, 'White' : 0}
  maneuvers_known = []
  maneuvers_readied = []
  maneuvers_granted = []

  # Initial build script
  def __init__(self, master):
    self.master = master

    #Window 1
    self.character_stats_frame = Frame(master, background='misty rose')
    self.character_stats_frame.grid(row=0)
    self.character_stats_setup()

    #Window 2
    self.maneuver_select_frame = Frame(master, background='misty rose')
    self.maneuver_select_setup()

    #Window 3
    self.maneuver_ready_frame = Frame(master, background='misty rose')
    self.maneuver_ready_setup()

    #Window 4
    self.encounter_frame = Frame(master, background='misty rose')
    self.encounter_setup()


  ##################################################################################
  #                           Frame setup methods                                  #
  ##################################################################################

  def character_stats_setup(self):
    Label(self.character_stats_frame, text="Level:",
      background='misty rose').grid(sticky=E)
    
    character_level = Entry(self.character_stats_frame,
      highlightbackground='misty rose', width=20)
    character_level.grid(row=0, column=1)
    character_level.focus()
    
    feat_taken = IntVar()
    Checkbutton(self.character_stats_frame, text="Extra Granted\nManeuver?",
      variable=feat_taken, background='misty rose').grid(row=0, column=2, sticky=W)

    Button(self.character_stats_frame,
      text='Begin',
      command=lambda: self.load_everything(character_level.get(),
        feat_taken.get()),
      background='misty rose',
      highlightbackground='misty rose').grid(row=2, columnspan=2)
    Button(self.character_stats_frame,
      text='Quit',
      command=self.character_stats_frame.quit,
      background='misty rose',
      highlightbackground='misty rose').grid(row=2, column=2)

  def maneuver_select_setup(self):
    self.total_maneuver_known_label = Label(self.maneuver_select_frame,
      text="Total Known Maneuvers: ",
      background='misty rose')
    self.total_maneuver_known_label.grid(row=0, sticky=W)
    Label(self.maneuver_select_frame, text="Possible Maneuvers:",
      background='misty rose').grid(row=0, column=2, sticky=W)

    self.maneuvers_known_list = Listbox(self.maneuver_select_frame,
      width=30,
      selectmode=MULTIPLE)
    self.maneuvers_known_list.grid(row=1, rowspan=4)
    self.maneuvers_possible_list = Listbox(self.maneuver_select_frame,
      width=30,
      selectmode=MULTIPLE)
    self.maneuvers_possible_list.grid(row=1, column=2, rowspan=4)

    Button(self.maneuver_select_frame,
      text='<',
      command=self.add_maneuver,
      background='misty rose',
      highlightbackground='misty rose').grid(row=2, column=1)
    Button(self.maneuver_select_frame,
      text='>',
      command=self.remove_maneuver,
      background='misty rose',
      highlightbackground='misty rose').grid(row=3, column=1)

    self.total_stances_known_label = Label(self.maneuver_select_frame,
      text="Total Known Stances: ",
      background='misty rose')
    self.total_stances_known_label.grid(row=5, sticky=W)
    Label(self.maneuver_select_frame, text="Possible Stances:",
      background='misty rose').grid(row=5, column=2, sticky=W)
    self.stances_known_list = Listbox(self.maneuver_select_frame,
      width=30,
      selectmode=MULTIPLE)
    self.stances_known_list.grid(row=6, rowspan=4)
    self.stances_possible_list = Listbox(self.maneuver_select_frame,
      width=30,
      selectmode=MULTIPLE)
    self.stances_possible_list.grid(row=6, column=2, rowspan=4)

    Button(self.maneuver_select_frame,
      text='<',
      command=self.add_stance,
      background='misty rose',
      highlightbackground='misty rose').grid(row=7, column=1)
    Button(self.maneuver_select_frame,
      text='>',
      command=self.remove_stance,
      background='misty rose',
      highlightbackground='misty rose').grid(row=8, column=1)

    Button(self.maneuver_select_frame,
      text='Set known',
      command=self.ready_maneuvers,
      background='misty rose',
      highlightbackground='misty rose').grid(row=10, columnspan=2)
    Button(self.maneuver_select_frame,
      text='Quit',
      command=self.maneuver_select_frame.quit,
      background='misty rose',
      highlightbackground='misty rose').grid(row=10, column=2)

  def maneuver_ready_setup(self):
    self.total_maneuver_ready_label = Label(self.maneuver_ready_frame,
      text="Total Maneuvers to Ready: ",
      background='misty rose')
    self.total_maneuver_ready_label.grid(row=0, columnspan=2)

    self.maneuvers_readied_list = Listbox(self.maneuver_ready_frame,
      width=20,
      selectmode=MULTIPLE)
    self.maneuvers_readied_list.grid(row=1, rowspan=4, columnspan=2)

    Button(self.maneuver_ready_frame,
      text='Start encounter',
      command=self.start_encounter,
      background='misty rose',
      highlightbackground='misty rose').grid(row=5)
    Button(self.maneuver_ready_frame,
      text='Quit',
      command=self.maneuver_ready_frame.quit,
      background='misty rose',
      highlightbackground='misty rose').grid(row=5, column=1)

  def encounter_setup(self):
    Label(self.encounter_frame, text="Granted manuevers this round:",
      background='misty rose').grid(row=0, columnspan=2)

    self.maneuvers_granted_list = Listbox(self.encounter_frame,
      width=20)
    self.maneuvers_granted_list.grid(row=1, rowspan=4, columnspan=2)

    Button(self.encounter_frame,
      text="Info",
      command=self.show_maneuver_info,
      background='misty rose',
      highlightbackground='misty rose').grid(row=5, column=0)
    Button(self.encounter_frame,
      text="Use",
      command=self.use_maneuver,
      background='misty rose',
      highlightbackground='misty rose').grid(row=5, column=1)
    
    Button(self.encounter_frame,
      text="Next round",
      command=self.next_round,
      background='misty rose',
      highlightbackground='misty rose').grid(row=6, column=0)
    Button(self.encounter_frame,
      text="End combat",
      command=self.end_combat,
      background='misty rose',
      highlightbackground='misty rose').grid(row=6, column=1)
    
    Button(self.encounter_frame,
      text="Quit",
      command=self.encounter_frame.quit,
      background='misty rose',
      highlightbackground='misty rose').grid(row=7, columnspan=2)


  ##################################################################################
  #                                Button methods                                  #
  ##################################################################################

  # Button populates the character_stats dict as well as the list of of possible
  # maneuvers and stances.
  def load_everything(self, character_level, feat_taken):
    try:
      character_level = int(character_level)
    except ValueError:
      tkMessageBox.showerror("Not a number",
        "Please enter a number as the level")
      return
    self.character_stats['level'] = character_level
    
    self.character_stats['feat_taken'] = feat_taken
    
    maneuvers_readied = character_level / 10 + 5
    self.character_stats['maneuvers_readied'] = maneuvers_readied
    self.total_maneuver_ready_label["text"] += str(maneuvers_readied)
    
    self.character_stats['maneuvers_granted'] = maneuvers_readied - 3 + feat_taken
    
    maneuvers_known = int(ceil(character_level / 2.0)) + 4
    self.character_stats['maneuvers_known'] = maneuvers_known
    self.total_maneuver_known_label['text'] += str(maneuvers_known)
    
    stances_known = (character_level - 2) / 7 + 2
    self.character_stats['stances_known'] = stances_known
    self.total_stances_known_label['text'] += str(stances_known)

    self.maneuvers_possible_list.delete(0, END)
    for maneuver_name in self.get_current_possible_maneuvers(character_level):
      self.maneuvers_possible_list.insert(END, maneuver_name)

    self.stances_possible_list.delete(0, END)
    for stance_name in self.get_current_possible_stances(character_level):
      self.stances_possible_list.insert(END, stance_name)

    self.character_stats_frame.grid_forget()
    self.maneuver_select_frame.grid(row=0)

  def add_maneuver(self):
    added_maneuvers = self.maneuvers_possible_list.curselection()

    for maneuver_id in added_maneuvers:
      if len(self.maneuvers_known_list.get(0, END)) == self.character_stats['maneuvers_known']:
        tkMessageBox.showerror("Max Known Maneuvers Reached",
          "You can't know any more maneuvers at your level!")
        break
      maneuver_name = self.maneuvers_possible_list.get(maneuver_id)
      self.maneuvers_known_list.insert(END, maneuver_name)
      self.maneuver_types_learned[maneuver_descriptions[maneuver_name]['school']] += 1

    self.update_maneuvers_and_stances_possible(self.character_stats['level'])

  def remove_maneuver(self):
    removed_maneuvers = map(int, self.maneuvers_known_list.curselection())
    removed_maneuvers.sort(reverse=True)

    for maneuver_id in removed_maneuvers:
      self.maneuvers_known_list.delete(maneuver_id)

    self.update_maneuvers_and_stances_possible(self.character_stats['level'])

  def add_stance(self):
    added_stances = self.stances_possible_list.curselection()

    for stance_id in added_stances:
      if len(self.stances_known_list.get(0, END)) == self.character_stats['stances_known']:
        tkMessageBox.showerror("Max Known Stances Reached",
          "You can't know any more stances at your level!")
        break
      stance_name = self.stances_possible_list.get(stance_id)
      self.stances_known_list.insert(END, stance_name)
      self.maneuver_types_learned[maneuver_descriptions[stance_name]['school']] += 1

    self.update_maneuvers_and_stances_possible(self.character_stats['level'])

  def remove_stance(self):
    removed_stances = map(int, self.stances_known_list.curselection())
    removed_stances.sort(reverse=True)

    for stance_id in removed_stances:
      self.stances_known_list.delete(stance_id)

    self.update_maneuvers_and_stances_possible(self.character_stats['level'])

  def ready_maneuvers(self):
    self.maneuvers_known = list(self.maneuvers_known_list.get(0, END))

    if len(self.maneuvers_known) < self.character_stats['maneuvers_known']:
      remaining = self.character_stats['maneuvers_known'] - len(self.maneuvers_known)
      tkMessageBox.showerror('Missing maneuvers!',
        "You need to select %s more maneuvers!" % remaining)
      del self.maneuvers_known[:]
      return

    for maneuver in self.maneuvers_known:
      self.maneuvers_readied_list.insert(END, maneuver)

    self.maneuver_select_frame.grid_forget()
    self.maneuver_ready_frame.grid(row=0)

  def start_encounter(self):
    del self.maneuvers_readied[:]
    del self.maneuvers_granted[:]
    for maneuver_id in self.maneuvers_readied_list.curselection():
      self.maneuvers_readied.append(self.maneuvers_readied_list.get(maneuver_id))
    total_granted = self.character_stats['maneuvers_granted']
    total_readied = self.character_stats['maneuvers_readied']

    if len(self.maneuvers_readied) < total_readied:
      remaining = total_readied
      tkMessageBox.showerror('Missing maneuvers!',
        "You need to select %s more manuevers to ready!" % remaining)
      del self.maneuvers_readied[:]
      return

    if len(self.maneuvers_readied) > total_readied:
      tkMessageBox.showerror('Too many manuevers!',
        "You can only ready %s manuevers!" % total_readied)
      del self.maneuvers_readied[:]
      return

    while len(self.maneuvers_granted) < total_granted:
      rolled_manuever = randint(0, len(self.maneuvers_readied) - 1)
      if self.maneuvers_readied[rolled_manuever] in self.maneuvers_granted:
        continue
      self.maneuvers_granted.append(self.maneuvers_readied[rolled_manuever])
      self.maneuvers_granted_list.insert(END,
        self.maneuvers_readied[rolled_manuever])

    self.maneuver_ready_frame.grid_forget()
    self.encounter_frame.grid(row=0)

  def show_maneuver_info(self):
    maneuver_id = self.maneuvers_granted_list.curselection()
    maneuver_name = self.maneuvers_granted_list.get(int(maneuver_id[0]))
    tkMessageBox.showinfo("Manuever details", "%s\n%s" % (maneuver_name, 
      maneuver_descriptions[maneuver_name]['description']))

  def use_maneuver(self):
    maneuver_id = self.maneuvers_granted_list.curselection()
    self.maneuvers_granted_list.delete(int(maneuver_id[0]))

  def next_round(self):
    if len(self.maneuvers_granted) == len(self.maneuvers_readied):
      self.maneuvers_granted_list.delete(0, END)
      del self.maneuvers_granted[:]
      total_granted = self.character_stats['maneuvers_granted']
      while len(self.maneuvers_granted) < total_granted:
        rolled_manuever = randint(0, len(self.maneuvers_readied) - 1)
        if self.maneuvers_readied[rolled_manuever] in self.maneuvers_granted:
          continue
        self.maneuvers_granted.append(self.maneuvers_readied[rolled_manuever])
        self.maneuvers_granted_list.insert(END,
          self.maneuvers_readied[rolled_manuever])
      return

    while True:
      rolled_manuever = randint(0, len(self.maneuvers_readied) - 1)
      if self.maneuvers_readied[rolled_manuever] in self.maneuvers_granted:
        continue
      self.maneuvers_granted.append(self.maneuvers_readied[rolled_manuever])
      self.maneuvers_granted_list.insert(END,
        self.maneuvers_readied[rolled_manuever])
      break

  def end_combat(self):
    self.maneuvers_granted_list.delete(0, END)
    self.encounter_frame.grid_forget()
    self.maneuver_ready_frame.grid(row=1)


  ##################################################################################
  #                               Utility methods                                  #
  ##################################################################################

  def update_maneuvers_and_stances_possible(self, character_level):
    self.maneuvers_possible_list.delete(0, END)
    for maneuver_name in self.get_current_possible_maneuvers(character_level):
      self.maneuvers_possible_list.insert(END, maneuver_name)


    self.stances_possible_list.delete(0, END)
    for stance_name in self.get_current_possible_stances(character_level):
      self.stances_possible_list.insert(END, stance_name)

  def get_current_possible_maneuvers(self, character_level):
    possible_maneuvers = []
    for maneuver_name in maneuver_descriptions.keys():
      maneuver_stats = maneuver_descriptions[maneuver_name]
      if 'stance' in maneuver_stats:
        continue
      if maneuver_stats['prereq']:
        if self.maneuver_types_learned[maneuver_stats['school']] < maneuver_stats['prereq']:
          continue
      if character_level < maneuver_stats['level']:
        continue
      maneuvers_known = self.maneuvers_known_list.get(0, END)
      if maneuver_name in maneuvers_known:
        continue
      possible_maneuvers.append(maneuver_name)

    return sorted(possible_maneuvers)

  def get_current_possible_stances(self, character_level):
    possible_stances = []
    for stance_name in maneuver_descriptions.keys():
      stance_stats = maneuver_descriptions[stance_name]
      if 'stance' not in stance_stats:
        continue
      if stance_stats['prereq']:
        if self.maneuver_types_learned[stance_stats['school']] < stance_stats['prereq']:
          continue
      if character_level < stance_stats['level']:
        continue
      stances_known = self.stances_known_list.get(0, END)
      if stance_name in stances_known:
        continue
      possible_stances.append(stance_name)

    return sorted(possible_stances)



root = Tk()
root.title('Crusader Maneuver Roller')
root.geometry('+0+0')
root.configure(background='misty rose')


app = CrusaderManeuverApp(root)

root.mainloop()