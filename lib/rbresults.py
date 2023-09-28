from tkinter import (ALL, BOTH, E, LEFT, NW, RIGHT, W, Y, BooleanVar,
                     Canvas, Frame, Scrollbar, Spinbox, StringVar, Variable,
                     ttk)
from lib.rbdb import rbDb
from lib.rbutility import (
        ENTRY_FONT,
        MONTH_ABBREV, 
        MSEC_IN_DAY, MSEC_IN_HOUR, MSEC_IN_MINUTE,
        NO_RACE_SELECTED,
        STATUS_FINISHED,
        USE_FINISH_TIMES,
        getCurrentFilesFolder,
        getFileList,
        getFileNames,
        getJSONFinishData,
        numSuffix,
    )

class ResultsInterface():
       
    def __init__(self, fControl: ttk.Frame):
        fMain = Frame(fControl)
        #fHdr = Frame(fControl, bg='orange')
        fSideRight = Frame(fControl, bg='palegreen')
        #fHdr.pack(expand=False, fill=BOTH, padx=(2,2), pady=(2,2))
        fSideRight.pack(side=RIGHT, expand=False, fill=Y, padx=(2,2), pady=(10,2))
        fMain.pack(expand=True, fill=BOTH, padx=(2,2), pady=(10,2))
        
        #identify frames using some labels
        #lHdr = ttk.Label(self.fHdr, text='Header')
        #lHdr.pack()
        #lMain = ttk.Label(fMain, text='Main panel')
        #lMain.pack()
        #lRight = ttk.Label(self.fSideRight, text='Right panel')
        #lRight.pack()
                
        #create the control panel
        self.displayRaceId = StringVar(value=NO_RACE_SELECTED)
        self.showControlPanel(fSideRight)
        
        #create the scrollable canvas
        fResultsArea = Frame(fMain)
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
               
        ##################################################
        #use the new db utils - just testing
        db = rbDb()
        result = db.createTable('test table', ('col1', 'col2'))
        print('create table result ', result)
        #result = db.addRow('test table', ('another row', 99))
        #print('add row result ', result)
        #result = db.addRows('test table',
        #    [
        #        ('some text', 5),
        #        ('some other text', 99),\
        #    ]
        #)
        #print('add rows result ', result)
        #result = db.removeRows('test table', 'col1', 'another row')
        #print('remove rows result', result)
        db.saveChanges()
        result = db.getRows('test table')
        print('get row data: ', result)
        #result = db.deleteTable('test table')
        #print('delete table result ', result)
        #################################################
        
        #self.getRecentRaceFile()

        #self.showRecentRace()
        
    #def getFinishFiles(self):
    #    fileList = getFileList(getCurrentFilesFolder())
    #    if len(fileList) < 1:
    #        return False
    #    #recentRaceData = getJSONFinishData(fileList[0])
    #    #return recentRaceData
    #    return fileList
    #removing this as getFileList(getCurrentFilesFolder()) gives the same list
    #os.path.basename(full_path) gives you the filename only (for the dialog box)
    #need to add a files dialog to the control panel
    
    def getProcessedRaceData(self, raceNumber, raceInfo):
        if not raceInfo: return False
        TOTALMS = 'finishms'
        finishData = list(raceInfo['data'])
        for i in finishData.copy():
            if not i['race'] == raceNumber: finishData.remove(i)
        for i in finishData:
            if i['status'] == STATUS_FINISHED:
                msSum = (
                    i['clock']['hh'] * MSEC_IN_HOUR
                    + i['clock']['mm'] * MSEC_IN_MINUTE
                    + i['clock']['ss'] * 1000
                    + i['clock']['ms']
                )
                i[TOTALMS] = msSum
            else: i[TOTALMS] = MSEC_IN_DAY # to make sorting easier
                
        finishData.sort(key=lambda x: x[TOTALMS])
        return {
            **raceInfo,
            'data': finishData,
        }
    
    def editEntry(self, i):
        print('test', i)
        
    def setCurrentFinishData(self, fd):
        self.currentFinishData = fd
        self.resultWorkingSet = fd
        
    def showRecentRace(self, startNumber=1, useCorrectedTime=False): #corrected time calc needs a start time
        raceInfo = self.getProcessedRaceData(
            startNumber,
            self.resultWorkingSet,
        )
        
        #keep control panel start value in sync
        if not startNumber == int(self.spStartValue.get()): self.spStartValue.set(startNumber)
        
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

        #show race number
        lRaceNum = ttk.Label(self.fResults, text='{}{} Start'.format(startNumber, numSuffix(startNumber)))
        lRaceNum.grid(row=2, column=0, columnspan=8, sticky=W)
        
        #show race date
        dateText = '{}{} {} {}'.format(
                raceInfo['date']['day'],
                numSuffix(raceInfo['date']['day']),
                MONTH_ABBREV[raceInfo['date']['month'] - 1],
                raceInfo['date']['year'],
            )
        lRaceDate = ttk.Label(self.fResults, text=dateText)
        lRaceDate.grid(row=1, column=0, columnspan=8, sticky=W)
               
        #column titles
        tableHdr = ['', 'Class', 'Sail', 'Finish', 'Rating']
        for i,h in enumerate(tableHdr):
            lHdr = ttk.Label(self.fResults, text=h, anchor=W, style='Def12Bold.TLabel')
            lHdr.grid(row=3, column=i, sticky=W, padx=racePadX, pady=racePadY)
            
        #if there are no finish times for this start...
        if len(raceInfo['data']) == 0:
            noTimesMsg = 'No finish times found for this start'
            lbl = ttk.Label(self.fResults, text=noTimesMsg, anchor=W)
            lbl.grid(row=4, column=0, columnspan=8, sticky=W, padx=racePadX, pady=racePadY)

        #display the results for each boat
        startRow = 4
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

            rating = '' if d['rating'] == 0 else d['rating']
            lbl = ttk.Label(
               self.fResults,
               text=rating,
               anchor=W
            )
            lbl.grid(row=i+startRow, column=4, sticky=E, padx=racePadX, pady=racePadY)
            
    def startChoiceUpdate(self):
        if self.spStartValue.get() == self.previousStart:
            return
        self.updateDisplayedRaceData()
        self.previousStart = self.spStartValue.get()

    def finishChoiceUpdate(self):
        self.spStartValue.set(1)
        self.updateDisplayedRaceData()
        
    def correctedTimeUpdate(self, val):
        print('corrected time update ', val)
        
    def updateDisplayedRaceData(self):
        fileName = self.cbFinishOptionValue.get()
        
        if fileName == USE_FINISH_TIMES:
            self.resultWorkingSet = self.currentFinishData
            self.showRecentRace(int(self.spStartValue.get()))
            return
        
        if len(self.cpFileNamesList) == 0: return
        try:
            pos = self.cpFileNamesList.index(fileName)
        except:
            pos = -1
        if pos > -1:
            self.resultWorkingSet = getJSONFinishData(self.cpFilePathsList[pos])
            self.showRecentRace(int(self.spStartValue.get()))
                              
    def showControlPanel(self, f):
        fControl = Frame(f)
        fControl.pack(padx=(8,8), pady=(0,2))
        
        #title label
        lbl = ttk.Label(fControl,text='Results Control Panel',style='Def12Bold.TLabel')
        lbl.grid(row=0,column=0, columnspan=8, sticky=W)
        
        #grid padding
        Xpadding=(0,4)
        Ypadding=(12,0)
        
        #get finish times
        #tbtn = ttk.Button(fControl, text='Get Finish Times')
        #tbtn.grid(row=1, column=0, sticky=W, padx=(0,4), pady=Ypadding)
        #lbl = ttk.Label(fControl, text='(overwrites any changes made below)')
        #lbl.grid(row=1, column=1, sticky=W, padx=(0,0), pady=Ypadding)
        
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
        fStartTime = Frame(fControl)
        fStartTime.grid(row=4,column=0, padx=Xpadding, pady=Ypadding, sticky=W)
        lbl = ttk.Label(fStartTime, text='Start Time')
        lbl.pack(padx=(0,8), pady=(0,0), anchor=W)
        #start time fields
        self.hhStartValue = Variable(value='14')
        hhEntry = Spinbox(fStartTime, from_=0, to=23, textvariable=self.hhStartValue, format="%02.0f", state='readonly', font=ENTRY_FONT)
        hhEntry.pack(side='left')
        hhEntry.config(width=3)
        self.mmStartValue = Variable(value='30')
        mmEntry = Spinbox(fStartTime, from_=0, to=59, textvariable=self.mmStartValue, format="%02.0f", state='readonly', font=ENTRY_FONT)
        mmEntry.pack(side='left', padx=(4, 0))
        mmEntry.config(width=3)
        
        #calculate corrected time? Requires a start time to be entered.
        fCorrected = Frame(fControl)
        fCorrected.grid(row=5,column=0, padx=Xpadding, pady=Ypadding, sticky=W)
        self.chkCorrectedValue = BooleanVar(value=False)
        chkCorrected = ttk.Checkbutton(fCorrected, text='Use Corrected Time', variable=self.chkCorrectedValue)
        chkCorrected.pack(side=LEFT, pady=(0,0), anchor=W)
        self.chkCorrectedValue.trace_add('write', callback=lambda name,index,mode: self.correctedTimeUpdate(self.chkCorrectedValue.get()))
                
        