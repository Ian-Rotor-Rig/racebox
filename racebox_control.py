from tkinter import (Button, Frame, Label, Spinbox, StringVar,
	Variable, ttk, BOTH, X, Y, NW)

class RBSignalControl:
	def __init__(self, fControl: ttk.Frame):
		#self.fControl = fControl

		#create disposable frames
		fMain = Frame(fControl)
		fMain.pack(expand=False, fill=BOTH)
		fCountdown = Frame(fMain)
		#fCountdown.forget()
		fSigConfig = Frame(fMain)
		fSigConfig.pack(expand=False, fill=BOTH)
		fBtnPanel = Frame(fControl)
		fBtnPanel.pack(expand=False, fill=BOTH)
  
		self.__initConfigInterface(fSigConfig)
		self.__initCountdownInterface(fCountdown)  

		self.countdownActive = False

		#the start countdown button
  		#private method 
		#tkraise on a frame to show/hide
		#see #https://www.pythontutorial.net/tkinter/tkraise/
		#https://coderslegacy.com/python/switching-between-tkinter-frames-with-tkraise/
		#though just using forget and pack seems to be fine here
		def __countdownStart():
			if self.countdownActive:
				fCountdown.forget()
				fSigConfig.pack(expand=False, fill=BOTH)
				startBtn.config(text='Start Countdown')
				self.countdownActive = False
			else:
				fSigConfig.forget()
				fCountdown.pack(expand=False, fill=BOTH)
				startBtn.config(text='Stop Countdown')
				self.countdownActive = True
				
		startBtn = Button(fBtnPanel, text='Start Countdown', command=__countdownStart)
		startBtn.pack(anchor=NW, pady=(25,0))
  
	def __initCountdownInterface(self, f: ttk.Frame):
		lNextStartTime = Label(
			f,
			text='00:00:00'
		)
		lNextStartTime.configure(font='Monospace 14 bold', bg='plum')
		lNextStartTime.grid(column=0,row=0,sticky='w') #, pady=(15, 0))
		#and then the time-to-next-start label


	def __initConfigInterface(self, f: ttk.Frame):
		# start time
		fStartTime = Frame(f)
		fStartTime.grid(column=0,row=0,sticky='w') 
		startTimeLabel = Label(
			fStartTime,
			text='First Start'
		)
		startTimeLabel.grid(column=0,row=0,sticky='w') 
	
		fStartTime = Frame(f)
		fStartTime.grid(column=0,row=1,sticky='w') 
		hhDefault = Variable(value='14')
		#hhEntry = Entry(fStartTime, textvariable=hhDefault)
		hhEntry = Spinbox(fStartTime, from_=0, to=23, textvariable=hhDefault, state='readonly')
		hhEntry.pack(side='left')
		hhEntry.config(width=3)
		mmDefault = Variable(value='30')
		mmEntry = Spinbox(fStartTime, from_=0, to=59, textvariable=mmDefault, state='readonly')
		mmEntry.pack(side='left', padx=(4, 0))
		mmEntry.config(width=3)
	
		# day context selector
		#fDayCtx = Frame(f, padx=10, pady=10)
		#fDayCtx.grid(column=0,row=2,sticky='w')
		#vDayCtx = IntVar()
		#vDayCtx.set(0)
		#vDayCtxValues = (('Today', 0), ('Tomorrow', 1), ('Now', 2))
		#for v in vDayCtxValues:
	#		r = Radiobutton(
	#    	fDayCtx,
	#		text=v[0],
	#		variable=vDayCtx,
	#		value=v[1]
	#   	)
	#		r.pack(side='left')
	#	
		# number of starts
		startsLabel = Label(
			f,
			text='Number Of Starts'
		)
		startsLabel.grid(column=0,row=3,sticky='w', pady=(15, 0))
	
		startsDefault = StringVar(value=1)
		startsEntry = Spinbox(f, from_=1, to=33, textvariable=startsDefault, state='readonly')
		startsEntry.grid(column=0,row=4,sticky='w')
		startsEntry.config(width=2)
	
		# start sequence type
		startSigLabel = Label(
			f,
			text='Start Sequence'
		)
		startSigLabel.grid(column=0,row=5,sticky='w', pady=(15, 0))
	
		startSigValues = ['10-5-Go', '5-4-1-Go']
		startSigEntry = ttk.Combobox(f, values=startSigValues, state='readonly')
		startSigEntry.set(startSigValues[0])
		startSigEntry.grid(column=0,row=6,sticky='w')
			
			
			
			