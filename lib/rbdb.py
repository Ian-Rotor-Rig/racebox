import sqlite3
from lib.rbutility import getDbFileName

class rbDb:
    def __init__(self):
        dbName = getDbFileName()
        self.con = sqlite3.connect(dbName)
        self.cursor = self.con.cursor()
    
    def __del__(self):
        self.cursor.close()
        self.con.close()
    
    def addFinishTimes(self, finishInfo):
        pass
    #get the finishinfo
    #create table for finishtimes - mainly for the ID, name and date
    #if the ID already exists then do and update not an add
    #create table for each race?
    #create table for finish times with primary key as the id
    #and the race number?
    # or maybe create a table for the finishtimes but get/store a new id for each race?
    
    def createTable(self, tableName: str, tableColumns: tuple):
        if self.tableExists(tableName): return True
        if len(tableColumns) < 1: return False
        columnText = ''
        for i,c in enumerate(tableColumns): columnText += ',{}'.format(c) if i > 0 else '{}'.format(c)
        print('table is ', tableName, ' and columns are ', columnText)
        self.cursor.execute('CREATE TABLE "{}"({})'.format(tableName, columnText)) #<------
        if self.tableExists(tableName): return True
        else: return False
        
    def deleteTable(self, tableName: str):
        if not self.tableExists(tableName): return False
        self.cursor.execute('DROP TABLE "{}"'.format(tableName))
        return True
    
    def saveChanges(self):
        self.con.commit()
        
    def tableExists(self, tableName: str):
        result = self.cursor.execute('SELECT name from sqlite_master WHERE name="{}"'.format(tableName))
        if result.fetchone() is None: return False
        else: return True
        
    def addRows(self, tableName: str, grid: list[tuple]):
        if len(grid) < 1: return False
        if len(grid[0]) < 1: return False
        placeHolders = ''
        for i in range(len(grid[0])): placeHolders += ', ?' if i > 0 else '?'
        qry = 'INSERT INTO "{}" VALUES({})'.format(tableName, placeHolders)
        print('query is ', qry)
        self.cursor.executemany(qry, grid)
        return True
        
    def addRow(self, tableName: str, row: tuple):
        if len(row) < 1: return False
        placeHolders = ''
        for i in range(len(row)): placeHolders += ', ?' if i > 0 else '?'
        qry = 'INSERT INTO "{}" VALUES({})'.format(tableName, placeHolders)
        self.cursor.execute(qry, row)
        return True
        
    def removeRows(self, tableName: str, columnName: str, columnValue):
        if len(columnName) < 1: return False
        if len(columnValue) < 1: return False
        qry = 'DELETE FROM "{}" WHERE {} = ?'.format(tableName, columnName)
        print('remove rows query is ', qry)
        self.cursor.execute(qry, (columnValue,))
        return True

    def getRows(self, tableName: str, columnNames: tuple = (), columnValue = ''):
        columnNamesText = '*'
        if len(columnNames) > 0:            
            columnNamesText = ''
            for i,c in enumerate(columnNames): columnNamesText += ',{}'.format(c) if i > 0 else '{}'.format(c)
        if columnValue == '':
            qry = 'SELECT {} FROM "{}"'.format(columnNamesText, tableName)
        else:
            qry = 'SELECT {} FROM "{}" WHERE {} = ?'.format(columnNamesText, tableName, columnValue)
        self.cursor.execute(qry)
        return self.cursor.fetchall() 
    
        ##################################################
        #use the new db utils - just testing
        #db = rbDb()
        #result = db.createTable('test table', ('col1', 'col2'))
        #print('create table result ', result)
        #result = db.addRow('test table', ('another row', 99))
        #print('add row result ', result)
        #result = db.addRows('test table',
        #    [
        #        ('some text', 5),
        #        ('some other text', 99),\
        #    ]
        #)
        #print('add rows result ', result)
        #result = db.removeRows('test table', 'col1', 'another row')
        #print('remove rows result', result)
        #db.saveChanges()
        #result = db.getRows('test table')
        #print('get row data: ', result)
        #result = db.deleteTable('test table')
        #print('delete table result ', result)
        #################################################