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
        if len(asInfo['name']) > 0: self.raceNameValue.set(asInfo['name'])
        enRaceName = ttk.Entry(raceNameFrame, textvariable=self.raceNameValue)
        enRaceName.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        enRaceName.pack(side=LEFT, anchor=W, padx=(4,0))
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
        #define columns
        self.colFrames = []
        for i in range(7):
            self.colFrames.append(Frame(self.rowFrame))
            self.colFrames[i].grid(row=0, column=i, padx=(0, 10))
                
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
        rbf = LabelFrame(rf, text='Use Between Races')
        rbf.pack(side=BOTTOM, anchor=W, pady=(0,25), ipady=25)
        #save as file button
        btnReset = ttk.Button(rbf, text="Save Finishes", command=self.saveToTxtFileAction, style='Custom.TButton')
        btnReset.pack(expand=True, anchor=CENTER)          
        #reset counter button
        btnReset = ttk.Button(rbf, text="Reset Finish Box", command=self.resetFinishBoxAction, style='Custom.TButton')
        btnReset.pack(expand=True, anchor=CENTER)
        
        #finish times header        
        self.__addFinishHdrRow()
        if len(asInfo['data']) > 0:
            for row in asInfo['data']:
                self.__drawFinishRow(row)
                if not row['pos'] == 0: self.pos = row['pos'] + 1
        
    def finishAction(self):
        on2Off = float(self.config.get('Signals', 'finishOn2Off'))
        self.relay.onoff(self.fc, on2Off)
        finishData = self.__addFinishData()
        self.finishData.append(finishData)
        self.pos += 1
        self.__drawFinishRow(finishData)
        self.autoSaveAction()
        
    def nonFinishAction(self):
        finishData = self.__addFinishData(False)
        self.finishData.append(finishData)
        self.__drawFinishRow(finishData)
        self.autoSaveAction()
                
    def __addFinishData(self, finisher=True):
        now = datetime.now()
        #finish data for this row
        newFinishData = {
            'pos': self.pos if finisher else 0,
            'clock': {'hh': now.hour, 'mm': now.minute, 'ss': now.second, 'ms': now.microsecond},
            'class': StringVar(),
            'sailnum': StringVar(), #the interface uses a string
            'race': StringVar(),
            'status': StringVar(),
            'notes': StringVar()
        }
        newFinishData['race'].set('1') #default race number to 1
        if finisher: newFinishData['status'].set('Finished')
        return newFinishData

    def __drawFinishRow(self, rowData):
        #draw the row
        above = 8
        txtPos = '{:>3}'.format(rowData['pos'])if rowData['pos'] > 0 else ''
        lPos = Label(self.colFrames[0], text=txtPos, font=FinishTimesInterface.FIXED_FONT)
        lPos.pack(side=BOTTOM, pady=(above,0))
        
        lTime = Label(self.colFrames[1], 
            text='{:02}:{:02}:{:02}'.format(rowData['clock']['hh'], rowData['clock']['mm'], rowData['clock']['ss'])
             if rowData['status'].get() == FinishTimesInterface.STATUS_FINISHED else '', 
            font=FinishTimesInterface.FIXED_FONT_BOLD)
        lTime.pack(side=BOTTOM, pady=(above,0))
        
        cbClass = ttk.Combobox(self.colFrames[2], values=self.classNames, textvariable=rowData['class'], width=14)
        cbClass.pack(side=BOTTOM, pady=(above,0))
        cbClass.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        cbClass.bind('<<ComboboxSelected>>', lambda e: self.autoSaveAction())
        
        validateNumbers = (self.colFrames[3].register(self.__onlyNumbers), '%S')
        
        enSailNum = ttk.Entry(self.colFrames[3], validate='key', validatecommand=validateNumbers, textvariable=rowData['sailnum'], width=14)
        enSailNum.pack(side=BOTTOM, pady=(above,0))
        enSailNum.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        
        enRaceNum = ttk.Entry(self.colFrames[4], validate='key', validatecommand=validateNumbers, textvariable=rowData['race'], width=4)
        enRaceNum.pack(side=BOTTOM, pady=(above,0))
        enRaceNum.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        
        if rowData['status'].get() == FinishTimesInterface.STATUS_FINISHED:
            lStatus = Label(self.colFrames[5], text=FinishTimesInterface.STATUS_FINISHED)
            lStatus.pack(side=BOTTOM, anchor=W, pady=(above,0))
        else:
            cbStatus = ttk.Combobox(self.colFrames[5], values=self.statusCodes, textvariable=rowData['status'], state='readonly', width=8)
            cbStatus.pack(side=BOTTOM, pady=(above,0))
            cbStatus.bind('<<ComboboxSelected>>', lambda e: self.autoSaveAction())
                            
        enNotes = ttk.Entry(self.colFrames[6], textvariable=rowData['notes'], width=25)
        enNotes.pack(side=BOTTOM, pady=(above,0))
        enNotes.bind('<KeyRelease>', lambda e: self.autoSaveAction())

    def __addFinishHdrRow(self):
        fileHdr = [['#', E], ['Clock', CENTER], ['Class', W], ['Sail Number', W], ['Race', W], ['Status', W], ['Notes', W]]
        for i,h in enumerate(fileHdr):
            l = Label(self.colFrames[i], text=h[0])
            l.pack(anchor=h[1])
        
    def __onlyNumbers(self, k):
        if k in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']: return True
        return False
        
    def resetFinishBoxAction(self):
        self.pos = 1
        self.finishData = []
        self.raceNameValue.set('')
        for c in self.colFrames:
            for w in c.winfo_children():
                w.destroy()
        self.__addFinishHdrRow()
        
    def saveToTxtFileAction(self):
        saveResult = self.__saveToTxtFile()
        if saveResult['result']:
            tk.messagebox.showinfo('Save File', saveResult['msg'])
            tmpFile = self.__getAutoSaveFileName()
            if os.path.exists(tmpFile): os.remove(tmpFile)            
        else:
            tk.messagebox.showinfo('Save File Error', saveResult['msg'])
        
    def saveToTxtFile(self):
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
                    lineOut = '{}, {:02}:{:02}:{:02}, {}, {}, {}, {}, {}, {}\n'.format(
                            f['pos'] if f['pos'] > 0 else '',
                            f['clock']['hh'] if f['pos'] > 0 else 0,
                            f['clock']['mm'] if f['pos'] > 0 else 0,
                            f['clock']['ss'] if f['pos'] > 0 else 0,
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
        