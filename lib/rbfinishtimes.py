from datetime import datetime
import json
import os
import sched
from tkinter import (ALL, BOTH, BOTTOM, CENTER, END, LEFT, NW, RIGHT, E, SW, W, X, Y,
    Canvas, Frame, Label, LabelFrame, Scrollbar, StringVar, messagebox, ttk)
import tkinter as tk
from lib.rbconfig import RaceboxConfig

class FinishTimesInterface:
    
    TITLE_FONT = 'Helvetica 12 bold'
    FIXED_FONT = 'Courier 12'
    FIXED_FONT_BOLD = 'Courier 12 bold'
    
    STATUS_FINISHED = 'Finished'
    
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
        asInfo = self.__getAutoSavedFinishData()
        self.finishData = asInfo['data']
        
        self.fc = fControl
        
        f = Frame(self.fc)
        f.pack(expand=True, fill=BOTH)
          
        #left frame (for results)
        lf = Frame(f)
        lf.pack(side=LEFT, fill=BOTH, expand=True)

        self.validateNumbers = (lf.register(self.__onlyNumbers), '%S')

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
        if len(asInfo['name']) > 0: self.raceNameValue.set(asInfo['name'])
        enRaceName = ttk.Entry(raceNameFrame, textvariable=self.raceNameValue)
        enRaceName.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        enRaceName.pack(side=LEFT, anchor=W, padx=(4,0))
        lraceTimesTitle = Label(self.raceDetailsFrame, text='Finish Times', font=FinishTimesInterface.TITLE_FONT)
        lraceTimesTitle.pack(anchor=W, pady=(4,0))
        
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
        rbf.pack(side=BOTTOM, anchor=W, pady=(0,25), ipady=25)
        #save as file button
        btnReset = ttk.Button(rbf, text="Save Finishes", command=self.saveToTxtFileAction, style='Custom.TButton')
        btnReset.pack(expand=True, anchor=CENTER)          
        #reset counter button
        btnReset = ttk.Button(rbf, text="Reset Finish Box", command=self.resetFinishBoxAction, style='Custom.TButton')
        btnReset.pack(expand=True, anchor=CENTER)
        
        #finish times header        
        self.__addFinishHdr(self.rowFrame)
        
        #autosave data
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
             if rowData[r]['status'].get() == FinishTimesInterface.STATUS_FINISHED else '')

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
            if rowData[r]['status'].get() == FinishTimesInterface.STATUS_FINISHED:
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
        
    def __onlyNumbers(self, k):
        if k in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']: return True
        return False
        
    def resetFinishBoxAction(self):
        if not messagebox.askyesno('Reset', 'Are you sure? You should save finish times first.'): return
        self.pos = 1
        self.finishData = []
        self.raceNameValue.set('')
        f = self.rowFrame
        for w in f.winfo_children():
            w.destroy()
        self.__addFinishHdr(self.rowFrame)
        tmpFile = self.__getAutoSaveFileName()
        if os.path.exists(tmpFile): os.remove(tmpFile)            
        
    def saveToTxtFileAction(self):
        saveResult = self.__saveToTxtFile()
        if saveResult['result']:
            tk.messagebox.showinfo('Save File', saveResult['msg'])
        else:
            tk.messagebox.showinfo('Save File Error', saveResult['msg'])
        
    def __saveToTxtFile(self):
        now = datetime.now()
        useDefaultFolder = True if self.config.get('Files', 'finshFileUseDefaultFolder').lower() == 'true' else False
        defaultFolder = os.path.expanduser('~') if useDefaultFolder else ''
        saveFileName = self.config.get('Files','finishFileFolder') + 'finishes-{}.txt'.format(now.strftime('%Y%m%d-%H%M'))
        fileHdr = 'Pos, Clock, Class, Sail, Rating, Race, Status, Notes\n'
        try:
            with open (defaultFolder + saveFileName, 'w+') as file:
                if len(self.raceNameValue.get()) > 0: file.write(self.raceNameValue.get() + '\n')
                file.write(fileHdr)
                for f in self.finishData:
                    rating = ''
                    for c in self.classList:
                        if c['name'].lower().strip() == f['class'].get().lower().strip():
                            rating = str(c['rating'])
                    if f['pos'] > 0:
                        lineOut = '{}, {:02}:{:02}:{:02}, {}, {}, {}, {}, {}, {}\n'.format(
                            f['pos'],
                            f['clock']['hh'],
                            f['clock']['mm'],
                            f['clock']['ss'],
                            f['class'].get(),
                            f['sailnum'].get(),
                            rating,
                            f['race'].get(),
                            f['status'].get() if f['status'].get() != FinishTimesInterface.STATUS_FINISHED else '',
                            f['notes'].get()
                        )
                    else:
                        lineOut = '{}, {}, {}, {}, {}, {}, {}, {}\n'.format(
                            '',
                            '',
                            f['class'].get(),
                            f['sailnum'].get(),
                            rating,
                            f['race'].get(),
                            f['status'].get() if f['status'].get() != FinishTimesInterface.STATUS_FINISHED else '',
                            f['notes'].get()
                        )
                    file.write(lineOut)
                return {'result': True, 'msg': 'File {}{} saved'.format(defaultFolder, saveFileName)}
        except Exception as error:
            return {'result': False, 'msg': 'Could not save the file {}{} - {}'.format(defaultFolder, saveFileName, error)}
    
    def __getAutoSaveFileName(self):
        homeFolder = os.path.expanduser('~')
        return homeFolder + '/rbautosave.json'
    
    def autoSaveAction(self):
        self.__autoSaveFinishData()
            
    def __autoSaveFinishData(self):
        saveFileName = self.__getAutoSaveFileName()
        tempFile = {
            'name': self.raceNameValue.get(),
            'data': []
        }
        for rd in self.finishData:
            rd = {
                'pos': rd['pos'],
                'clock': rd['clock'],
                'class': rd['class'].get(),
                'sailnum':rd['sailnum'].get(),
                'race': rd['race'].get(),
                'status': rd['status'].get(),
                'notes': rd['notes'].get()
            }
            tempFile['data'].append(rd)
        try:
            with open (saveFileName, 'w+') as file:
                file.write(json.dumps(tempFile))
        except Exception as error:
            print(error)
            
    def __getAutoSavedFinishData(self):
        raceInfo = {
            'name': '',
            'data': []
        }
        tmpFile = self.__getAutoSaveFileName()
        try:
            with open (tmpFile, 'r') as file:
                tmp = json.load(file)
                raceInfo['name'] = tmp['name']
                for row in tmp['data']:
                    raceInfo['data'].append({
                            'pos': row['pos'],
                            'clock': row['clock'],
                            'class': StringVar(value=row['class']),
                            'sailnum': StringVar(value=row['sailnum']),
                            'race': StringVar(value=row['race']),
                            'status': StringVar(value=row['status']),
                            'notes': StringVar(value=row['notes'])
                        })
                return raceInfo
        except: # Exception as error:
            return raceInfo
        
        
    def __drawApproachingBoats(self, abFrame): 
        self.abClassList = []
        self.abSailList = []
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
                self.abClassList.append(cStrVar)
                c.pack(side=LEFT, padx=(0,padGap))
                
                ls = Label(f, text="Sail")
                ls.pack(side=LEFT, padx=(0,padGap))
                
                sStrVar = StringVar()
                s = ttk.Entry(f, validate='key', validatecommand=self.validateNumbers, width=8, textvariable=sStrVar)
                self.abSailList.append(sStrVar)
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
