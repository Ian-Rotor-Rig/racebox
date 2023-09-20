#import json
from tkinter import ALL, BOTH, E, LEFT, NW, RIGHT, W, Y, Canvas, Frame, PhotoImage, Scrollbar, StringVar, ttk
from lib.rbdb import rbDb
from lib.rbutility import (
        MONTH_ABBREV, 
        MSEC_IN_DAY, MSEC_IN_HOUR, MSEC_IN_MINUTE,
        STATUS_FINISHED,
        getCurrentFilesFolder, getFileList, getJSONFinishData,
        numSuffix,
    )

class ResultsInterface():
       
    def __init__(self, fControl: ttk.Frame):
        self.fHdr = Frame(fControl, bg='orange')
        fMain = Frame(fControl)
        self.fSideRight = Frame(fControl, bg='palegreen')
        self.fHdr.pack(expand=False, fill=BOTH, padx=(2,2), pady=(2,2))
        self.fSideRight.pack(side=RIGHT, expand=False, fill=Y, padx=(2,2), pady=(10,2))
        fMain.pack(expand=True, fill=BOTH, padx=(2,2), pady=(10,2))
        
        #identify frames using some labels
        lHdr = ttk.Label(self.fHdr, text='Header')
        lHdr.pack()
        #lMain = ttk.Label(fMain, text='Main panel')
        #lMain.pack()
        lRight = ttk.Label(self.fSideRight, text='Right panel')
        lRight.pack()
        
        #create the scrollable canvas
        fResultsArea = Frame(fMain, bg='aqua')
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
        
        #use the new db utils
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
        #self.getRecentRaceFile()
        self.showRecentRace()
        
    def getRecentFinishFile(self):
        fileList = getFileList(getCurrentFilesFolder())
        if len(fileList) < 1:
            #print('no recent files found')
            return False
        #for f in fileList: print(f.title())
        print('most recent file: ', fileList[0])
        #recentRace = json.dumps(getJSONFinishData(fileList[0]), indent=2)
        #print(recentRace)
        recentRaceData = getJSONFinishData(fileList[0])
        return recentRaceData
    
    def getSortedRaceData(self, raceNumber):
        raceInfo = self.getRecentFinishFile()
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
    
    def EditEntry(self, i):
        print('test', i)
        
    def showRecentRace(self, raceNumber=1):
        raceInfo = self.getSortedRaceData(raceNumber)
        if not raceInfo: return

        #padding for the results cells
        racePadX = (4,4)
        racePadY = (2,2)

        #icon
        #editIcon = PhotoImage(file='images/edit20.png') #must use self on PhotoImage
        #weird, but necessary
        #lEditIcon = ttk.Label(image=editIcon)
        #lEditIcon.image = editIcon
                      
        #show race title
        lRaceTitle = ttk.Label(self.fResults, text=raceInfo['name'], style='Def12Bold.TLabel')
        lRaceTitle.grid(row=0, column=0, columnspan=8, sticky=W)

        #show race number
        lRaceNum = ttk.Label(self.fResults, text='{}{} start'.format(raceNumber, numSuffix(raceNumber)))
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

        #display the results for each boat
        startRow = 4
        for i,d in enumerate(raceInfo['data']):
           lPos = ttk.Label(self.fResults, text=i+1, anchor=W)
           lPos.grid(row=i+startRow, column=0, sticky=E, padx=racePadX, pady=racePadY)

           lPos = ttk.Label(self.fResults, text=d['class'], anchor=W)
           lPos.grid(row=i+startRow, column=1, sticky=W, padx=racePadX, pady=racePadY)

           lPos = ttk.Label(self.fResults, text=d['sailnum'], anchor=W)
           lPos.grid(row=i+startRow, column=2, sticky=W, padx=racePadX, pady=racePadY)

           lPos = ttk.Label(self.fResults,
                    text='{:02}:{:02}:{:02}'.format(
                        d['clock']['hh'],
                        d['clock']['mm'],
                        d['clock']['ss'],
                    ) if d['status'] == STATUS_FINISHED else d['status'],
                    anchor=W
                )
           lPos.grid(row=i+startRow, column=3, sticky=W, padx=racePadX, pady=racePadY)

           lPos = ttk.Label(
               self.fResults,
               text=d['rating'],
               anchor=W
            )
           lPos.grid(row=i+startRow, column=4, sticky=E, padx=racePadX, pady=racePadY)
           
           #add an edit button
           #bEdit = ttk.Button(self.fResults, image=editIcon)
           #bEdit.grid(row=i+startRow, column=5, padx=racePadX, pady=0)
           #bEdit = ttk.Checkbutton(self.fResults, text='')
           #bEdit.grid(row=i+startRow, column=5, padx=racePadX, pady=0)
           bEditValue = StringVar()
           bEdit = ttk.Radiobutton(self.fResults, text='', variable=bEditValue, command=lambda x = i: self.EditEntry(x))
           bEdit.grid(row=i+startRow, column=5, padx=racePadX, pady=0)
           