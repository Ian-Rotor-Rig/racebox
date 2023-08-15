
from tkinter import ALL, BOTH, DISABLED, LEFT, N, NONE, RIGHT, W, Y, Button, Canvas, Frame, Label, PhotoImage, Scrollbar, ttk
from tkinter.font import BOLD, Font
from tkinter.scrolledtext import ScrolledText
from rbconfig import RaceboxConfig

class ExtrasInterface:
    
    def __init__(self, fControl: ttk.Frame, relay):
        self.countdownActive = False
        self.relay = relay
        self.config = RaceboxConfig()
        self.on2Off = float(self.config.get('Signals', 'defaultOn2Off'))
        
        #fonts
        self.fontTitle = Font(weight=BOLD)

		#create internal frames
        self.fc = fControl
        fExtras = Frame(self.fc)
        fExtras.pack(expand=True, fill=BOTH)
        
        #add flag section
        self.__addFlagsSection(fExtras)
        
    def __addFlagsSection(self, f):
        flags = [
            [
                'flags/P-prep96.png',
                'Preparatory',
                '5 minutes to the start (10-5-Go) or 4 minutes (5-4-1-Go)',
                0
            ],
            [
                'flags/X-single-recall96.png',
                'Over Start Line',
                'Some boats were over the start line and must restart',
                1
            ],
            [
                'flags/FP-general-recall96.png',
                'General Recall',
                'All boats must return to start area',
                2
            ],
            [
                'flags/S-shorten96.png',
                'Shorten Course',
                'After the next mark, boats must head for the finish line',
                2
            ],
            [
                'flags/C-change-course96.png',
                'Course Change',
                'The next mark has been moved - repeated sound signals should be made',
                0
            ],
            [
                'flags/AP-postpone96.png',
                'Postpone',
                'Race start is postponed but a new start is likely soon',
                2
            ],
            [
                'flags/N-abandon96.png',
                'Abandon',
                'The race is abandoned, often (but not always) due to bad weather',
                3
            ]
        ]
        flagsSectionFrame = Frame(f)
        flagsSectionFrame.pack(fill=BOTH, expand=True, anchor=W, padx=4)
        
        lFlagsTitle = Label(flagsSectionFrame, text='Flags and Sound Signals', font=self.fontTitle)
        lFlagsTitle.pack(anchor=W, padx=5, pady=10)
        
        flagsFrame = Frame(flagsSectionFrame)
        flagsFrame.pack(fill=BOTH, expand=True, pady=10)
        
        #scrollable canvas and frame
        cv = Canvas(flagsFrame, highlightthickness=0)
        cv.pack(side=LEFT, expand=True, fill=BOTH)
        sb = Scrollbar(flagsFrame, command=cv.yview)
        sb.pack(side=RIGHT, fill=Y)   
        cv.configure(yscrollcommand = sb.set)     
        flagsListFrame = Frame(cv, padx=5, pady=5)
        cw = cv.create_window([0,0], window=flagsListFrame, anchor=N+W)
        cv.bind('<Configure>', lambda e: cv.configure(scrollregion=cv.bbox(ALL)))
        flagsListFrame.bind('<Configure>', lambda e: cv.itemconfigure(cw, width=e.width))

        for i,f in enumerate(flags):
            imgFlag = PhotoImage(file=f[0])
            lFlag = Label(flagsListFrame, image=imgFlag, justify=LEFT)
            lFlag.image = imgFlag
            lFlagInfoTitle = Label(flagsListFrame, text=f[1], justify=LEFT, font=self.fontTitle)
            lFlagInfo = Label(flagsListFrame, text=f[2], wraplength=275, justify=LEFT)
            lFlag.grid(row=i, column=0, sticky=W, pady=10)
            lFlagInfoTitle.grid(row=i, column=1, sticky=W, pady=10, padx=10)
            lFlagInfo.grid(row=i, column=2, sticky=W, pady=10, padx=10)
            if f[3] > 0:
                btnFlagHoot = Button(flagsListFrame, text=str(f[3])+' x Hoot', command= lambda h = f[3]: __flagHoot(h))
                btnFlagHoot.grid(row=i, column=3, sticky=W, padx=10)
            
        def __flagHoot(n):
            self.relay.onoff(self.fc, self.on2Off, n)
