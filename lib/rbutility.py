from datetime import datetime
import glob
import json
import os
import uuid

from lib.rbconfig import RaceboxConfig

ENTRY_FONT = 'Helvetica 12'
TITLE_FONT = 'Helvetica 12 bold'
FIXED_FONT = 'Courier 12'
FIXED_FONT_BOLD = 'Courier 12 bold'
FIXED_FONT_LARGE = 'Courier 14 bold'

MONTH_ABBREV = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

STATUS_FINISHED = 'Finished'
STATUS_CODES = ['RET', 'OCS', 'DSQ', 'DNF', 'Other']

FINISH_FILE_PREFIX = 'rbfinishes-'
RESULT_DATABASE_NAME = 'racebox.db'
AUTOSAVE_FILENAME = 'rbautosave.json'
USE_FINISH_TIMES = 'Use finish times'
NO_RACE_SELECTED = '(no race selected)'
TOTALMS = 'finishms'

MSEC_IN_MINUTE = 1000 * 60
MSEC_IN_HOUR = MSEC_IN_MINUTE * 60
MSEC_IN_DAY = MSEC_IN_HOUR * 24

def msToTime(ms_in):
    seconds = int(ms_in/1000)%60
    minutes = int(ms_in/(MSEC_IN_MINUTE))%60
    hours = int(ms_in/(MSEC_IN_HOUR))%24
    ms = int(ms_in - hours*MSEC_IN_HOUR - minutes*MSEC_IN_MINUTE - seconds*1000)
    return hours, minutes, seconds, ms
 
def numSuffix(num):
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= num % 100 < 20 else num % 10, 'th') #4 could be any number > 3

def getJSONFinishData(fileName):
    try:
        with open (fileName, 'r') as file:
            return json.load(file)
    except:
        return {
            'id': '',
            'data': []
        }

def setJSONFinishData(fileName, finishInfo):
    try:
        with open (fileName, 'w+') as file:
            file.write(json.dumps(finishInfo))
            return True
    except Exception as error:
        print(error)
        return False
    
def processFinishInfo(finishInfo, classList):
    finishList = []
    for rd in finishInfo['data']:
        rating = getRating(rd['class'].get(), classList)
        rd = {
            'pos': rd['pos'],
            'clock': rd['clock'],
            'class': rd['class'].get(),
            'rating': rating,
            'sailnum':rd['sailnum'].get(),
            'race': int(rd['race'].get()),
            'status': rd['status'].get(),
            'notes': rd['notes'].get()
        }
        finishList.append(rd)
    return {**finishInfo, 'data': finishList}
        
def getAutoSaveFileName():
    homeFolder = os.path.expanduser('~')
    return os.path.join(homeFolder, AUTOSAVE_FILENAME)

def getUniqueId(convertToString=True):
    id = uuid.uuid4()
    return str(id) if convertToString else id

def convertStringToUUID(s):
    return uuid.UUID(s)

def getDbFileName():
    config = RaceboxConfig()
    try:
        dbFolder = config.get('Files', 'databasefolder')
    except:
        dbFolder = os.path.expanduser('~')
    print('db file is ', os.path.join(dbFolder, RESULT_DATABASE_NAME))
    return os.path.join(dbFolder, RESULT_DATABASE_NAME)

def getFinishFileName(extn):
    now = datetime.now()
    fileName = '{}{}'.format(FINISH_FILE_PREFIX, now.strftime('%Y%m%d-%H%M'))
    filesFolder = getCurrentFilesFolder()
    #os.path.join throws away anything before an absolute path
    return os.path.join(filesFolder, fileName + '.' +  extn)

def getCurrentFilesFolder():
    config = RaceboxConfig()
    useDefaultFolder = True if config.get('Files', 'finshFileUseDefaultFolder').lower() == 'true' else False
    defaultFolder = os.path.expanduser('~') if useDefaultFolder else ''
    filesFolder = config.get('Files','finishFileFolder')
    if useDefaultFolder:
        return os.path.join(defaultFolder, filesFolder)
    else:
        return filesFolder
    
def getFileList(folderName, prefix=FINISH_FILE_PREFIX, extn='json', recentFirst=True):
    fileList = glob.glob(os.path.join(folderName, '{}*.{}'.format(prefix, extn)), recursive = False)
    fileList.sort(key=os.path.getctime, reverse=recentFirst)
    return fileList

def getFileNames(fileList):
    fileNames = []
    for f in fileList: fileNames.append(os.path.basename(f))
    return fileNames

def getRating(classValue, classList):
    # https://stackoverflow.com/questions/8270092/remove-all-whitespace-in-a-string/8270124#8270124
    rating = 0
    cv = ''.join(classValue.split()).lower()
    for c in classList:
        if ''.join(c['name'].split()).lower() == cv: rating = int(c['rating'])
    return rating

def onlyNumbers(k):
    if k in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']: return True
    return False

def saveToCSVFile(saveFileName, finishInfo):
    fileHdr = 'Pos, Clock, Class, Sail, Rating, Race, Status, Notes\n'
    try:
        with open (saveFileName, 'w+') as file:
            if len(finishInfo['name']) > 0: file.write(finishInfo['name'] + '\n')
            file.write(fileHdr)
            for f in finishInfo['data']:
                rating = '' if f['rating'] == 0 else f['rating']
                status = '' if f['status'] == STATUS_FINISHED else f['status']
                if f['pos'] > 0:
                    lineOut = '{}, {:02}:{:02}:{:02}, {}, {}, {}, {}, {}, {}\n'.format(
                        f['pos'],
                        f['clock']['hh'],
                        f['clock']['mm'],
                        f['clock']['ss'],
                        f['class'],
                        f['sailnum'],
                        rating,
                        f['race'],
                        status,
                        f['notes']
                    )
                else:
                    lineOut = '{}, {}, {}, {}, {}, {}, {}, {}\n'.format(
                        '',
                        '',
                        f['class'],
                        f['sailnum'],
                        rating,
                        f['race'],
                        status,
                        f['notes']
                    )
                file.write(lineOut)
            return {'result': True, 'msg': 'File {} saved'.format(saveFileName)}
    except Exception as error:
        return {'result': False, 'msg': 'Could not save the file {} - {}'.format(saveFileName, error)}
