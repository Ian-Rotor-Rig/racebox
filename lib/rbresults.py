from tkinter import BOTH, RIGHT, Y, Frame, ttk

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
        