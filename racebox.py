from tkinter import (TOP, IntVar, Menu, font, messagebox, ttk, PhotoImage,
	BOTTOM, X, BOTH, Tk, Canvas, W,E,NW, LEFT, RIGHT)
from lib.rbsignals2 import Signals2Interface
from lib.rbfinishtimes import FinishTimesInterface
from lib.rbsignals import SignalsInterface
from datetime import datetime
from lib.rbserial import USBSerialRelay
from lib.rbhid import USBHIDRelay
from lib.rbconfig import RaceboxConfig

# Create the main window
mainWindow = Tk()
mainWindow.title('Racebox')
mainWindow.minsize(width=1000, height=500)

#default font
default_font = font.nametofont('TkDefaultFont')
default_font.configure(size=12)
text_font = font.nametofont('TkTextFont')
text_font.configure(size=12)
menu_font = font.nametofont('TkMenuFont')
menu_font.configure(size=12)

# window icon
icon = PhotoImage(file='images/racebox192.png')
mainWindow.iconphoto(False, icon)

#main menu
topMenu = Menu(mainWindow)
mainWindow.config(menu=topMenu)

# header colour
hdrColour = 'thistle'
hdrColourText = 'darkslategrey'
ftrColour = 'black'

# Styles
s = ttk.Style()
#s.theme_use('alt')
s.configure('Control.TFrame', borderwidth=4, relief='flat')
s.configure('Setup.TFrame', borderwidth=4, relief='flat')
s.configure('Header.TFrame', background=hdrColour)
s.configure('Footer.TFrame', background=ftrColour)
s.configure('Custom.TNotebook', tabposition='ne', background='indigo')
s.configure('Results.TNotebook', tabposition='se', background='indigo')
s.configure('TNotebook.Tab', background='mediumaquamarine', padding=[8,4])
s.configure('Custom.TButton', background='silver', padding=(8,8,8,6)) #left top right bottom 
s.configure('CustomSmall.TButton', background='silver', padding=(2,2,2,1)) #left top right bottom 
s.configure('H12Bold.TLabel', font=('Helvetica','12', 'bold'))
s.configure('Def12Bold.TLabel', font=('TkDefaultFont','12', 'bold'))
s.configure('CourierLargeBold.TLabel', font=('Courier','16', 'bold'))

#general config
config = RaceboxConfig()

#USB relay
raceboxRelay = USBHIDRelay()
serialPort = config.get('Relays', 'serialRelayPort')
try:
    serialDriver = config.get('Relays', 'serialdriver')
except:
    serialDriver = False
if not raceboxRelay.active: raceboxRelay = USBSerialRelay(serialPort) if not serialDriver else USBSerialRelay(serialPort, serialDriver)

#header
headerFrame = ttk.Frame(mainWindow, style='Header.TFrame')
headerCanvas = Canvas(headerFrame, bg=hdrColour, bd=0, width=50, height=50, highlightthickness=0)
headerCanvas.pack(side=LEFT, ipady=2)
rbLogoSmall = PhotoImage(file='images/racebox50.png')
headerCanvas.create_image(2,2, anchor=NW, image=rbLogoSmall)

#icon in header to show if a USB relay is connected/recognised
connectCanvas = Canvas(headerFrame, bg=hdrColour, bd=0, width=25, height=25, highlightthickness=0)
connectCanvas.pack(side=RIGHT, padx=(0,10))
connectIcon = PhotoImage(file='images/relay-on.png') if raceboxRelay.active else PhotoImage(file='images/relay-off.png')
connectCanvas.create_image(0,0, anchor=NW, image=connectIcon)

hdrLabel = ttk.Label(
    headerFrame,
    text='Racebox',
    foreground=hdrColourText,
    background=hdrColour,
    font=('Helvetica', 14, 'bold')
)
hdrLabel.pack(side=LEFT)

# main screen
n = ttk.Notebook(mainWindow, style='Custom.TNotebook',padding='0 4 0 0')
signalsFrame = ttk.Frame(n, style='Control.TFrame', padding='10 10 10 10')
manualSignalsFrame = ttk.Frame(n, style='Control.TFrame') #now the manual signals tab
finishTimesFrame = ttk.Frame(n, style='Control.TFrame')
resultsFrame = ttk.Frame(n, style='Control.TFrame')

n.add(signalsFrame, text='Auto Signals') #tab 0
n.add(manualSignalsFrame, text='Manual Signals') #tab 1
n.add(finishTimesFrame, text='Finish Times') #tab 2
n.add(resultsFrame, text='Results') #tab 3
n.tab(3, state='hidden')

#add widgets to each control frame
SignalsInterface(signalsFrame, raceboxRelay)
Signals2Interface(manualSignalsFrame, raceboxRelay)
ft = FinishTimesInterface(finishTimesFrame, resultsFrame, raceboxRelay)

#control notebook tabs visibility
def setNbTabs(nb: ttk.Notebook, adv: bool):
    if adv:
        nb.tab(3, state='normal')
    else:
        nb.tab(3, state='hidden')

#define menu options for topMenu
#file menu
fileMenu = Menu(topMenu, tearoff=0)
topMenu.add_cascade(label='File', menu=fileMenu)
fileMenu.add_command(label='Exit', command=mainWindow.quit)
#view menu
viewMenu = Menu(topMenu, tearoff=0)
topMenu.add_cascade(label='View', menu=viewMenu)
advValue = IntVar(value=0)
viewMenu.add_checkbutton(
    label='Advanced Options',
    variable=advValue,
    command=lambda: setNbTabs(n, True if advValue.get() == 1 else False)
    )
#help menu
helpMenu = Menu(topMenu, tearoff=0)
topMenu.add_cascade(label='Help', menu=helpMenu)
helpMenu.add_command(label='Documentation',
                     command=lambda: messagebox.showinfo(
                         'Documentation',
                         'Help for Racebox is at:\n' + 
                         'https://github.com\n/rotor-rig/racebox/wiki'
                         ))
helpMenu.add_command(label='About',
                     command=lambda: messagebox.showinfo(
                         'About',
                         'Racebox is a free program\n' +
                         'Designed by Ian Cherrill\n' +
                         'Website: rotor-rig.com/racebox\n' +
                         'Contact: info@rotor-rig.com'
                         ))

#footer
footerFrame = ttk.Frame(mainWindow, style='Footer.TFrame')
footerFrame.grid_columnconfigure(0, weight=1)
footerFrame.grid_columnconfigure(1, weight=1)
footerFrame.grid_columnconfigure(2, weight=1)

logoFrame = ttk.Frame(footerFrame, style='Footer.TFrame')
logoFrame.grid(column=0,row=0,padx=(0,0), sticky=W)

footerCanvas = Canvas(logoFrame, bg="black", bd=0, width=60, height=60, highlightthickness=0)
footerCanvas.grid(column=0,row=0,padx=(0,0))
rotorRigLogoSmall = PhotoImage(file='images/sail50.png')
footerCanvas.create_image(2,2, anchor=NW, image=rotorRigLogoSmall)

rrLabel = ttk.Label(
    logoFrame,
    text='Rotor-Rig.com',
    foreground='darkorange',
    background='black',
    font=('Sans-Serif', 12)
)
rrLabel.grid(column=1,row=0,padx=(0,0))

timeLabel = ttk.Label(
    footerFrame,
    text='Time',
    foreground='lime',
    background='black',
    font=('Monospace', 14, 'bold')
)
timeLabel.grid(column=1,row=0,padx=(0,0))

#pack the main screen
#packing the header and footer before the middle
#means the middle will be reduced first when window is resized
headerFrame.pack(side=TOP, fill=X)
footerFrame.pack(side=BOTTOM, fill=X)
n.pack(expand=True, fill=BOTH)

def __hootSound():
    on2Off = float(config.get('Signals', 'defaultOn2Off'))
    raceboxRelay.onoff(mainWindow, on2Off)

hootBtn = ttk.Button(footerFrame, text='Hoot', command=__hootSound, style='Custom.TButton')
hootBtn.grid(column=2,row=0, sticky=E, padx=(0,10))

def clockLoop():
    #time
    now = datetime.now()
    nowText = now.strftime('%H:%M:%S')
    timeLabel.config(text=nowText)       
    mainWindow.after(1000, clockLoop)

# Start the timing loop
clockLoop()

# Run forever!
mainWindow.mainloop()
