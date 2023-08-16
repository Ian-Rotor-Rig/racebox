from datetime import datetime
import os
from tkinter import ALL, BOTH, BOTTOM, CENTER, END, LEFT, NW, RIGHT, TOP, E, W, X, Y, Canvas, Frame, Label, LabelFrame, Scrollbar, ttk
import tkinter as tk
from rbconfig import RaceboxConfig

class FinishTimesInterface:
    def __init__(self, fControl: ttk.Frame, relay):
        self.pos = 1
        self.finishList = []
        self.relay = relay
        self.config = RaceboxConfig()
        
        self.fc = fControl
        
        f = Frame(self.fc)
        f.pack(expand=True, fill=BOTH)
        
        #left frame (for results)
        lf = Frame(f, padx=5, pady=10)
        lf.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.canvas = Canvas(lf)
        sb = Scrollbar(lf, orient='vertical', command=self.canvas.yview)
        self.finishFrame = Frame(self.canvas) #do not pack this
        cw = self.canvas.create_window((0, 0), window=self.finishFrame, anchor=NW)
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        sb.pack(side=RIGHT, fill=Y)        
        self.finishFrame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox(ALL)))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(cw, width=e.width))
        
        #left-side internal frame for rows of times
        self.rowFrame = Frame(self.finishFrame)
        self.rowFrame.pack(fill=X, expand=True)
                
        #right frame (for the buttons etc)
        rf = Frame(f)
        rf.pack(side=LEFT, ipadx=10, padx=25, fill=Y)

        #finish button
        btnFinish = ttk.Button(rf, text="Finish", command=self.finishAction, style='Custom.TButton')
        btnFinish.pack(side=TOP, anchor=W, pady=50)

        #right bottom frame (reset and save)
        rbf = LabelFrame(rf, text='Use Between Races')
        rbf.pack(side=BOTTOM, anchor=W, pady=25, ipady=25)
        #save as file button
        btnReset = ttk.Button(rbf, text="Save Finishes", command=self.saveToTxtFileAction, style='Custom.TButton')
        btnReset.pack(expand=True, anchor=CENTER)          
        #reset counter button
        btnReset = ttk.Button(rbf, text="Reset Finish Box", command=self.resetCounterAction, style='Custom.TButton')
        btnReset.pack(expand=True, anchor=CENTER)  
          
    def finishAction(self):
        on2Off = float(self.config.get('Signals', 'finishOn2Off'))
        self.relay.onoff(on2Off)
        self.__addFinishRow(on2Off)
        
    def __addFinishRow(self, on2Off):
        if self.pos == 1: self.__addFinishHdrRow()
        self.relay.onoff(self.fc, on2Off)
        now = datetime.now()
        yPad = 2
        txtPos = '{:>3}'.format(self.pos)
        lPos = Label(self.rowFrame, text=txtPos, font='TkFixedFont')
        lPos.grid(row=self.pos, column=0, pady=yPad)
        lTime = Label(self.rowFrame, text='  {} '.format(now.strftime('%H:%M:%S')), font='TkFixedFont', width=12)
        lTime.grid(row=self.pos, column=1, pady=yPad)
        cbClass = ttk.Combobox(self.rowFrame, values=['Solo', 'RS200', 'Laser'], width=14)
        cbClass.grid(row=self.pos, column=2, padx=5, pady=yPad)
        validateNumbers = (self.rowFrame.register(self.__onlyNumbers), '%S')
        enSailNum = ttk.Entry(self.rowFrame, validate='key', validatecommand=validateNumbers, width=14)
        enSailNum.grid(row=self.pos, column=3, padx=5, pady=yPad)
        enRaceNum = ttk.Entry(self.rowFrame, validate='key', validatecommand=validateNumbers, width=4)
        enRaceNum.grid(row=self.pos, column=4, padx=5, pady=yPad)
        enRaceNum.insert(0, '1')
        enNotes = ttk.Entry(self.rowFrame, width=40)
        enNotes.grid(row=self.pos, column=5,padx=5, pady=yPad)
        #scroll down
        self.canvas.update()
        self.canvas.yview_moveto(1.0)        
        #increment finish pos
        self.pos += 1
        
    def __addFinishHdrRow(self):
        lPos = Label(self.rowFrame, text='#')
        lPos.grid(row=0, column=0, sticky=E)
        lTime = Label(self.rowFrame, text='Clock')
        lTime.grid(row=0, column=1)
        lClass = Label(self.rowFrame, text='Class')
        lClass.grid(row=0, column=2, sticky=W, padx=5, ipadx=2)
        lSailNum = Label(self.rowFrame, text='Sail Number')
        lSailNum.grid(row=0, column=3, sticky=W, padx=5, ipadx=2)
        lRaceNum = Label(self.rowFrame, text='Race')
        lRaceNum.grid(row=0, column=4, sticky=W, padx=5, ipadx=2)
        lNotes = Label(self.rowFrame, text='Notes')
        lNotes.grid(row=0, column=5, sticky=W, padx=5, ipadx=2)
        
    def __onlyNumbers(self, k):
        if k in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']: return True
        return False
        
    def resetCounterAction(self):
        ####self.txtboxFinish.delete('1.0', END)
        self.pos = 1
        
    def saveToTxtFileAction(self):
        now = datetime.now()
        useDefaultFolder = True if self.config.get('Files', 'finshFileUseDefaultFolder').lower() == 'true' else False
        defaultFolder = os.path.expanduser('~') if useDefaultFolder else ''
        saveFileName = self.config.get('Files','finishFileFolder') + 'finishes-{}.txt'.format(now.strftime('%Y%m%d-%H%M'))
        try:
            with open (defaultFolder + saveFileName, 'w+') as file:
                ####file.write(self.txtboxFinish.get('1.0', END))
                file.close()
                tk.messagebox.showinfo('Save File', 'File {}{} saved'.format(defaultFolder, saveFileName))
        except:
            tk.messagebox.showerror('Save File Error', 'Could not save the file {}{}'.format(defaultFolder, saveFileName))
