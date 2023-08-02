from datetime import datetime, timedelta
import json
from tkinter import (Button, Frame, Label, Spinbox, StringVar,
	Variable, ttk, BOTH, NW, W)
from rbconfig import defaultSequence

class SignalsInterface:
	sequenceList = [
        {'name': '10-5-Go', 'interval': 5, 'warning': [-10,-5]},
        {'name': '5-4-1-Go', 'interval': 5, 'warning': [-5,-4,-1]},
        {'name': '3-2-1-Go', 'interval': 3, 'warning': [-3,-2,-1]}
    ]
 
	SIGNAL_OLD = 1
	SIGNAL_NOW = 0
	SIGNAL_FUTURE = -1
	SIGNAL_MAX_AGE = 1500 #ms
	
	def __init__(self, fControl: ttk.Frame, relay):

		self.countdownActive = False
		self.relay = relay

		#create internal frames
		fMain = Frame(fControl)
		fMain.pack(expand=False, fill=BOTH)

		self.fCountdown = Frame(fMain)
		
		self.fSigConfig = Frame(fMain)
		self.fSigConfig.pack(expand=False, fill=BOTH)
		
		fBtnPanel = Frame(fControl)
		fBtnPanel.pack(expand=False, fill=BOTH)
		
		self.startBtn = Button(fBtnPanel, text='Start Countdown', command=self.__changeCountdownStatus)
		self.startBtn.pack(anchor=NW, pady=(40,0))
  
		self.__initConfigInterface(self.fSigConfig)
		self.__initCountdownInterface(self.fCountdown)
		
	#the start countdown button
  		#private method 
	#tkraise on a frame to show/hide
	#see #https://www.pythontutorial.net/tkinter/tkraise/
	#https://coderslegacy.com/python/switching-between-tkinter-frames-with-tkraise/
	#though just using forget and pack seems to be fine here
	def __updateCountdownBtnPanel(self):
		if self.countdownActive:
			self.fSigConfig.forget()
			self.fCountdown.pack(expand=False, fill=BOTH)
			self.startBtn.config(text='Stop Countdown')
		else:
			self.fCountdown.forget()
			self.fSigConfig.pack(expand=False, fill=BOTH)
			self.startBtn.config(text='Start Countdown')
   
	def __changeCountdownStatus(self):
		if self.countdownActive: self.__stopCountdown()
		else: self.__startCountdown()
   
	def __startCountdown(self):
		self.countdownActive = True
		self.__countdown()
		self.__updateCountdownBtnPanel()
   
	def __stopCountdown(self):
		self.countdownActive = False
		self.__updateCountdownBtnPanel()
  
	def __countdown(self):
		if not self.relay.active: print('no active relay')
		signalsConfig = {
			'name': self.selectedSequenceName.get(),
			'starts': int(self.startsCount.get()),
			'startHour': int(self.hhValue.get()),
			'startMinute': int(self.mmValue.get())
        }
		[signals, starts] = self.__getSignalList(signalsConfig)
		#print('countdown start')
		#print('signals: ', signals)
		#print('starts: ', starts)
		self.__countdownLoop(signals, starts, len(starts), signalsConfig['name'])
   
	def __countdownLoop(self, signals, starts, startCount, seqName):
		if not self.countdownActive: return
		if len(signals) < 1: return
		#print('countdown active')
		tooLate = signals[0] + timedelta(milliseconds=SignalsInterface.SIGNAL_MAX_AGE)
		chk = self.__checkNextSignal(signals[0], tooLate)
		if chk == SignalsInterface.SIGNAL_NOW:
			self.relay.onoff()
		#print(chk, signals[0])
		if chk == SignalsInterface.SIGNAL_OLD or chk == SignalsInterface.SIGNAL_NOW:
			if signals[0] == starts[0]: starts.pop(0)
			rm = signals.pop(0)
			#print('removed ', rm)
		self.__updateCountdownDisplay(signals, starts, startCount, seqName)
		self.fCountdown.after(500, self.__countdownLoop, signals, starts, startCount, seqName)
  
	def __checkNextSignal(self, signal, tooLate):
		#print('check if signal is due')
		now = datetime.now()
		if now >= tooLate: return SignalsInterface.SIGNAL_OLD
		if signal < now < tooLate: return SignalsInterface.SIGNAL_NOW
		return SignalsInterface.SIGNAL_FUTURE
   
	def __getSignalList(self, config):
		# print(config)
		sequenceIndex = -1
		for sequenceIndex, item in enumerate(SignalsInterface.sequenceList):
			if item['name'] == config['name']: break
		if sequenceIndex == -1: return []
		# print('selected sequence ' + json.dumps(SignalsInterface.sequenceList[sequenceIndex]))
		signalList = []
		startList = []
		now = datetime.now()
		# print(now)
		firstStart = now.replace(hour=config['startHour'], minute=config['startMinute'], second=0, microsecond=0)
		#firstWarning = firstStart - timedelta(minutes=5)
		#print(firstStart)
		#print(firstWarning)
  		#
		# loop through the warnings and add to array
  		# then add first start
		# if more than one start the parent loop then does the same
  		# for each subesuent start
		# we need separate arrays for starts and all signals OR
		# use a dict to show which signal is a start and which is a warning
		#
		currentStart = firstStart
		startInterval = SignalsInterface.sequenceList[sequenceIndex]['interval']
		for start in range(config['starts']):
			for warning in SignalsInterface.sequenceList[sequenceIndex]['warning']:
				warningTime = currentStart - timedelta(minutes=abs(warning))
				if warningTime not in signalList: signalList.append(warningTime)
			if currentStart not in signalList:
				signalList.append(currentStart)
				startList.append(currentStart)
			currentStart = currentStart + timedelta(minutes=startInterval)
    
		# print('signals ', signalList)
		# print('starts', startList)
		# when removing signals - can check to see if the signal being removed is also in starts and remove it from there too

		return [signalList, startList]

		# unpack like this: [signals, starts] = getSignalList(config)
		# the js rest operator ... is * in Python
		# so the first/last start would be [firstStart, *otherStarts, lastStart] = starts 

	def __updateCountdownDisplay(self, signals, starts, startCount, seqName):
		self.lNumberOfStartsValue.config(text=startCount)
		if len(signals) < 1:
			self.lTime2Start.config(text='00:00:00')
			self.lNextStartTime.config(text='00:00:00')
			self.lLastStartValue.config(text='00:00:00')
			return
		self.lNextStartTime.config(text="{:%H:%M:%S}".format(starts[0]))
		self.lLastStartValue.config(text="{:%H:%M:%S}".format(starts[-1]))
		now = datetime.now()
		if now < starts[0]:
			time2Start = starts[0] - now
			t2Shours, remainder = divmod(time2Start.total_seconds(), 3600)
			t2Sminutes, t2Sseconds = divmod(remainder, 60)
			self.lTime2Start.config(text='{:02}:{:02}:{:02}'.format(int(t2Shours), int(t2Sminutes), int(t2Sseconds)))
		else:
			self.lTime2Start.config(text='00:00:00')
		self.lSequenceValue.config(text=seqName)
      
	def __initCountdownInterface(self, f: ttk.Frame):
		#grid options
		f.rowconfigure(0, minsize=50)
		f.rowconfigure(1, minsize=50)
		f.rowconfigure(2, minsize=40)
		f.rowconfigure(3, minsize=40)
		f.rowconfigure(4, minsize=40)
		f.columnconfigure(0, pad=25)

		#next start time label
		lNextStartTxt = Label(
			f,
			text='Next Start Time'
		)
		lNextStartTxt.grid(column=0,row=0,sticky='w')
		
		self.lNextStartTime = Label(
			f,
			text='00:00:00'
		)
		self.lNextStartTime.configure(
			font='Monospace 14 bold',
			bg='plum',
			padx=12,
			pady=8
		)
		self.lNextStartTime.grid(column=1,row=0)
		
		#countdown to next start label
		lTime2StartTxt = Label(
			f,
			text='Time To Start'
		)
		lTime2StartTxt.grid(column=0,row=1,sticky='w')
		
		self.lTime2Start = Label(
			f,
			text='00:00:00'
		)
		self.lTime2Start.configure(
			font='Monospace 14 bold',
			bg='orange',
			padx=12,
			pady=8
		)
		self.lTime2Start.grid(column=1,row=1)
		
		#number of starts plain label
		lNumberOfStartsTxt = Label(
			f,
			text='Number Of Starts'
		)
		lNumberOfStartsTxt.grid(column=0,row=2,sticky='w')		
		self.lNumberOfStartsValue = Label(
			f,
			text='0',
			anchor=W
		)
		self.lNumberOfStartsValue.grid(column=1,row=2,sticky='w')	
		
		#final start time plain label
		lLastStartTxt = Label(
			f,
			text='Final Start Time'
		)
		lLastStartTxt.grid(column=0,row=3,sticky='w')		
		self.lLastStartValue = Label(
			f,
			text='00:00:00',
			anchor=W
		)
		self.lLastStartValue.grid(column=1,row=3,sticky='w')	
  
		#start sequence
		lSequenceTxt = Label(
			f,
			text='Sequence'
		)
		lSequenceTxt.grid(column=0,row=4,sticky='w')		
		self.lSequenceValue = Label(
			f,
			text='',
			anchor=W
		)
		self.lSequenceValue.grid(column=1,row=4,sticky='w')	  
		
		#general recall/add start button
		lAddStartTxt = Label(
			f,
			text='General Recall'
		)
		lAddStartTxt.grid(column=0,row=5,sticky='w')		
		lAddStartBtn = Button(
			f,
			text='Add Start',
			anchor=W
		)
		lAddStartBtn.grid(column=1,row=5,sticky='w')	

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
		self.hhValue = Variable(value='14')
		hhEntry = Spinbox(fStartTime, from_=0, to=23, textvariable=self.hhValue, format="%02.0f", state='readonly')
		hhEntry.pack(side='left')
		hhEntry.config(width=3)
		self.mmValue = Variable(value='30')
		mmEntry = Spinbox(fStartTime, from_=0, to=59, textvariable=self.mmValue, format="%02.0f", state='readonly')
		mmEntry.pack(side='left', padx=(4, 0))
		mmEntry.config(width=3)
	
		# number of starts
		startsLabel = Label(
			f,
			text='Number Of Starts'
		)
		startsLabel.grid(column=0,row=3,sticky='w', pady=(15, 0))
	
		self.startsCount = StringVar(value=1)
		startsEntry = Spinbox(f, from_=1, to=33, textvariable=self.startsCount, state='readonly')
		startsEntry.grid(column=0,row=4,sticky='w')
		startsEntry.config(width=2)
	
		# start sequence type
		startSigLabel = Label(
			f,
			text='Start Sequence'
		)
		startSigLabel.grid(column=0,row=5,sticky='w', pady=(15, 0))
  
		sequenceNames = []
		for s in SignalsInterface.sequenceList: sequenceNames.append(s['name'])
		### https://www.pythontutorial.net/tkinter/tkinter-combobox/
		self.selectedSequenceName = StringVar()
		startSigEntry = ttk.Combobox(f, values=sequenceNames, textvariable=self.selectedSequenceName, state='readonly')
		self.selectedSequenceName.set(sequenceNames[defaultSequence])
		startSigEntry.grid(column=0,row=6,sticky='w')			
			