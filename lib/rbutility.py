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
FIXED_FONT_LARGE = 'Monospace 14 bold'

MONTH_ABBREV = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

STATUS_FINISHED = 'Finished'
STATUS_CODES = ['RET', 'OCS', 'DSQ', 'DNF', 'Other']

FINISH_FILE_PREFIX = 'rbfinishes-'
RESULT_DATABASE_NAME = 'racebox.db'
AUTOSAVE_FILENAME = 'rbautosave.json'

MSEC_IN_MINUTE = 1000 * 60
MSEC_IN_HOUR = MSEC_IN_MINUTE * 60
MSEC_IN_DAY = MSEC_IN_HOUR * 24

def dayPostfix(day):
    if day in [1, 21, 31]:  return 'st'
    if day in [2, 22]:  return 'nd'
    if day in [3, 23]:  return 'rd'
    return 'th'

def getJSONFinishData(fileName):
    try:
        with open (fileName, 'r') as file:
            return json.load(file)
    except Exception as error:
        return {
            'id': '',
            'name': '',
            'date': {},
            'data': []
        }

def setJSONFinishData(fileName, finishInfo, classList):
    jsonInfo = {
        'id': finishInfo['id'],
        'name': finishInfo['name'],
        'date': {
            'day': finishInfo['date']['day'],
            'month': finishInfo['date']['month'],
            'year': finishInfo['date']['year']
        },
        'data': []
    }
    for rd in finishInfo['data']:
        rating = getRating(rd['class'], classList)
        rd = {
            'pos': rd['pos'],
            'clock': rd['clock'],
            'class': rd['class'].get(),
            'rating': rating,
            'sailnum':int(rd['sailnum'].get()),
            'race': int(rd['race'].get()),
            'status': rd['status'].get(),
            'notes': rd['notes'].get()
        }
        jsonInfo['data'].append(rd)
    try:
        with open (fileName, 'w+') as file:
            file.write(json.dumps(jsonInfo))
            return True
    except Exception as error:
        print(error)
        return False

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

def getRating(classValue, classList):
    rating = 0
    for c in classList:
        if c['name'].lower().strip() == classValue.get().lower().strip(): rating = int(c['rating'])
    return rating

def onlyNumbers(k):
    if k in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']: return True
    return False

def saveToCSVFile(saveFileName, finishInfo, classList):
    fileHdr = 'Pos, Clock, Class, Sail, Rating, Race, Status, Notes\n'
    try:
        with open (saveFileName, 'w+') as file:
            if len(finishInfo['name']) > 0: file.write(finishInfo['name'] + '\n')
            file.write(fileHdr)
            for f in finishInfo['data']:
                rating = str(getRating(f['class'], classList))
                if rating == '0': rating = ''
                if f['pos'] > 0:
                    lineOut = '{}, {:02}:{:02}:{:02}, {}, {}, {}, {}, {}, {}\n'.format(
                        f['pos'],
                        f['clock']['hh'],
                        f['clock']['mm'],
                        f['clock']['ss'],
                        f['class'].get(),
                        f['sailnum'].get(),
                        rating,
                        f['race'].get(),
                        f['status'].get() if f['status'].get() != STATUS_FINISHED else '',
                        f['notes'].get()
                    )
                else:
                    lineOut = '{}, {}, {}, {}, {}, {}, {}, {}\n'.format(
                        '',
                        '',
                        f['class'].get(),
                        f['sailnum'].get(),
                        rating,
                        f['race'].get(),
                        f['status'].get() if f['status'].get() != STATUS_FINISHED else '',
                        f['notes'].get()
                    )
                file.write(lineOut)
            return {'result': True, 'msg': 'File {} saved'.format(saveFileName)}
    except Exception as error:
        return {'result': False, 'msg': 'Could not save the file {} - {}'.format(saveFileName, error)}
