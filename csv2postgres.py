# -*- coding: utf-8 -*-
"""
Created on Sun Aug 15 23:20:29 2021

@author: Muzaffer
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from os import listdir
import json
import psycopg2 as pg
import pandas as pd
from tkinter import messagebox

class CSV2Postgres(tk.Tk):
    
    def __init__(self):
        
        super().__init__()
        self.title("Multiple Import of CSV Files")
        self.geometry("370x190+300+100")
        self.resizable(False, False)
        
        self.label = ttk.Label(self, text="Open File Directory:")
        self.label.place(x=20, y=20)
        
        self.dirNameEntry = ttk.Entry(self, width=40)
        self.dirNameEntry.place(x=20, y=50)
        
        self.tableLabel = ttk.Label(self, text="Table Name:")
        self.tableLabel.place(x=20, y=80)
        
        self.tableNameEntry = ttk.Entry(self, width=40)
        self.tableNameEntry.place(x=20, y=110)
        
        self.openDirButton = ttk.Button(self, text="Open")
        self.openDirButton['command'] = self.askOpenDir
        self.openDirButton.place(x=270, y=48)
        
        self.newTableCheck = ttk.Checkbutton(self, text="Create New Table")
        self.newTableCheck.place(x=150, y=80)        
        
        self.multipleImport = ttk.Button(self, text="Import")
        self.multipleImport['command'] = self.ImportData
        self.multipleImport.place(x=270, y=108)
        
        self.ConnectPG()

    def ConnectPG(self):
        global cur, conn
        with open("config.json","r") as file:
            configFile = json.load(file)
        conn = pg.connect(
        host = configFile['host'],
        database = configFile['database'],
        user = configFile['user'],
        password = configFile['password']
        )
        cur = conn.cursor()
        return cur, conn
        
    def askOpenDir(self):
        global nameDir
        nameDir = filedialog.askdirectory()
        self.dirNameEntry.insert(0,nameDir)
        return nameDir
    
    def ImportData(self):
        
        files = listdir(nameDir)
        
        data = pd.read_csv(nameDir+"/"+files[0], sep=";")
        dataColumns = data.columns.values
        dataValues = data.values
        
        if self.newTableCheck.state()[0] == 'selected':
        
            tableQuery = """CREATE TABLE IF NOT EXISTS """+self.tableNameEntry.get()+" ("
        
            for i in range(len(dataColumns)):
                dataType = str(type(dataValues[0,i]))
                tableQuery = tableQuery +" "+ dataColumns[i] + " " + dataType + ","
        
            tableQuery = tableQuery.replace("class","")
            tableQuery = tableQuery.replace("<","")
            tableQuery = tableQuery.replace(">","")
            tableQuery = tableQuery.replace("'","")
            tableQuery = tableQuery.replace("str","varchar(250)")
            n = len(tableQuery)-1
            tableQuery = tableQuery[:n]
            tableQuery = tableQuery + ")"
            
            cur.execute(tableQuery)
            conn.commit()
        
        insertRecord = """INSERT INTO """+ self.tableNameEntry.get() + " VALUES("
        for i in range(len(dataColumns)):
            insertRecord = insertRecord + "%s, "
        
        N = len(insertRecord)-2
        insertRecord = insertRecord[:N] + ")"
        
        for file in range(len(files)):
            data = pd.read_csv(nameDir+"/"+files[file], sep=";")
            records = data.values
            
            for rec in range(len(records)):
                record = records[rec, :]
                cur.execute(insertRecord, record)
                conn.commit()
        
        messagebox.showinfo("Succesfully!", "Data import complete.")

if __name__ == "__main__":
    App = CSV2Postgres()
    App.mainloop()