from tkinter import (ALL, BOTH, E, LEFT, NW, RIGHT, W, Y, BooleanVar,
                     Canvas, Frame, IntVar, LabelFrame, Scrollbar, Spinbox, StringVar, Variable,
                     ttk)
#from lib.rbdb import rbDb
from lib.rbutility import (
        ENTRY_FONT,
        MONTH_ABBREV, 
        MSEC_IN_DAY, MSEC_IN_HOUR, MSEC_IN_MINUTE,
        NO_RACE_SELECTED,
        STATUS_FINISHED,
        TITLE_FONT,
        TOTALMS,
        USE_FINISH_TIMES,
        getCurrentFilesFolder,
        getFileList,
        getFileNames,
        getJSONFinishData,
        msToTime,
        numSuffix,
    )

class ResultsInterface():
       
    def __init__(self, fControl: ttk.Frame):
        self.fParent = Frame(fControl)
        self.fParent.pack(expand=True, fill=BOTH)
        self.fMain = Frame(self.fParent)
        #fHdr = Frame(fControl, bg='orange')
        self.fSideRight = Frame(self.fParent) #, bg='palegreen')
        #fHdr.pack(expand=False, fill=BOTH, padx=(2,2), pady=(2,2))
        self.setMainAreaVisible()
        
        #create the edit screen (not shown by default)
        self.fEdit = Frame(self.fParent)
        self.createEditPage()
        self.editEntryId = IntVar(value=-1)
        
        #identify frames using some labels
        #lHdr = ttk.Label(self.fHdr, text='Header')
        #lHdr.pack()
        #lMain = ttk.Label(self.fMain, text='Main panel')
        #lMain.pack()
        #lRight = ttk.Label(self.fSideRight, text='Right panel')
        #lRight.pack()
                
        #create the control panel
        self.displayRaceId = StringVar(value=NO_RACE_SELECTED)
        self.showControlPanel(self.fSideRight)
        
        #create the scrollable canvas
        fResultsArea = Frame(self.fMain)
        fResultsArea.pack(expand=True, fill=BOTH)
        canvas = Canvas(fResultsArea , highlightthickness=0)
        sb = Scrollbar(fResultsArea , orient='vertical', command=canvas.yview)
        self.fResults = Frame(canvas) #do not pack this
        cw = canvas.create_window((0, 0), window=self.fResults, anchor=NW)
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=2)
        sb.pack(side=RIGHT, fill=Y)        
        self.fResults.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox(ALL)))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(cw, width=e.width))
        
        #add holding message
        lbl = ttk.Label(self.fResults, text='Results appear here automatically after finishes are saved')
        lbl.pack(anchor=W)
        lbl = ttk.Label(self.fResults, text='Or you can load a source file from the control panel')
        lbl.pack(anchor=W)
               
        #keep the finish data
        self.currentFinishData = False
        self.resultWorkingSet = False
        self.previousStart = 1     
    
    def setMainAreaVisible(self, showFrame=True):
        self.fSideRight.pack(side=RIGHT, expand=False, fill=Y, padx=(2,2), pady=(10,2)) if showFrame else self.fSideRight.forget()
        self.fMain.pack(expand=True, fill=BOTH, padx=(2,2), pady=(10,2)) if showFrame else self.fMain.forget()
           
    def getProcessedRaceData(self, raceInfo):
        if not raceInfo: return False
        
        #get finish data
        finishData = list(raceInfo['data'])
        
        #get control panel values
        cp = self.getControlPanelValues()
        
        #define start time
        startMs = cp['startHour'] * MSEC_IN_HOUR + cp['startMinute'] * MSEC_IN_MINUTE
        print('start ms ', startMs)
        
        #remove boats not in this race
        for i in finishData.copy():
            if not i['race'] == cp['startNumber']: finishData.remove(i)
        #calculate finish time for each boat in ms
        for i in finishData:
            if i['status'] == STATUS_FINISHED:
                msSum = (
                    i['clock']['hh'] * MSEC_IN_HOUR
                    + i['clock']['mm'] * MSEC_IN_MINUTE
                    + i['clock']['ss'] * 1000
                    ###+ i['clock']['ms']
                )
                if cp['useCorrected'] == True:
                    i[TOTALMS] = (msSum - startMs) / (i['rating'] / 1000)
                    print(msSum - startMs, i['rating'] / 1000)
                else:
                    i[TOTALMS] = msSum - startMs if self.startTimeSet else msSum
            else: i[TOTALMS] = MSEC_IN_DAY #non-finishers - this makes sorting easier
                
        finishData.sort(key=lambda x: x[TOTALMS])
        return {
            **raceInfo,
            'data': finishData,
        }
    
    def editEntry(self, i):
        print('test', i)
        self.editEntryId.set(value=i)
        self.setMainAreaVisible(False)
        self.fEdit.pack(expand=True, fill=BOTH)
    
    def editEntryComplete(self, saveEntry=True):
        print('finished editing ', self.editEntryId.get(), ' save is ', saveEntry)
        if saveEntry: self.upDateEntry()
        self.fEdit.forget()
        self.setMainAreaVisible()
        
    def upDateEntry(self):
        print('update entry ', self.editEntryId.get())
        ##update data in self.resultWorkingSet

    def deleteEntry(self):
        print('delete entry ', self.editEntryId.get())
        ##delete it here
        self.editEntryComplete(False) #then return to main screen     
        
    def setCurrentFinishData(self, fd):
        self.currentFinishData = fd
        self.resultWorkingSet = fd
        self.unsetStartTime()
                             
    def showRecentRace(self):
        raceInfo = self.getProcessedRaceData(self.resultWorkingSet)        
        cp = self.getControlPanelValues()
        useCorrected = cp['useCorrected']
        
        ############################################ may still be an issue        
        #keep control panel start value in sync
        #if not startNumber == int(self.spStartValue.get()): self.spStartValue.set(startNumber)
        
        #remove any previous results
        for c in self.fResults.winfo_children():
            c.destroy()

        #padding for the results cells
        racePadX = (4,4)
        racePadY = (2,2)

        #icon
        #editIcon = PhotoImage(file='images/edit16.png')
        #weird, but necessary otherwise editIcon is garbage-collected
        #lEditIcon = ttk.Label(image=editIcon)
        #lEditIcon.image = editIcon
        
        if not raceInfo:
            self.displayRaceId.set(NO_RACE_SELECTED)
            if self.cbFinishOptionValue.get() == USE_FINISH_TIMES:
                msg = 'Save the current finish times or select a source file'
            else:
                msg = 'No race data found'
            lbl = ttk.Label(self.fResults, text=msg)
            lbl.grid(row=0, column=0, columnspan=8, sticky=W)
            return
              
        #show the race id in the control panel
        self.displayRaceId.set(raceInfo['id'])

        #show race title
        lRaceTitle = ttk.Label(self.fResults, text=raceInfo['name'], style='Def12Bold.TLabel')
        lRaceTitle.grid(row=0, column=0, columnspan=8, sticky=W)
        
        #show race date
        dateText = '{}{} {} {}'.format(
                raceInfo['date']['day'],
                numSuffix(raceInfo['date']['day']),
                MONTH_ABBREV[raceInfo['date']['month'] - 1],
                raceInfo['date']['year'],
            )
        lRaceDate = ttk.Label(self.fResults, text=dateText)
        lRaceDate.grid(row=1, column=0, columnspan=8, sticky=W)

        #show race start time
        timeText = 'Start time {:02}:{:02}'.format(
                cp['startHour'],
                cp['startMinute'],
            ) if self.startTimeSet else 'Start time (not set)'
        lRaceTime = ttk.Label(self.fResults, text=timeText)
        lRaceTime.grid(row=3, column=0, columnspan=8, sticky=W)

        #show race number
        lRaceNum = ttk.Label(self.fResults, text='{}{} start'.format(cp['startNumber'], numSuffix(cp['startNumber'])))
        lRaceNum.grid(row=2, column=0, columnspan=8, sticky=W)
               
        #column titles
        #tableHdr = ['', 'Class', 'Sail', 'Finish', 'Corrected', 'Rating'] if useCorrected else ['', 'Class', 'Sail', 'Finish', 'Elapsed']
        if not self.startTimeSet:
            tableHdr = ['', 'Class', 'Sail', 'Finish']
        elif useCorrected:
            tableHdr = ['', 'Class', 'Sail', 'Finish', 'Corrected', 'Rating']
        else:
            tableHdr = ['', 'Class', 'Sail', 'Finish', 'Elapsed']
        
        for i,h in enumerate(tableHdr):
            lHdr = ttk.Label(self.fResults, text=h, anchor=W, style='Def12Bold.TLabel')
            lHdr.grid(row=4, column=i, sticky=W, padx=racePadX, pady=racePadY)
            
        #if there are no finish times for this start...
        if len(raceInfo['data']) == 0:
            noTimesMsg = 'No finish times found for this start'
            lbl = ttk.Label(self.fResults, text=noTimesMsg, anchor=W)
            lbl.grid(row=0, column=0, columnspan=8, sticky=W, padx=racePadX, pady=racePadY)

        #display the results for each boat
        startRow = 5
        for i,d in enumerate(raceInfo['data']):
            #add an edit button
            #bEdit = ttk.Button(self.fResults, image=editIcon, command=lambda x = i: self.editEntry(x), padding=(0,0))
            #bEdit.grid(row=i+startRow, column=0)
           
            #pos
            lbl = ttk.Label(self.fResults, text=i+1, anchor=W, foreground='blue', borderwidth=2, relief='groove', padding=(8,1), takefocus=True)
            lbl.bind('<Button-1>', lambda _, x = i: self.editEntry(x))
            lbl.grid(row=i+startRow, column=0, sticky=E, padx=racePadX, pady=racePadY)

            lbl = ttk.Label(self.fResults, text=' '.join(d['class'].split()).strip(), anchor=W)
            lbl.grid(row=i+startRow, column=1, sticky=W, padx=racePadX, pady=racePadY)

            lbl = ttk.Label(self.fResults, text=d['sailnum'], anchor=W)
            lbl.grid(row=i+startRow, column=2, sticky=W, padx=racePadX, pady=racePadY)

            lbl = ttk.Label(self.fResults,
                    text='{:02}:{:02}:{:02}'.format(
                        d['clock']['hh'],
                        d['clock']['mm'],
                        d['clock']['ss'],
                    ) if d['status'] == STATUS_FINISHED else d['status'],
                    anchor=W
                )
            lbl.grid(row=i+startRow, column=3, sticky=W, padx=racePadX, pady=racePadY)
            
            if not self.startTimeSet:
                pass
            elif useCorrected:
                ct = msToTime(d[TOTALMS])
                #print('corrected time ', ct)
                lbl = ttk.Label(self.fResults,
                    text='{:02}:{:02}:{:02}'.format(
                        ct[0],
                        ct[1],
                        ct[2],
                    ) if d['status'] == STATUS_FINISHED else d['status'],
                    anchor=W
                )
                lbl.grid(row=i+startRow, column=4, sticky=W, padx=racePadX, pady=racePadY)

                rating = '' if d['rating'] == 0 else d['rating']
                lbl = ttk.Label(
                    self.fResults,
                    text=rating,
                    anchor=W
                )
                lbl.grid(row=i+startRow, column=5, sticky=W, padx=racePadX, pady=racePadY)
            else:
                et = msToTime(d[TOTALMS])
                #print('elapsed time ', et)
                lbl = ttk.Label(self.fResults,
                    text='{:02}:{:02}:{:02}'.format(
                        et[0],
                        et[1],
                        et[2],
                    ) if d['status'] == STATUS_FINISHED else d['status'],
                    anchor=W
                )
                lbl.grid(row=i+startRow, column=4, sticky=W, padx=racePadX, pady=racePadY)
            
    def startChoiceUpdate(self):
        if self.spStartValue.get() == self.previousStart:
            return
        self.unsetStartTime()
        self.updateDisplayedRaceData()
        self.previousStart = self.spStartValue.get()

    def finishChoiceUpdate(self):
        self.spStartValue.set(1)
        self.unsetStartTime()
        self.updateDisplayedRaceData()
        
    def correctedTimeUpdate(self, val):
        #print('corrected time update ', val)
        self.updateDisplayedRaceData()
    
    def setStartTime(self):
        #print('start time set or updated')
        self.startTimeSet = True
        self.updateDisplayedRaceData()

    def unsetStartTime(self):
        #print('start time unset')
        self.startTimeSet = False
        
    def updateDisplayedRaceData(self):
        fileName = self.cbFinishOptionValue.get()
        
        if fileName == USE_FINISH_TIMES:
            self.resultWorkingSet = self.currentFinishData
            self.showRecentRace()
            return
        
        if len(self.cpFileNamesList) == 0: return
        try:
            pos = self.cpFileNamesList.index(fileName)
        except:
            pos = -1
        if pos > -1:
            self.resultWorkingSet = getJSONFinishData(self.cpFilePathsList[pos])
            self.showRecentRace()
                              
    def showControlPanel(self, f):
        fControl = LabelFrame(f, text='Results Control Panel', font=TITLE_FONT, padx=8, pady=4)
        fControl.pack(padx=(4,4), pady=(0,2))

        #grid padding
        Xpadding=(0,4)
        Ypadding=(12,0)
        
        #load finish times file
        fFinishCombo = Frame(fControl)
        fFinishCombo.grid(row=1,column=0, padx=Xpadding, pady=Ypadding, sticky=W)
        lbl = ttk.Label(fFinishCombo, text='Source')
        lbl.pack(side=LEFT, padx=(0,8), pady=(0,0), anchor=W)
        self.cpFilePathsList = getFileList(getCurrentFilesFolder())
        self.cpFileNamesList = getFileNames(self.cpFilePathsList)
        self.cbFinishOptionValue = StringVar(value=USE_FINISH_TIMES)
        cbFinishOptions = [USE_FINISH_TIMES, *self.cpFileNamesList]
        cbFinishFile = ttk.Combobox(fFinishCombo, values=cbFinishOptions, width=32, textvariable=self.cbFinishOptionValue, state='readonly')
        cbFinishFile.pack(side=LEFT, pady=(0,0), anchor=W)
        self.cbFinishOptionValue.trace_add('write', callback=lambda name,index,mode: self.finishChoiceUpdate())
        
        #race id
        fRaceID = Frame(fControl)
        fRaceID.grid(row=2,column=0, padx=Xpadding, pady=Ypadding, sticky=W)
        lbl = ttk.Label(fRaceID, text='Race ID')
        lbl.pack(padx=(0,8), pady=(0,0), anchor=W)
        lbl = ttk.Label(
            fRaceID,
            textvariable=self.displayRaceId
        )
        lbl.pack(padx=(0,8), pady=(0,0), anchor=W)
        
        #start number
        fStartControl = Frame(fControl)
        fStartControl.grid(row=3,column=0, padx=Xpadding, pady=Ypadding, sticky=W)
        lbl = ttk.Label(fStartControl, text='Start')
        lbl.pack(side=LEFT, padx=(0,8), pady=(0,0), anchor=W)
        self.spStartValue = StringVar(value=1)
        spStart = Spinbox(fStartControl, from_=1, to=999, textvariable=self.spStartValue, format="%01.0f", state='readonly', font=ENTRY_FONT)
        spStart.pack(side=LEFT, pady=(0,0), anchor=W)
        spStart.config(width=3)
        self.spStartValue.trace_add('write', callback=lambda name,index,mode: self.startChoiceUpdate())
        
        #start time
        self.startTimeSet = False
        fStartTime = Frame(fControl)
        fStartTime.grid(row=4,column=0, padx=Xpadding, pady=Ypadding, sticky=W)
        lbl = ttk.Label(fStartTime, text='Start Time')
        lbl.pack(padx=(0,8), pady=(0,0), anchor=W)
        #start time fields
        self.hhStartValue = Variable(value='12')
        hhEntry = Spinbox(fStartTime, from_=0, to=23, textvariable=self.hhStartValue, format="%02.0f", state='readonly', font=ENTRY_FONT)
        hhEntry.pack(side='left')
        hhEntry.config(width=3)
        self.mmStartValue = Variable(value='00')
        mmEntry = Spinbox(fStartTime, from_=0, to=59, textvariable=self.mmStartValue, format="%02.0f", state='readonly', font=ENTRY_FONT)
        mmEntry.pack(side='left', padx=(4, 0))
        mmEntry.config(width=3)        
        #start time update button
        btnTimeUpdate = ttk.Button(
            fStartTime,
            text="Set",
            command=self.setStartTime,
            style='CustomSmall.TButton',
            width=4
            )
        btnTimeUpdate.pack(side='left', padx=(8, 0))
        
        #corrected time
        fCorrected = Frame(fControl)
        fCorrected.grid(row=5,column=0, padx=Xpadding, pady=Ypadding, sticky=W)
        self.chkCorrectedValue = BooleanVar(value=False)
        chkCorrected = ttk.Checkbutton(fCorrected, text='Use Corrected Time', variable=self.chkCorrectedValue)
        chkCorrected.pack(side=LEFT, pady=(0,0), anchor=W)
        self.chkCorrectedValue.trace_add('write', callback=lambda name,index,mode: self.correctedTimeUpdate(self.chkCorrectedValue.get()))
                
    def getControlPanelValues(self):
        return {
            'raceId': self.displayRaceId.get(),
            'sourceFile': self.cbFinishOptionValue.get(),
            'startNumber': int(self.spStartValue.get()),
            'startHour': int(self.hhStartValue.get()),
            'startMinute': int(self.mmStartValue.get()),
            'useCorrected': self.chkCorrectedValue.get()
        }
    
    def createEditPage(self):
        #self.fEdit = Frame(self.fParent)
        #print('create edit page')
        lEdit = ttk.Label(self.fEdit, text='Test editing an entry')
        lEdit.pack(side=LEFT)
        bEditCancel = ttk.Button(self.fEdit, text='Cancel', command=lambda: self.editEntryComplete(False), style='Custom.TButton')
        bEditCancel.pack(side=LEFT)
        bEditOk = ttk.Button(self.fEdit, text='Ok', command=lambda: self.editEntryComplete(True), style='Custom.TButton')
        bEditOk.pack(side=LEFT)
        bEditDelete = ttk.Button(self.fEdit, text='Delete', command=lambda: self.deleteEntry(), style='Custom.TButton')
        bEditDelete.pack(side=LEFT)

""" {
  "id": "b60d2858-5ef5-48c0-8e2a-e7336091d98c",
  "name": "Aero Race",
  "date": {
    "day": 3,
    "month": 10,
    "year": 2023
  },
  "data": [
    {
      "pos": 1,
      "clock": {
        "hh": 20,
        "mm": 23,
        "ss": 27,
        "ms": 731.506
      },
      "class": "Aero9",
      "rating": 1010,
      "sailnum": "1760",
      "race": 1,
      "status": "Finished",
      "notes": ""
    },
  ]
}

    def getControlPanelValues(self):
        return {
            'raceId'
            'sourceFile'
            'startNumber'
            'startHour'
            'startMinute'
            'useCorrected'
        }
 """