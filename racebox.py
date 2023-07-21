#from tkinter import *
from tkinter import (ttk, PhotoImage, Button, messagebox, Frame,
	BOTTOM, X,Y,BOTH, Tk, Canvas, W,E,N,S,NW, LEFT, RIGHT, CENTER)
from racebox_control import RBSignalControl
from datetime import datetime

# Create the main window
mainWindow = Tk()
mainWindow.title('Racebox')
mainWindow.minsize(width=500, height=500)

# window icon
icon = PhotoImage(file='racebox192.png')
mainWindow.iconphoto(False, icon)

# Styles
s = ttk.Style()
#s.theme_use('alt')
s.configure('Control.TFrame', borderwidth=4, relief='flat')
s.configure('Setup.TFrame', borderwidth=4, relief='flat')
s.configure('Footer.TFrame', background='black')
s.configure('Custom.TNotebook', tabposition='ne', background='darkgrey')
s.configure('StartTime.TLabel')
s.configure('StartCount.TLabel')

# main screen
n = ttk.Notebook(mainWindow, style='Custom.TNotebook',padding='0 4 0 0')
n.pack(expand=True, fill=BOTH) #do not add .pack to the frame creation line
signalFrame = ttk.Frame(n, style='Control.TFrame', padding='10 10 10 10')
setupFrame = ttk.Frame(n, style='Setup.TFrame')   # second page
n.add(signalFrame, text='Signals')
n.add(setupFrame, text='Setup')

#add widgets to control frame
screenControl = RBSignalControl(signalFrame)

#footer
footerFrame = ttk.Frame(mainWindow, style='Footer.TFrame')
footerFrame.pack(side=BOTTOM, fill=X)
footerFrame.grid_columnconfigure(0, weight=1)
footerFrame.grid_columnconfigure(1, weight=1)
footerFrame.grid_columnconfigure(2, weight=1)

logoFrame = ttk.Frame(footerFrame, style='Footer.TFrame')
logoFrame.grid(column=0,row=0,padx=(0,0), sticky=W)

footerCanvas = Canvas(logoFrame, bg="black", bd=0, width=60, height=60, highlightthickness=0)
footerCanvas.grid(column=0,row=0,padx=(0,0))
rotorRigLogoSmall = PhotoImage(file='sail50.png')
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

def __hootSound():
	messagebox.showinfo(title='Test hoot', message='Hoot!')
	#to do

hootBtn = Button(footerFrame, text='Hoot', command=__hootSound)
hootBtn.grid(column=2,row=0, sticky=E, padx=(0,10))

def loop():
    #time
    now = datetime.now()
    nowText = now.strftime('%H:%M:%S')
    timeLabel.config(text=nowText)
        
    # Schedule a call to `loop` in 500 milliseconds with t+1 as a parameter
    mainWindow.after(300, loop)

# Start the timing loop
loop()

# Run forever!
mainWindow.mainloop()
