from tkinter import Button, Frame, Label, Spinbox, StringVar, Variable, ttk

class RBSignalControl:
	def __init__(self, fControl: ttk.Frame):
		#self.fControl = fControl

		#create disposable frames
		fMain = Frame(fControl)
		fMain.pack(expand=True, fill='both')
		fCountdown = Frame(fMain)
		#fCountdown.forget()
		fSigConfig = Frame(fMain)
		fSigConfig.pack(expand=True, fill='both')
		fBtnPanel = Frame(fControl)
		fBtnPanel.pack(expand=True, fill='both')
  
		initConfigInterface(fSigConfig)
		initCountdownInterface(fCountdown)  

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
				fSigConfig.pack(expand=True, fill='both')
				startBtn.config(text='Start Countdown')
				self.countdownActive = False
			else:
				fSigConfig.forget()
				fCountdown.pack(expand=True, fill='both')
				startBtn.config(text='Stop Countdown')
				self.countdownActive = True
		startBtn = Button(fBtnPanel, text='Start Countdown', command=__countdownStart)
		startBtn.grid(column=0,row=0,sticky='se')
		fBtnPanel.grid_columnconfigure(0, weight=1)
		fBtnPanel.grid_rowconfigure(0, weight=1)
  
def initCountdownInterface(f: ttk.Frame):
	someLabel = Label(
		f,
		text='Countdown Screen'
	)
	someLabel.grid(column=0,row=0,sticky='w') #, pady=(15, 0))


def initConfigInterface(f: ttk.Frame):
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

	# start signals type
	startSigLabel = Label(
		f,
		text='Start Signals'
	)
	startSigLabel.grid(column=0,row=5,sticky='w', pady=(15, 0))

	startSigValues = ['10-5-Go', '5-4-1-Go']
	startSigEntry = ttk.Combobox(f, values=startSigValues, state='readonly')
	startSigEntry.set(startSigValues[0])
	startSigEntry.grid(column=0,row=6,sticky='w')