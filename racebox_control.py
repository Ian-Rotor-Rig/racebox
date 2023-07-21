from tkinter import (Button, Frame, Label, Spinbox, StringVar,
	Variable, ttk, BOTH, X, Y, NW, W)

class RBSignalControl:
	
	def __init__(self, fControl: ttk.Frame):

		self.countdownActive = False

		#create internal frames
		fMain = Frame(fControl)
		fMain.pack(expand=False, fill=BOTH)

		self.fCountdown = Frame(fMain)
		
		self.fSigConfig = Frame(fMain)
		self.fSigConfig.pack(expand=False, fill=BOTH)
		
		fBtnPanel = Frame(fControl)
		fBtnPanel.pack(expand=False, fill=BOTH)
		
		self.startBtn = Button(fBtnPanel, text='Start Countdown', command=self.__updateCountdownBtnPanel)
		self.startBtn.pack(anchor=NW, pady=(40,0))
  
		self.__initConfigInterface(self.fSigConfig)
		self.__initCountdownInterface(self.fCountdown)  
		
	#the start countdown button
  		#private method 
	#tkraise on a frame to show/hide
	#see #https://www.pythontutorial.net/tkinter/tkraise/
	#https://coderslegacy.com/python/switching-between-tkinter-frames-with-tkraise/
	#though just using forget and pack seems to be fine here
	def __updateCountdownBtnPanel (self):
		if self.countdownActive:
			self.fCountdown.forget()
			self.fSigConfig.pack(expand=False, fill=BOTH)
			self.startBtn.config(text='Start Countdown')
			self.countdownActive = False
		else:
			self.fSigConfig.forget()
			self.fCountdown.pack(expand=False, fill=BOTH)
			self.startBtn.config(text='Stop Countdown')
			self.countdownActive = True
  
	def __initCountdownInterface(self, f: ttk.Frame):
		#grid options
		f.rowconfigure(1, minsize=75)
		f.columnconfigure(0, pad=25)

		#next start time label
		lNextStartTxt = Label(
			f,
			text='Next Start Time'
		)
		lNextStartTxt.grid(column=0,row=0,sticky='w')
		
		lNextStartTime = Label(
			f,
			text='00:00:00'
		)
		lNextStartTime.configure(
			font='Monospace 14 bold',
			bg='plum',
			padx=12,
			pady=8
		)
		lNextStartTime.grid(column=1,row=0)#,sticky='w')
		
		#countdown to next start label
		lTime2StartTxt = Label(
			f,
			text='Time To Start'
		)
		lTime2StartTxt.grid(column=0,row=1,sticky='w') #, pady=(50, 0))
		
		lTime2Start = Label(
			f,
			text='00:00:00'
		)
		lTime2Start.configure(
			font='Monospace 14 bold',
			bg='orange',
			padx=12,
			pady=8
		)
		lTime2Start.grid(column=1,row=1)#,sticky='w')
		
		#number of starts plain label
		lNumberOfStartsTxt = Label(
			f,
			text='Number Of Starts'
		)
		lNumberOfStartsTxt.grid(column=0,row=2,sticky='w')		
		lNumberOfStartsValue = Label(
			f,
			text='0',
			anchor=W
		)
		lNumberOfStartsValue.grid(column=1,row=2,sticky='w')	

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
			
			
			
			