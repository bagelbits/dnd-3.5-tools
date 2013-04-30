from Tkinter import *
from random import randint
import tkFileDialog
import tkMessageBox
import xml.etree.ElementTree as ET
import re


class colorz:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


class SkillCheckApp:
    skill_table = {}
    button_to_mod = {}

    def __init__(self, master):
        self.master = master

        #Initializing frames
        self.file_loader_frame = Frame(master, background='misty rose')
        self.file_loader_frame.grid(row=0)
        self.skill_roller_frame = Frame(master, background='misty rose')
        self.skill_roll_button_frame = Frame(master, background='misty rose')

        self.roll_result_frame = Frame(master, background='misty rose')
        self.reroll_button_frame = Frame(master, background='misty rose')
        separator = Frame(height=2, width=350, bd=1, relief=SUNKEN)
        separator.grid(row=9)
        self.exit_frame = Frame(master, background='misty rose')
        self.exit_frame.grid(row=10)

        self.file_loader_setup()
        self.skill_roller_setup()
        self.skill_roll_button_setup()
        self.roll_result_setup()
        self.reroll_button_setup()

        self.exit_setup()

    def file_loader_setup(self):
        Label(self.file_loader_frame, text="Character Name:",
              background='misty rose').grid(row=0)
        self.path_to_xml = Entry(self.file_loader_frame,
                                highlightbackground='misty rose', width=20)
        self.path_to_xml.grid(row=0, column=1)
        browse_button = Button(self.file_loader_frame,
                               text="Browse...",
                               command=self.loadtemplate,
                               background='misty rose',
                               highlightbackground='misty rose')
        browse_button.grid(row=0, column=2)
        load_xml_button = Button(self.file_loader_frame,
                                 text="Load!",
                                 command=lambda: self.skill_grabber(self.path_to_xml.get()),
                                 background='misty rose',
                                 highlightbackground='misty rose')
        load_xml_button.grid(row=1, column=1)

    def skill_roller_setup(self):
        Label(self.skill_roller_frame, text="Select skills to roll:",
              background='misty rose').pack()
        skill_scroll = Scrollbar(self.skill_roller_frame)
        self.skill_box = Listbox(self.skill_roller_frame, selectmode=MULTIPLE,
                                 height=20, width=40,
                                 highlightbackground='misty rose',
                                 exportselection=0)
        skill_scroll.config(command=self.skill_box.yview)
        self.skill_box.config(yscrollcommand=skill_scroll.set)
        self.skill_box.pack(side=LEFT)
        skill_scroll.pack(side=LEFT, fill=Y)

    def skill_roll_button_setup(self):
        skill_roll_button = Button(self.skill_roll_button_frame,
                                   text="ROLL!",
                                   command=lambda: self.general_skill_roll(),
                                   background='misty rose',
                                   highlightbackground='misty rose',
                                   fg="red")
        skill_roll_button.pack()

    def roll_result_setup(self):
        Label(self.roll_result_frame, text="Result log:",
              background='misty rose').pack()
        result_scroll = Scrollbar(self.roll_result_frame)
        self.result_box = Text(self.roll_result_frame,
                            height=20, width=40,
                            highlightbackground='misty rose')
        result_scroll.config(command=self.result_box.yview)
        self.result_box.config(yscrollcommand=result_scroll.set)
        self.result_box.pack(side=LEFT)
        result_scroll.pack(side=LEFT, fill=Y)

    def reroll_button_setup(self):
        pick_again_button = Button(self.reroll_button_frame,
                                   text="Pick new skill",
                                   command=lambda: self.pick_new_skills(),
                                   background='misty rose',
                                   highlightbackground='misty rose')
        reroll_button = Button(self.reroll_button_frame,
                               text="REROLL!",
                               command=lambda: self.general_skill_roll(),
                               background='misty rose',
                               highlightbackground='misty rose',
                               fg="red")
        pick_again_button.grid(row="0")
        reroll_button.grid(row="0", column="1")

    def exit_setup(self):
        reset_button = Button(self.exit_frame,
                                 text="Reset",
                                 command=self.reset,
                                 background='misty rose',
                                 highlightbackground='misty rose')
        reset_button.grid(row=0, column=0)
        quit_button = Button(self.exit_frame,
                                 text="Quit",
                                 command=self.exit_frame.quit,
                                 background='misty rose',
                                 highlightbackground='misty rose')
        quit_button.grid(row=0, column=1)

    def pick_new_skills(self):
        self.skill_box.selection_clear(0, END)
        self.skill_roller_frame.grid(row=0)
        self.skill_roll_button_frame.grid(row=1)
        self.result_box.delete('1.0', END)
        self.roll_result_frame.grid_forget()
        self.reroll_button_frame.grid_forget()

    def reset(self):
        self.path_to_xml.delete(0, END)
        self.file_loader_frame.grid(row=0)
        self.skill_roll_button_frame.grid_forget()
        self.skill_box.delete(0, END)
        self.skill_roller_frame.grid_forget()
        self.result_box.delete('1.0', END)
        self.roll_result_frame.grid_forget()
        self.reroll_button_frame.grid_forget()

    def loadtemplate(self):
        filename = tkFileDialog.askopenfilename(filetypes=(
                                                ("XML files", "*.xml"),
                                                ("All files", "*.*")))
        if filename:
            try:
                self.path_to_xml.delete(0, END)
                self.path_to_xml.insert(0, filename)
            except:
                tkMessageBox.showerror("Open Source File",
                    "Failed to read file \n'%s'" % filename)
                return

################
# Dice rollers #
################

    def roll_dice(self, dice=1, sides=6):
        try:
            return [randint(1, sides) for x in range(dice)]
        except:
            return []

    def general_skill_roll(self):
        self.result_box.delete('1.0', END)

        skills_to_roll = []
        for skill in self.skill_box.curselection():
            skills_to_roll.append(self.skill_box.get(skill))

        for skill_roll in skills_to_roll:
            total_dc_roll = 0
            total_mod = self.skill_table[skill_roll]

            self.result_box.insert(END, "Skill: %s\n" % (skill_roll, ))

            self.result_box.insert(END, "Roll: 1d20 + %d\n" % (total_mod, ))

            base_dc_roll = sum(self.roll_dice(1, 20))

            self.result_box.insert(END, "Base roll: %d\n" % (base_dc_roll, ))

            #EXPLODING DICE
            while base_dc_roll == 20:
                total_mod += base_dc_roll
                self.result_box.insert(END, "\nExploding dice! Roll again\n\n")
                self.result_box.insert(END, "Roll: 1d20 + %d\n" % (total_mod, ))

                base_dc_roll = sum(self.roll_dice(1, 20))

                self.result_box.insert(END, "Base roll: %d\n" % (base_dc_roll, ))

            if base_dc_roll == 1:
                self.result_box.insert(END, "\nCritical Failure!\n\n")

            total_dc_roll += total_mod + base_dc_roll
            self.result_box.insert(END, "Total roll result: %d\n\n" % (total_dc_roll, ))

        self.skill_roller_frame.grid_forget()
        self.skill_roll_button_frame.grid_forget()
        self.roll_result_frame.grid(row=0)
        self.reroll_button_frame.grid(row=1)

########################
# Grab skills from XML #
########################

    def skill_grabber(self, path_to_xml):
        xml_skill_table = {}
        xml_file_name = path_to_xml
        tree = ET.parse(xml_file_name)
        root = tree.getroot()
        for node in root.findall("./data/node"):
            if node.attrib['name'].startswith("Skill"):
                result = re.match("Skill(\d\d)(.*)$", node.attrib['name'])
                if not result.group(2):
                    xml_skill_table[int(result.group(1))] = {'name': node.text}
                else:
                    xml_skill_table[int(result.group(1))][result.group(2)] = node.text

        for key in sorted(xml_skill_table):
            self.skill_table[xml_skill_table[key]['name']] \
                = int(xml_skill_table[key]['Mod'])
        self.file_loader_frame.grid_forget()

        for skill_name in sorted(self.skill_table):
            self.skill_box.insert(END, skill_name)

        self.skill_roller_frame.grid(row=0)
        self.skill_roll_button_frame.grid(row=1)
        self.master.update_idletasks()


root = Tk()
root.title('Skill Check Roller')
root.geometry('+0+0')
root.configure(background='misty rose')

app = SkillCheckApp(root)

root.mainloop()
