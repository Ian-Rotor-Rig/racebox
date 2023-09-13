from datetime import datetime
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

def getJSONFinishData(fileName):
    try:
        with open (fileName, 'r') as file:
            return json.load(file)
    except Exception as error:
        return {
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
            'sailnum':rd['sailnum'].get(),
            'race': rd['race'].get(),
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
    return os.path.join(homeFolder, 'rbautosave.json')

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
    print('db file is ', os.path.join(dbFolder, 'racebox.db'))
    return os.path.join(dbFolder, 'racebox.db')

def getFinishFileName(extn):
    now = datetime.now()
    fileName = 'finishes-{}'.format(now.strftime('%Y%m%d-%H%M'))
    config = RaceboxConfig()
    useDefaultFolder = True if config.get('Files', 'finshFileUseDefaultFolder').lower() == 'true' else False
    defaultFolder = os.path.expanduser('~') if useDefaultFolder else ''
    filesFolder = config.get('Files','finishFileFolder')
    if useDefaultFolder:
        #os.path.join throws away anything before an absolute path like filesFolder
        return defaultFolder + os.path.join(filesFolder, fileName + extn)
    else:
        return os.path.join(filesFolder, fileName + extn)

def getRating(classValue, classList):
    rating = 0
    for c in classList:
        if c['name'].lower().strip() == classValue.get().lower().strip(): rating = c['rating']
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
