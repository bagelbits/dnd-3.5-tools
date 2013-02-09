from Tkinter import *
import tkMessageBox
import sys
import os
import threading
import random
import acr_unicorn
import acr_SQLsetup
from decimal import *
from PIL import Image, ImageTk


###############################################################################
# GIF loading
###############################################################################

class Gif(Label):
    def __init__(self, master, filename):
        evanGif = Image.open(filename)
        gifSeq = []
        try:
            while 1:
                gifSeq.append(evanGif.copy())
                evanGif.seek(len(gifSeq))  # skip to next frame
        except EOFError:
            pass  # We're done
        try:
            #Special case for the evangalion gif
            if evanGif.info['duration'] == 0:
                self.delay = 80
                self.startdelay = 80
            else:
                if filename == 'images/odkRx.gif':
                    self.startdelay = 2500
                    self.delay = 80
                else:
                    self.delay = evanGif.info['duration']
                    self.startdelay = self.delay
        except KeyError:
            self.delay = 100
        gifFirst = gifSeq[0].convert('RGBA')
        self.gifFrames = [ImageTk.PhotoImage(gifFirst)]

        Label.__init__(self, master, image=self.gifFrames[0])

        temp = gifSeq[0]
        for image in gifSeq[1:]:
            temp.paste(image, image.convert('RGBA'))
            frame = temp.convert('RGBA')
            self.gifFrames.append(ImageTk.PhotoImage(frame))

        self.gifIdx = 0
        self.cancel = self.after(self.delay, self.play)

    def play(self):
        self.config(image=self.gifFrames[self.gifIdx])
        self.gifIdx += 1
        if self.gifIdx == len(self.gifFrames):
            self.gifIdx = 0
            self.after(self.startdelay, self.play)
        else:
            self.cancel = self.after(self.delay, self.play)


###############################################################################
#
###############################################################################
class App:
    def __init__(self, master):
        self.master = master

        #Initializing frames
        self.logoFrame = Frame(master, background='misty rose')
        self.logoFrame.grid(row=0)
        self.dateFrame = Frame(master, background='misty rose')
        self.dateFrame.grid(row=1)
        self.apSelectFrame = Frame(master, background='misty rose')
        self.apSelectFrame.grid(row=2)
        self.clientFrame = Frame(master, background='misty rose')
        #self.clientFrame.grid(row=3)
        self.pubFrame = Frame(master, background='misty rose')
        #self.pubFrame.grid(row=4)
        self.buttonFrame = Frame(master, background='misty rose')
        self.buttonFrame.grid(row=5)
        self.loadingFrame = Frame(master, background='misty rose')
        #self.loadingFrame.grid(row=6)
        self.loadGIF = Gif(self.loadingFrame, self.randGif()).pack()

        self.logoSetup()
        self.dateSetup()
        self.reportSetup()
        self.pubSetup()
        self.clientSetup()
        self.buttonSetup()

    def randGif(self):
        imgNum = random.randint(1, 7)
        if imgNum == 1:
            return 'images/Others/4Y9UJ.gif'
        elif imgNum == 2:
            return 'images/Others/odkRx.gif'
        elif imgNum == 3:
            return 'images/Others/Q6CBO.gif'
        elif imgNum == 4:
            return 'images/Others/nyanex.gif'
        elif imgNum == 5:
            return 'images/record.gif'
        else:
            return 'images/Others/nyan.gif'

    def logoSetup(self):
        #Logo
        acrLogo = PhotoImage(file="images/cc_logo.gif")
        acrLogoLabel = Label(self.logoFrame, image=acrLogo,
                             background='misty rose')
        acrLogoLabel.acrLogo = acrLogo
        acrLogoLabel.pack()

    def dateSetup(self):
        #Date
        Label(self.dateFrame, text="Start Month:",
              background='misty rose').grid(row=0)
        self.startMonth = Entry(self.dateFrame,
                                highlightbackground='misty rose', width=2)
        self.startMonth.grid(row=0, column=1)
        Label(self.dateFrame, text="Start Year:",
              background='misty rose').grid(row=1)
        self.startYear = Entry(self.dateFrame,
                                highlightbackground='misty rose', width=4)
        self.startYear.grid(row=1, column=1)
        Label(self.dateFrame, text="End Month:",
              background='misty rose').grid(row=2)
        self.endMonth = Entry(self.dateFrame, highlightbackground='misty rose',
                        width=2)
        self.endMonth.grid(row=2, column=1)
        Label(self.dateFrame, text="End Year:",
              background='misty rose').grid(row=3)
        self.endYear = Entry(self.dateFrame, highlightbackground='misty rose',
                            width=4)
        self.endYear.grid(row=3, column=1)

    def reportSetup(self):
        #Report Type
        Label(self.apSelectFrame, text="Select Report Type:",
              background='misty rose').grid(row=0)
        self.apSelect = Listbox(self.apSelectFrame, selectmode=SINGLE,
                                height=3, highlightbackground='misty rose',
                                exportselection=0)
        self.apSelect.bind('<<ListboxSelect>>', self.apSelectCallback)
        self.apSelect.grid(row=1)
        for item in ["Artists", "Publishers", "Both"]:
            self.apSelect.insert(END, item)
        self.allTheThings = IntVar()
        self.checkAll = Checkbutton(self.apSelectFrame, text="All?",
                                    variable=self.allTheThings,
                                    background='misty rose',
                                    highlightbackground='misty rose',
                                    command=self.hideBoxes)
        self.checkAll.grid(row=1, column=1)

    def clientSetup(self):
        #Client names
        self.clientLabel = Label(self.clientFrame, text="Select Clients:",
                                 background='misty rose').pack()
        self.clientscroll = Scrollbar(self.clientFrame)
        self.clientbox = Listbox(self.clientFrame, selectmode=MULTIPLE,
                                 height=10, width=40,
                                 highlightbackground='misty rose',
                                 exportselection=0)
        self.clientscroll.config(command=self.clientbox.yview)
        self.clientbox.config(yscrollcommand=self.clientscroll.set)
        self.clientbox.pack(side=LEFT)
        self.clientscroll.pack(side=LEFT, fill=Y)
        acrDB = acr_SQLsetup.ACR_DB_SETUP()
        dbCurs = acrDB.assumeDirectControl()
        dbCurs.execute("SELECT name FROM clients")
        client_sorted = dbCurs.fetchall()
        for x in range(len(client_sorted)):
            client_sorted[x] = client_sorted[x][0]
        client_sorted.sort()
        for item in client_sorted:
            self.clientbox.insert(END, item)

    def pubSetup(self):
        #Publisher names
        self.pubLabel = Label(self.pubFrame, text="Select Publishers:",
                              background='misty rose').pack()
        self.pubscroll = Scrollbar(self.pubFrame)
        self.pubbox = Listbox(self.pubFrame, selectmode=MULTIPLE, height=10,
                              width=40, highlightbackground='misty rose',
                              exportselection=0)
        self.pubscroll.config(command=self.pubbox.yview)
        self.pubbox.config(yscrollcommand=self.pubscroll.set)
        self.pubbox.pack(side=LEFT)
        self.pubscroll.pack(side=LEFT, fill=Y)
        acrDB = acr_SQLsetup.ACR_DB_SETUP()
        dbCurs = acrDB.assumeDirectControl()
        dbCurs.execute("SELECT name FROM copyright_holders")
        pub_sorted = dbCurs.fetchall()
        for x in range(len(pub_sorted)):
            pub_sorted[x] = pub_sorted[x][0]
        pub_sorted.sort()
        for item in pub_sorted:
            self.pubbox.insert(END, item)

    def buttonSetup(self):
        #ALL THE BUTTONS
        self.generateBt = Button(self.buttonFrame,
                                 text="Generate!",
                                 command=self.generate,
                                 background='misty rose',
                                 highlightbackground='misty rose')
        self.generateBt.pack(side=LEFT)
        self.resetBt = Button(self.buttonFrame, text="Reset!",
                              command=self.reset, background='misty rose',
                              highlightbackground='misty rose')
        self.resetBt.pack(side=LEFT)
        self.quitBt = Button(self.buttonFrame, text="Quit!", fg="red",
                             command=self.buttonFrame.quit,
                             background='misty rose',
                             highlightbackground='misty rose')
        self.quitBt.pack(side=LEFT)

    def hideBoxes(self):
        self.pubFrame.grid_forget()
        self.clientFrame.grid_forget()
        self.checkAll.config(command=self.showBoxes)

    def showBoxes(self):
        self.apSelectCallback('<<ListboxSelect>>')
        self.checkAll.config(command=self.hideBoxes)

    def apSelectCallback(self, event):
        select = '-1'
        if not self.apSelect.curselection() == ():
            select = self.apSelect.curselection()[0]
        if select == '0':
            self.pubFrame.grid_forget()
            self.clientFrame.grid(row=3)
        if select == '1':
            self.clientFrame.grid_forget()
            self.pubFrame.grid(row=4)
        if select == '2':
            self.clientFrame.grid(row=3)
            self.pubFrame.grid(row=4)

    def fileChecker(self, filename):
        if(not os.path.isfile(filename)):
            return False
        return True

    def checkForFiles(self, srDates):
        errorReport = []
        if not self.fileChecker("tables/ACR.db"):
            print "Please run acr_srgen.py first."
            sys.exit()
        acrDB = acr_SQLsetup.ACR_DB_SETUP()
        dbCurs = acrDB.assumeDirectControl()
        for date in srDates:
            dbCurs.execute("SELECT * FROM sales \
                            WHERE date = ? LIMIT 1", (date, ))
            found = dbCurs.fetchone()
            if not found:
                errorReport.append("Please run acr_srgen.py for the date: "
                    + date + "\n")
        dbCurs.close()
        errorReport = filter(None, errorReport)
        if errorReport != []:
                tkMessageBox.showerror("Error", "\n".join(errorReport))
                return False
        else:
            return True

    def folderSetup(self, startDate, endDate):
        srDates = []
        if(not os.path.exists('reports/' + ".".join(startDate) + "-"
                + ".".join(endDate) + '/artists/empty')):

            os.makedirs('reports/' + ".".join(startDate) + "-"
                + ".".join(endDate) + '/artists/empty')

        if(not os.path.exists('reports/' + ".".join(startDate) + "-"
                + ".".join(endDate) + '/artists/mm')):

            os.makedirs('reports/' + ".".join(startDate) + "-"
                + ".".join(endDate) + '/artists/mm')

        if(not os.path.exists('reports/' + ".".join(startDate) + "-"
                + ".".join(endDate) + '/publishers/empty')):

            os.makedirs('reports/' + ".".join(startDate) + "-"
                + ".".join(endDate) + '/publishers/empty')

        startMonth, startYear = startDate
        endMonth, endYear = endDate
        startMonth = int(startMonth)
        startYear = int(startYear)
        endMonth = int(endMonth)
        endYear = int(endYear)
        while(startYear < endYear):
            for mon in range(startMonth, 13):
                srDates.append(str(mon).zfill(2) + "_" + str(startYear))
            startMonth = 1
            startYear += 1
        for mon in range(startMonth, endMonth + 1):
            srDates.append(str(mon).zfill(2) + "_" + str(startYear))
        return srDates

    def inputCheck(self, startDate, endDate, report_type, allTheThings,
                    clnames, pubnames):
        if len(startDate[0]) == 0:
            tkMessageBox.showerror("Error",
                "You forgot to enter a start month!")
            return False
        if len(startDate[1]) == 0:
            tkMessageBox.showerror("Error",
                "You forgot to enter a start year!")
            return False
        if len(endDate[0]) == 0:
            tkMessageBox.showerror("Error",
                "You forgot to enter a end month!")
            return False
        if len(endDate[1]) == 0:
            tkMessageBox.showerror("Error",
                "You forgot to enter a end year!")
            return False
        if len(report_type) == 0:
            tkMessageBox.showerror("Error",
                "You forgot to select a report type!")
            return False
        if report_type[0] == '0' and allTheThings == 0 and clnames == []:
            tkMessageBox.showerror("Error",
                "Either select all or enter a client name!")
            return False
        if report_type[0] == '1' and allTheThings == 0 and pubnames == []:
            tkMessageBox.showerror("Error",
                "Either select all or enter publisher name!")
            return False
        if report_type[0] == '2' and allTheThings == 0 \
                and clnames == [] and pubnames == []:
            tkMessageBox.showerror("Error",
                "Either select all or enter a client and publisher name!")
            return False
        return True

    def generate(self):
        #TODO File checker
        startDate = []
        endDate = []
        startDate.append(self.startMonth.get().zfill(2))
        startDate.append(self.startYear.get())
        endDate.append(self.endMonth.get().zfill(2))
        endDate.append(self.endYear.get())
        cllist = self.clientbox.curselection()
        clnames = []
        publist = self.pubbox.curselection()
        pubnames = []
        srDates = self.folderSetup(startDate, endDate)
        for item in cllist:
            clnames.append(self.clientbox.get(item))
        for item in publist:
            pubnames.append(self.pubbox.get(item))
        report_type = self.apSelect.curselection()
        #report_type = '1'
        allTheThings = self.allTheThings.get()
        #allTheThings = True
        if not self.inputCheck(startDate, endDate, report_type, allTheThings,
                                clnames, pubnames):
            return
        if not self.checkForFiles(srDates):
            return
        tester = acr_unicorn.ACR_CALC()
        print clnames
        self.gen_Thread = threading.Thread(target=tester.calc,
            args=(startDate, endDate, clnames, pubnames,
                  report_type[0], allTheThings, srDates))
        self.gen_Thread.start()
        self.wait_generate()

    def wait_generate(self):
        self.hideForGen()
        self.master.update_idletasks()
        if self.gen_Thread.isAlive():
            self.master.after(500, self.wait_generate)
        else:
            tkMessageBox.showinfo("Complete", "Report generation completed!")
            self.reset()

    def hideForGen(self):
        self.logoFrame.grid_forget()
        self.dateFrame.grid_forget()
        self.apSelectFrame.grid_forget()
        self.clientFrame.grid_forget()
        self.pubFrame.grid_forget()
        self.buttonFrame.grid_forget()
        self.loadingFrame.grid(row=7)

    def reset(self):
        self.loadingFrame.grid_forget()
        self.logoFrame.grid(row=1)
        self.dateFrame.grid(row=2)
        self.apSelectFrame.grid(row=3)
        self.buttonFrame.grid(row=6)
        self.startMonth.delete(0, END)
        self.startYear.delete(0, END)
        self.endMonth.delete(0, END)
        self.endYear.delete(0, END)
        self.allTheThings.set(0)
        self.apSelect.select_clear(0, END)
        self.pubbox.select_clear(0, END)
        self.pubFrame.grid_forget()
        self.clientbox.select_clear(0, END)
        self.clientFrame.grid_forget()


root = Tk()
root.title('ACR Sales Calculator')
root.geometry('+0+0')
root.configure(background='misty rose')

app = App(root)

root.mainloop()
