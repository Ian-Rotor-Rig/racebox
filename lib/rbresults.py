#import json
from tkinter import BOTH, E, RIGHT, W, Y, Frame, ttk
from lib.rbdb import rbDb
from lib.rbutility import (
        MONTH_ABBREV, 
        MSEC_IN_DAY, MSEC_IN_HOUR, MSEC_IN_MINUTE,
        STATUS_FINISHED,
        dayPostfix,
        getCurrentFilesFolder, getFileList, getJSONFinishData,
    )

class ResultsInterface():
       
    def __init__(self, fControl: ttk.Frame):
        self.fHdr = Frame(fControl, bg='orange')
        self.fMain = Frame(fControl, bg='aqua')
        self.fSideRight = Frame(fControl, bg='palegreen')
        self.fSideRight.pack(side=RIGHT, expand=False, fill=Y, padx=(10,2), pady=(2,2))
        self.fHdr.pack(expand=False, fill=BOTH, padx=(10,10), pady=(10,0))
        self.fMain.pack(expand=False, fill=BOTH, padx=(10,0), pady=(10,2))
        
        #identify frames
        lHdr = ttk.Label(self.fHdr, text='Header')
        lHdr.pack()
        #lMain = ttk.Label(fMain, text='Main panel')
        #lMain.pack()
        lRight = ttk.Label(self.fSideRight, text='Right panel')
        lRight.pack()
        
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
        
    def showRecentRace(self, raceNumber=1):
        racePadX = 4
        racePadY = 2
        tableHdr = ['', 'Class', 'Sail', 'Finish', 'Rating']
        raceInfo = self.getSortedRaceData(raceNumber)
        if not raceInfo: return
        raceTitle = ttk.Label(self.fMain, text=raceInfo['name'])
        raceTitle.grid(row=0, column=0, columnspan=8, sticky=W)
        dateText = '{}{} {} {}'.format(
                raceInfo['date']['day'],
                dayPostfix(raceInfo['date']['day']),
                MONTH_ABBREV[raceInfo['date']['month'] - 1],
                raceInfo['date']['year'],
            )
        raceDate = ttk.Label(self.fMain, text=dateText)
        raceDate.grid(row=1, column=0, columnspan=8, sticky=W)
        for i,h in enumerate(tableHdr):
            lHdr = ttk.Label(self.fMain, text=h, anchor=W)
            lHdr.grid(row=2, column=i, sticky=W, padx=racePadX, pady=racePadY)
        for i,d in enumerate(raceInfo['data']):
           lPos = ttk.Label(self.fMain, text=i+1, anchor=W)
           lPos.grid(row=i+3, column=0, sticky=E, padx=racePadX, pady=racePadY)

           lPos = ttk.Label(self.fMain, text=d['class'], anchor=W)
           lPos.grid(row=i+3, column=1, sticky=W, padx=racePadX, pady=racePadY)

           lPos = ttk.Label(self.fMain, text=d['sailnum'], anchor=W)
           lPos.grid(row=i+3, column=2, sticky=W, padx=racePadX, pady=racePadY)

           lPos = ttk.Label(self.fMain,
                    text='{:02}:{:02}:{:02}'.format(
                        d['clock']['hh'],
                        d['clock']['mm'],
                        d['clock']['ss'],
                    ) if d['status'] == STATUS_FINISHED else d['status'],
                    anchor=W
                )
           lPos.grid(row=i+3, column=3, sticky=W, padx=racePadX, pady=racePadY)

           lPos = ttk.Label(
               self.fMain,
               text=d['rating'],
               anchor=W
            )
           lPos.grid(row=i+3, column=4, sticky=W, padx=racePadX, pady=racePadY)
           