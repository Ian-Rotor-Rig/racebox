from datetime import datetime
import os
from tkinter import BOTH, BOTTOM, CENTER, END, LEFT, NW, RIGHT, TOP, S, W, X, Y, Frame, LabelFrame, Scrollbar, ttk
import tkinter as tk
from rbconfig import RaceboxConfig

class FinishTimesInterface:
    def __init__(self, fControl: ttk.Frame, relay):
        self.pos = 1
        self.relay = relay
        self.config = RaceboxConfig()
        
        self.fc = fControl
        
        f = Frame(self.fc)
        f.pack(expand=True, fill=BOTH)
        
        #frame for text box
        tf = Frame(f, padx=25, pady=25)
        tf.pack(side=LEFT, fill=Y)
        #text box
        self.txtboxFinish = tk.Text(tf, width=40)
        self.txtboxFinish.pack(side=LEFT, fill=Y)
        self.txtboxFinish.tag_configure('bold', font=('monospace', 11, 'bold'))
        #sans-serif
        
        #scrollbar
        scrollFinishBox = Scrollbar(tf)
        scrollFinishBox.pack(side=RIGHT, fill=Y)
        scrollFinishBox.config(command=self.txtboxFinish.yview)
        self.txtboxFinish.config(yscrollcommand=scrollFinishBox.set)
        
        #right frame
        rf = Frame(f)
        rf.pack(side=LEFT, ipadx=25, fill=Y)

        #finish button
        btnFinish = ttk.Button(rf, text="Finish", command=self.finishAction)
        btnFinish.pack(side=TOP, anchor=W, pady=50)

        #right bottom frame
        rbf = LabelFrame(rf, text='Use Between Races')
        rbf.pack(side=BOTTOM, anchor=W, pady=25, ipady=25)
        #save as file button
        btnReset = ttk.Button(rbf, text="Save Finishes", command=self.saveToTxtFileAction)
        btnReset.pack(expand=True, anchor=CENTER)          
        #reset counter button
        btnReset = ttk.Button(rbf, text="Reset Finish Box", command=self.resetCounterAction)
        btnReset.pack(expand=True, anchor=CENTER)  
          
    def finishAction(self):
        on2Off = float(self.config.get('Signals', 'finishOn2Off'))
        self.relay.onoff(self.fc, on2Off)
        now = datetime.now()
        self.txtboxFinish.insert(END, '\n{:>3}'.format(self.pos), 'bold')
        self.txtboxFinish.insert(END, '  {} '.format(now.strftime('%H:%M:%S')))
        self.pos += 1
        
    def resetCounterAction(self):
        self.txtboxFinish.delete('1.0', END)
        self.pos = 1
        
    def saveToTxtFileAction(self):
        now = datetime.now()
        useDefaultFolder = True if self.config.get('Files', 'finshFileUseDefaultFolder').lower() == 'true' else False
        defaultFolder = os.path.expanduser('~') if useDefaultFolder else ''
        saveFileName = self.config.get('Files','finishFileFolder') + 'finishes-{}.txt'.format(now.strftime('%Y%m%d-%H%M'))
        try:
            with open (defaultFolder + saveFileName, 'w+') as file:
                file.write(self.txtboxFinish.get('1.0', END))
                file.close()
                tk.messagebox.showinfo('Save File', 'File {}{} saved'.format(defaultFolder, saveFileName))
        except:
            tk.messagebox.showerror('Save File Error', 'Could not save the file {}{}'.format(defaultFolder, saveFileName))
