from datetime import datetime
import json
import os
from tkinter import (ALL, BOTH, BOTTOM, CENTER, LEFT, NW, RIGHT, E, SW, W, X, Y,
    Canvas, Frame, Label, LabelFrame, Scrollbar, StringVar, messagebox, ttk)
import tkinter as tk
from lib.rbconfig import RaceboxConfig
from lib.rbutility import (
        STATUS_CODES,
        STATUS_FINISHED,
        getAutoSaveFileName,
        getJSONFinishData,
        saveToCSVFile,
        setJSONFinishData,
        onlyNumbers
    )

class FinishTimesInterface:
    
    TITLE_FONT = 'Helvetica 12 bold'
    FIXED_FONT = 'Courier 12'
    FIXED_FONT_BOLD = 'Courier 12 bold'
    
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
        self.statusCodes = STATUS_CODES
        self.statusCodes.insert(0, '')
                
        #finish data
        asInfo = self.__restoreFinishGridInfo()
        self.finishData = asInfo['data']
        
        self.fc = fControl
        
        f = Frame(self.fc)
        f.pack(expand=True, fill=BOTH)
          
        #left frame (for results)
        lf = Frame(f)
        lf.pack(side=LEFT, fill=BOTH, expand=True)

        self.validateNumbers = (lf.register(onlyNumbers), '%S')

        #left side lower frame for approaching boats
        abFrame = LabelFrame(lf, text='Approaching Boats', font=FinishTimesInterface.TITLE_FONT)
        abFrame.pack(side=BOTTOM, anchor=SW, ipadx=4, padx=4, pady=(16,4))
        self.__drawApproachingBoats(abFrame)
                
        #header for race details
        self.raceDetailsFrame = Frame(lf)
        self.raceDetailsFrame.pack(anchor=W, padx=10, pady=10)
        
        raceNameFrame = Frame(self.raceDetailsFrame)
        raceNameFrame.pack(pady=(2,12))
        
        lraceName = Label(raceNameFrame, text='Race name')
        lraceName.pack(side=LEFT, anchor=W)
        
        self.raceNameValue = StringVar()
        if 'name' in asInfo and len(asInfo['name']) > 0: self.raceNameValue.set(asInfo['name'])
        enRaceName = ttk.Entry(raceNameFrame, textvariable=self.raceNameValue, width=25)
        enRaceName.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        enRaceName.pack(side=LEFT, anchor=W, padx=(4,0))
        
        lracedate = Label(raceNameFrame, text='Date')
        lracedate.pack(side=LEFT, anchor=W, padx=(20,0))
        
        now = datetime.now()
        self.raceDateValue = StringVar(value=now.strftime('%d %b %Y'))            
        if 'date' in asInfo and len(asInfo['date']) > 0: self.raceDateValue.set(asInfo['date'])
        enRaceDate = ttk.Entry(raceNameFrame, textvariable=self.raceDateValue, width=12)
        enRaceDate.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        enRaceDate.pack(side=LEFT, anchor=W, padx=(4,0))
        
        lraceTimesTitle = Label(self.raceDetailsFrame, text='Finish Times', font=FinishTimesInterface.TITLE_FONT)
        lraceTimesTitle.pack(anchor=W, pady=(5,0))
        
        #canvas for scrollable finish times
        self.canvas = Canvas(lf, highlightthickness=0)
        sb = Scrollbar(lf, orient='vertical', command=self.canvas.yview)
        self.finishFrame = Frame(self.canvas) #do not pack this
        cw = self.canvas.create_window((0, 0), window=self.finishFrame, anchor=NW)
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=2)
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
        btnFinish.pack(anchor=W, pady=(50,0))

        #non finisher button
        btnReset = ttk.Button(rf, text="Non-Finisher", command=self.nonFinishAction, style='Custom.TButton')
        btnReset.pack(anchor=W, pady=(50,0))  
                
        #right bottom frame (reset and save)
        rbf = LabelFrame(rf, text='Use After Races')
        rbf.pack(side=BOTTOM, anchor=W, pady=(0,25), ipady=20, ipadx=5)
        #save as file button
        btnReset = ttk.Button(rbf, text="Save Finishes", command=self.saveToFileAction, style='Custom.TButton')
        btnReset.pack(expand=True, anchor=CENTER)          
        #reset counter button
        btnReset = ttk.Button(rbf, text="Reset Finish Box", command=self.resetFinishBoxAction, style='Custom.TButton')
        btnReset.pack(expand=True, anchor=CENTER)
        
        #finish times header        
        self.__addFinishHdr(self.rowFrame)
        
        #get the race autosave data (if any) and set up the finish times grid
        if len(asInfo['data']) > 0:
            for row in range(len(asInfo['data'])):
                self.__addFinishRow(self.rowFrame)
                if not asInfo['data'][row]['pos'] == 0: self.pos = asInfo['data'][row]['pos'] + 1
            self.__populateFinishGrid(self.rowFrame, asInfo['data'])
        
    def finishAction(self, abClass='', abSail=''):
        on2Off = float(self.config.get('Signals', 'finishOn2Off'))
        self.relay.onoff(self.fc, on2Off)
        finishData = self.__addFinishData(True, abClass, abSail)
        self.finishData.append(finishData)
        self.pos += 1
        self.autoSaveAction()
        self.__addFinishRow(self.rowFrame)
        self.__populateFinishGrid(self.rowFrame, self.finishData)
        
    def nonFinishAction(self):
        finishData = self.__addFinishData(False)
        self.finishData.append(finishData)
        self.autoSaveAction()
        self.__addFinishRow(self.rowFrame)
        self.__populateFinishGrid(self.rowFrame, self.finishData)
                
    def __addFinishData(self, finisher=True, classValue='', sailValue=''):
        now = datetime.now()
        #finish data for this row
        newFinishData = {
            'pos': self.pos if finisher else 0,
            'clock': {'hh': now.hour, 'mm': now.minute, 'ss': now.second, 'ms': now.microsecond},
            'class': StringVar(value=classValue),
            'sailnum': StringVar(value=sailValue), #the interface uses a string
            'race': StringVar(value='1'),
            'status': StringVar(),
            'notes': StringVar()
        }
        if finisher: newFinishData['status'].set('Finished')
        return newFinishData

    def __populateFinishGrid(self, f, rowData):
        rows = len(rowData)
        if rows < 1: return
        for r in range(rows):
            gridRow = rows - r #populate table in reverse order

            #pos
            cell = f.grid_slaves(row=gridRow, column=0)
            cell[0].configure(text='{:>3}'.format(rowData[r]['pos'])if rowData[r]['pos'] > 0 else '')
            
            #clock
            cell = f.grid_slaves(row=gridRow, column=1)
            cell[0].configure(text='{:02}:{:02}:{:02}'.format(rowData[r]['clock']['hh'], rowData[r]['clock']['mm'], rowData[r]['clock']['ss'])
             if rowData[r]['status'].get() == STATUS_FINISHED else '')

            #class
            cell = f.grid_slaves(row=gridRow, column=2)
            cell[0].configure(textvariable=rowData[r]['class'])

            #sail number
            cell = f.grid_slaves(row=gridRow, column=3)
            cell[0].configure(textvariable=rowData[r]['sailnum'])

            #race
            cell = f.grid_slaves(row=gridRow, column=4)
            cell[0].configure(textvariable=rowData[r]['race'])

            #status
            cell = f.grid_slaves(row=gridRow, column=5)
            cell[0].configure(textvariable=rowData[r]['status'])
            if rowData[r]['status'].get() == STATUS_FINISHED:
                cell[0].configure(state='disabled')
            else:
                cell[0].configure(state='readonly')

            #notes
            cell = f.grid_slaves(row=gridRow, column=6)
            cell[0].configure(textvariable=rowData[r]['notes'])
    
    def __addFinishRow(self, f):
        self.rowCount += 1
        rowNumber = self.rowCount
        below = 4
        right = 10
        above = 4
        
        lPos = Label(f, text='', font=FinishTimesInterface.FIXED_FONT, justify=RIGHT)
        lPos.grid(row=rowNumber, column=0, padx=(0,right), pady=(above,below))
        
        lTime = Label(f, text='', font=FinishTimesInterface.FIXED_FONT_BOLD)
        lTime.grid(row=rowNumber, column=1, padx=(0,right), pady=(above,below))
        
        cbClass = ttk.Combobox(f, values=self.classNames, width=12)
        cbClass.grid(row=rowNumber, column=2, padx=(0,right), pady=(0,below))
        cbClass.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        cbClass.bind('<<ComboboxSelected>>', lambda e: self.autoSaveAction())
              
        enSailNum = ttk.Entry(f, validate='key', validatecommand=self.validateNumbers, width=12)
        enSailNum.grid(row=rowNumber, column=3, padx=(0,right), pady=(0,below))
        enSailNum.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        
        enRaceNum = ttk.Entry(f, validate='key', validatecommand=self.validateNumbers, width=8)
        enRaceNum.grid(row=rowNumber, column=4, padx=(0,right), pady=(0,below))
        enRaceNum.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        
        cbStatus = ttk.Combobox(f, values=self.statusCodes, width=8)
        cbStatus.grid(row=rowNumber, column=5, padx=(0,right), pady=(0,below))
        cbStatus.bind('<<ComboboxSelected>>', lambda e: self.autoSaveAction())
                            
        enNotes = ttk.Entry(f, width=25)
        enNotes.grid(row=rowNumber, column=6, padx=(0,right), pady=(0,below))
        enNotes.bind('<KeyRelease>', lambda e: self.autoSaveAction())

    def __addFinishHdr(self, f):
        self.rowCount = 0
        fileHdr = [['#', E+W], ['Clock', E+W], ['Class', W], ['Sail', W], ['Race', W], ['Status', W], ['Notes', W]]
        for i,h in enumerate(fileHdr):
            l = Label(f, text=h[0])
            l.grid(row=0, column=i, sticky=h[1])
               
    def resetFinishBoxAction(self):
        if not messagebox.askyesno('Reset', 'Are you sure? You should save finish times first.'): return
        self.pos = 1
        self.finishData = []
        self.raceNameValue.set('')
        f = self.rowFrame
        for w in f.winfo_children():
            w.destroy()
        self.__addFinishHdr(self.rowFrame)
        tmpFile = getAutoSaveFileName()
        if os.path.exists(tmpFile): os.remove(tmpFile)          
        
    def __getFinishFileName(self):
        now = datetime.now()
        useDefaultFolder = True if self.config.get('Files', 'finshFileUseDefaultFolder').lower() == 'true' else False
        defaultFolder = os.path.expanduser('~') if useDefaultFolder else ''
        fn = self.config.get('Files','finishFileFolder') + 'finishes-{}'.format(now.strftime('%Y%m%d-%H%M'))
        return defaultFolder + fn
        
    def saveToFileAction(self):
        saveFileName = self.__getFinishFileName()
        saveFinishesToCSV = saveToCSVFile(
                saveFileName + '.csv',
                {
                    'name': self.raceNameValue.get(),
                    'date': self.raceDateValue.get(),
                    'data': self.finishData
                },
                self.classList
            )
        if saveFinishesToCSV['result']:
            tk.messagebox.showinfo('Save File', saveFinishesToCSV['msg'])
        else:
            tk.messagebox.showinfo('Save File Error', saveFinishesToCSV['msg'])
        jsonResult = setJSONFinishData(
            saveFileName + '.json',
            {
                'name': self.raceNameValue.get(),
                'date': self.raceDateValue.get(),
                'data': self.finishData
            },
            self.classList
        )
        if not jsonResult: tk.messagebox.showinfo('Save File Error', 'JSON finish data could not be saved')
                

       
    def autoSaveAction(self):
        saveFileName = getAutoSaveFileName()
        setJSONFinishData(
            saveFileName + '.json',
            {
                'name': self.raceNameValue.get(),
                'date': self.raceDateValue.get(),
                'data': self.finishData
            },
            self.classList
        )
                              
    def __restoreFinishGridInfo(self):
        autoSaveFile = getAutoSaveFileName()
        autoSaveInfo = getJSONFinishData(autoSaveFile)
        finishRowList = []
        for row in autoSaveInfo['data']:
            finishRowList.append({
                'pos': row['pos'],
                'clock': row['clock'],
                'class': StringVar(value=row['class']),
                'sailnum': StringVar(value=row['sailnum']),
                'race': StringVar(value=row['race']),
                'status': StringVar(value=row['status']),
                'notes': StringVar(value=row['notes'])
            })
        return {
            'name': autoSaveInfo['name'],
            'date': autoSaveInfo['date'],
            'data': finishRowList
        }

        
    def __drawApproachingBoats(self, abFrame): 
        padGap = 4
        layout = [2,2]
        for row in range(layout[0]):
            for col in range(layout[1]):
                f = Frame(abFrame, padx=4, pady=4)
                f.grid(row=row, column=col)
                
                lc = Label(f, text="Class")
                lc.pack(side=LEFT, padx=(0,padGap))
                
                cStrVar = StringVar()
                c = ttk.Combobox(f, values=self.classNames, width=10, textvariable=cStrVar)
                c.pack(side=LEFT, padx=(0,padGap))
                
                ls = Label(f, text="Sail")
                ls.pack(side=LEFT, padx=(0,padGap))
                
                sStrVar = StringVar()
                s = ttk.Entry(f, validate='key', validatecommand=self.validateNumbers, width=8, textvariable=sStrVar)
                s.pack(side=LEFT, padx=(0,padGap))
                
                b = ttk.Button(
                    f,
                    text='Finish',
                    command=lambda classRef=cStrVar, sailRef=sStrVar: self.__abFinishAction(classRef, sailRef)
                )
                b.pack(side=LEFT, padx=(padGap,0))
    
    def __abFinishAction(self, classRef, sailRef):
        abClass = classRef.get()
        abSail = sailRef.get()
        self.finishAction(abClass, abSail)
        classRef.set('')
        sailRef.set('')
