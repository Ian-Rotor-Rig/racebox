from aifc import _aifc_params
from datetime import datetime
import json
import os
from tkinter import (ALL, BOTH, BOTTOM, CENTER, END, LEFT, NW, RIGHT, TOP, E, W, X, Y,
    Canvas, Frame, Label, LabelFrame, Scrollbar, StringVar, ttk)
import tkinter as tk
from rbconfig import RaceboxConfig

class FinishTimesInterface:
    
    TITLE_FONT = 'Helvetica 12 bold'
    FIXED_FONT = 'Monospace 12'
    
    def __init__(self, fControl: ttk.Frame, relay):
        self.pos = 1
        self.finishList = []
        self.relay = relay
        self.config = RaceboxConfig()
        
        #get the list of classes
        with open('classes.json') as jsonFile:
            self.classList = json.load(jsonFile)
        self.classNames = []
        for c in self.classList:
            self.classNames.append(c['name'])
            
        #the list of status codes
        self.statusCodes = ['', 'RET', 'OCS', 'DSQ', 'DNF', 'Other']
                
        #finish data
        self.finishData = []
        
        self.fc = fControl
        
        f = Frame(self.fc)
        f.pack(expand=True, fill=BOTH)
        
        #left frame (for results)
        lf = Frame(f, padx=5, pady=10)
        lf.pack(side=LEFT, fill=BOTH, expand=True)
        
        #header for race details
        self.raceDetailsFrame = Frame(lf)
        self.raceDetailsFrame.pack(anchor=W)
        raceNameFrame = Frame(self.raceDetailsFrame)
        raceNameFrame.pack(pady=(2,12))
        lraceName = Label(raceNameFrame, text='Race name')
        lraceName.pack(side=LEFT, anchor=W)
        self.raceNameValue = StringVar()
        enRaceName = ttk.Entry(raceNameFrame, textvariable=self.raceNameValue)
        enRaceName.pack(side=LEFT, anchor=W)
        lraceTimesTitle = Label(self.raceDetailsFrame, text='Finish Times', font=FinishTimesInterface.TITLE_FONT)
        lraceTimesTitle.pack(anchor=W, pady=(2,4))
        
        #canvas for scrollable finish times
        self.canvas = Canvas(lf, highlightthickness=0)
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
        
        #finish times header
        self.__addFinishHdrRow()
        
    def finishAction(self):
        on2Off = float(self.config.get('Signals', 'finishOn2Off'))
        self.relay.onoff(self.fc, on2Off)
        self.__addFinishRow(on2Off)
        
    def __addFinishHeader(self):
        pass
        
    def __addFinishRow(self, on2Off):
        if self.pos == 1: self.__addFinishHdrRow()
        self.relay.onoff(self.fc, on2Off)
        now = datetime.now()

        #finish data for this row
        finishRow = {
            'pos': str(self.pos),
            'clock': {'hh': now.hour, 'mm': now.minute, 'ss': now.second, 'ms': now.microsecond},
            'class': StringVar(),
            'sailnum': StringVar(), #the interface uses a string
            'race': StringVar(),
            'status': StringVar(),
            'notes': StringVar()
        }
        self.finishData.append(finishRow)
        finishRow['race'].set('1')
        
        #draw the interface
        yPad = 2
        txtPos = '{:>3}'.format(self.pos)
        lPos = Label(self.rowFrame, text=txtPos, font=FinishTimesInterface.FIXED_FONT)
        lPos.grid(row=self.pos, column=0, pady=yPad)
        lTime = Label(self.rowFrame, text='  {} '.format(now.strftime('%H:%M:%S')), font=FinishTimesInterface.FIXED_FONT)
        lTime.grid(row=self.pos, column=1, pady=yPad)
        cbClass = ttk.Combobox(self.rowFrame, values=self.classNames, textvariable=finishRow['class'], width=14)
        cbClass.grid(row=self.pos, column=2, padx=5, pady=yPad)
        validateNumbers = (self.rowFrame.register(self.__onlyNumbers), '%S')
        enSailNum = ttk.Entry(self.rowFrame, validate='key', validatecommand=validateNumbers, textvariable=finishRow['sailnum'], width=14)
        enSailNum.grid(row=self.pos, column=3, padx=5, pady=yPad)
        enRaceNum = ttk.Entry(self.rowFrame, validate='key', validatecommand=validateNumbers, textvariable=finishRow['race'], width=4)
        enRaceNum.grid(row=self.pos, column=4, padx=5, pady=yPad)
        cbStatus = ttk.Combobox(self.rowFrame, values=self.statusCodes, textvariable=finishRow['status'], state='readonly', width=8)
        cbStatus.grid(row=self.pos, column=5, padx=5, pady=yPad)
        enNotes = ttk.Entry(self.rowFrame, textvariable=finishRow['notes'], width=25)
        enNotes.grid(row=self.pos, column=6,padx=5, pady=yPad)
        #scroll down
        self.canvas.update()
        self.canvas.yview_moveto(1.0)        
        #increment finish pos
        self.pos += 1
        
    def __addFinishHdrRow(self):
        fileHdr = [['#', E], ['Clock', E+W], ['Class', W], ['Sail Number', W], ['Race', W], ['Status', W], ['Notes', W]]
        for i,h in enumerate(fileHdr):
            l = Label(self.rowFrame, text=h[0])
            l.grid(row=0, column=i, sticky=h[1], ipadx=4 if h[1] == W else 0)
        
    def __onlyNumbers(self, k):
        if k in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']: return True
        return False
        
    def resetCounterAction(self):
        for c in self.rowFrame.winfo_children():
            c.destroy()
        self.pos = 1
        self.__addFinishHdrRow()
        self.raceNameValue.set('')
        
    def saveToTxtFileAction(self):
        now = datetime.now()
        useDefaultFolder = True if self.config.get('Files', 'finshFileUseDefaultFolder').lower() == 'true' else False
        defaultFolder = os.path.expanduser('~') if useDefaultFolder else ''
        saveFileName = self.config.get('Files','finishFileFolder') + 'finishes-{}.txt'.format(now.strftime('%Y%m%d-%H%M'))
        fileHdr = 'Pos, Clock, Class, Sail, Rating, Race, Status, Notes\n'
        #maybe need to add in a race name etc?
        try:
            with open (defaultFolder + saveFileName, 'w+') as file:
                if len(self.raceNameValue.get()) > 0: file.write(self.raceNameValue.get() + '\n')
                file.write(fileHdr)
                for f in self.finishData:
                    rating = ''
                    for c in self.classList:
                        if c['name'].lower().strip() == f['class'].get().lower().strip():
                            rating = str(c['rating'])
                    lineOut = '{}, {:02}:{:02}:{:02}, {}, {}, {}, {}, {}, {}\n'.format(
                            f['pos'], f['clock']['hh'],f['clock']['mm'],f['clock']['ss'],
                            f['class'].get(), f['sailnum'].get(), rating, f['race'].get(), f['status'].get(), f['notes'].get()
                        )
                    file.write(lineOut)
                tk.messagebox.showinfo('Save File', 'File {}{} saved'.format(defaultFolder, saveFileName))
        except Exception as error:
            tk.messagebox.showerror('Save File Error', 'Could not save the file {}{} - {}'.format(defaultFolder, saveFileName, error))
