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
        self.cursor.execute('DROP TABLE {}'.format(tableName))
        return True
    
    def saveChanges(self):
        self.con.commit()
        
    def tableExists(self, tableName: str):
        result = self.cursor.execute('SELECT name from sqlite_master WHERE name="{}"'.format(tableName))
        if result.fetchone() is None: return False
        else: return True
        
    def addRows(self, tableName: str, grid: list[tuple]):
        if len(grid) < 1: return
        if len(grid[0]) < 1: return
        qry = 'INSERT INTO "{}" VALUES({})'.format(tableName, '?' * len(grid[0]))
        self.cursor.executemany(qry, grid)
        
    def addRow(self, tableName: str, row: tuple):
        qry = 'INSERT INTO "{}" VALUES({})'.format(tableName, '?' * len(row))
        self.cursor.execute(qry, row)
        
    def removeRows(self, tableName: str, columnName: str, columnValue):
        qry = 'DELETE FROM "{}" WHERE {} = ?'.format(tableName, columnName)
        self.cursor.execute(qry, columnValue)

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
    
    