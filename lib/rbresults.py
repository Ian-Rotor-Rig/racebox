from tkinter import BOTH, RIGHT, Y, Frame, ttk
from lib.rbdb import rbDb
from lib.rbutility import getCurrentFilesFolder, getFileList

class ResultsInterface():
       
    def __init__(self, fControl: ttk.Frame):
        fHdr = Frame(fControl, bg='orange')
        fMain = Frame(fControl, bg='aqua')
        fSideRight = Frame(fControl, bg='palegreen')
        fSideRight.pack(side=RIGHT, expand=False, fill=Y, padx=(10,2), pady=(2,2))
        fHdr.pack(expand=False, fill=BOTH, padx=(10,10), pady=(10,0))
        fMain.pack(expand=False, fill=BOTH, padx=(10,0), pady=(10,2))
        
        #identify frames
        lHdr = ttk.Label(fHdr, text='Header')
        lHdr.pack()
        lMain = ttk.Label(fMain, text='Main panel')
        lMain.pack()
        lRight = ttk.Label(fSideRight, text='Right panel')
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
        self.getLastRace()
        
    def getLastRace(self):
        fileList = getFileList(getCurrentFilesFolder())
        for f in fileList: print(f.title())
