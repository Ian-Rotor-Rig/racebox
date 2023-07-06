#from tkinter import *
from tkinter import ttk, PhotoImage, BOTTOM, X, Tk, Canvas
from racebox_control import RBSignalControl
from datetime import datetime

# Create the main window
mainWindow = Tk()
mainWindow.title('Racebox')
mainWindow.minsize(width=480, height=640)

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

# main screen
n = ttk.Notebook(mainWindow, style='Custom.TNotebook',padding='0 4 0 0')
n.pack(expand=True, fill='both') #do not add .pack to the frame creation line
controlFrame = ttk.Frame(n, style='Control.TFrame', padding='10 10 10 10')
setupFrame = ttk.Frame(n, style='Setup.TFrame')   # second page
n.add(controlFrame, text='Signal Control')
n.add(setupFrame, text='Setup')

#add widgets to control frame
screenControl = RBSignalControl(controlFrame)

#footer
footerFrame = ttk.Frame(mainWindow, style='Footer.TFrame')
footerFrame.pack(side=BOTTOM, fill=X)
footerCanvas = Canvas(footerFrame, bg="black", bd=0, width=60, height=60, highlightthickness=0)
footerCanvas.grid(column=0, row=0)
rotorRigLogoSmall = PhotoImage(file='sail50.png')
footerCanvas.create_image(2,2, anchor='nw', image=rotorRigLogoSmall)

rrLabel = ttk.Label(
    footerFrame,
    text='Rotor-Rig.com',
    foreground='darkorange',
    background='black',
    font=('Sans-Serif', 12)
)
rrLabel.grid(column=1,row=0,padx=(0,50))

timeLabel = ttk.Label(
    footerFrame,
    text='Time',
    foreground='lime',
    background='black',
    font=('Monospace', 14, 'bold')
    )
timeLabel.grid(column=2,row=0)

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
