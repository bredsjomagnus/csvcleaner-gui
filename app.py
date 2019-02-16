from PyQt4.QtCore import *
from PyQt4.QtGui import *

import xml.etree.ElementTree as ET
import requests

import pandas as pd

import sys
import math
import json

import maintest_ui

# setting up mylaps header and datatypes
# mylaps = zip(mylapsheadertitles, mylapsheaderdatatypes)


# Globals
# templates [dict]: templdata
templdata = dict()
# list of correct headers that needs to correct dataframe
headercorrections = []
# list of column corrections
columncorrections = []
# list of wrong headers collected from dataframe
dfwrongs = []
# dataframe
df = pd.DataFrame({})
# nan values för string och för numeric
nanvalues = {'str': "", "numeric": -1}

class Maintest(QMainWindow, maintest_ui.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.splitter.setStretchFactor(1, 10)
        # signal actionOpen
        # When open is selected/triggered connect to slot
        # self.actionOpen.triggered.connect(self.getfile)
        self.actionOpen.triggered.connect(self.getcsvfile)
        # signal actionExit
        self.actionExit.triggered.connect(self.exiting)
        # signal actionSkolmaten
        self.actionSkolmaten.triggered.connect(self.skolmaten)
        # signal fixHeaderBtn
        self.fixHeaderBtn.clicked.connect(self.fixheader)
        # signal fixButtonsBtn
        self.fixColumnsBtn.clicked.connect(self.fixColumn)
        # signal actionSave
        self.actionSave.triggered.connect(self.saveDf)

    # slot
    # actionSave
    def saveDf(self):
        """
        Save global df to csv-file
        """
        # use global dataframe: df
        global df
        
        # opening FileDialog for saving and getting filename from it: fname
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        fltr = "CSV files (*.csv)"
        dlg.setFilter(fltr)
        fname = dlg.getSaveFileName(self, 'Save file')

        # save dataframe to csv without index column
        df.to_csv(fname, index=False)

    # slot
    # fixheader
    def fixheader(self):
        """
        Fixing headers that needs to be corrected
        """
        # print("headercorrections: " + str(headercorrections))
        # print("dfwrongs: " + str(dfwrongs))
        # print("Dataframe: " + str(df))

        # reseting headercorrections and dfwrongs and
        # renaming columns according to template

        global headercorrections
        headercorrections = []
        global dfwrongs
        dfwrongs = []
        global df

        # trying to fix headers
        try:
            df.columns = templdata['mylaps']['header']
        except:
            pass

        # print(str(df.columns.tolist()))
        self.displayDf(df)

    def fixColumn(self):
        global df
        global nanvalues
        global columncorrections

        self.progressLabel.setText('Fixing Columns...')

        self.fixColumnsBtn.setEnabled(False)

        # total number of rows in df: count_row (int)
        count_row = df.shape[0]

        datatypes = templdata['mylaps']['datatypes']
        columns = df.columns.tolist()
        for row in range(1, count_row):
            # insert new row in rowPosition
            # rowPosition = self.table.rowCount()
            # self.table.insertRow(rowPosition)

            # print("rowPosition: {}".format(rowPosition))

            for column, value in enumerate(df):
                try:
                    if datatypes[column] == 'str':
                        df[columns[column]].fillna(nanvalues['str'], inplace=True)
                    else:
                        df[columns[column]].fillna(nanvalues['numeric'], inplace=True)

                    df[columns[column]] = df[columns[column]].astype(datatypes[column])
                except Exception as error:
                    # print("Convertion error: {}".format(error))
                    pass
                cellvalue = df.iloc[row, column]
                # typeof = type(cellvalue.item())
                typeof = self.npType(cellvalue)
                # print("Row: {}, Column: {}, type: {}".format(row, column, typeof))
                
                if self.dtype(datatypes[column]) == typeof:
                    value = "{}".format(cellvalue)
                    self.table.setItem(row, column, QTableWidgetItem(value))
                    self.table.item(row, column).setBackground(Qt.green)
                    try:
                        popped = columncorrections.pop()
                    except:
                        pass
                else:
                    value = "{} \n IS {}/SHOULD BE {}".format(cellvalue, typeof, self.dtype(datatypes[column]))
                    self.table.setItem(row, column, QTableWidgetItem(value))
                    
                    self.table.item(row, column).setBackground(Qt.red)
            self.progressBar.setValue((row/count_row)*100)
        
        self.progressLabel.setText('Done')
        self.progressBar.setValue(0)
        # if len(columncorrections) > 0:
        #     self.fixColumnsBtn.setEnabled(True)

    # slot
    # actionOpen
    def getcsvfile(self):
        """
        Open csv-file and read it into TableWidget table
        """

        # print(templdata)
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        fltr = "CSV files (*.csv)"
        dlg.setFilter(fltr)
        fname = dlg.getOpenFileName(self, 'Open CSV file')

        try:
            # get dataframe from csv-file
            global df

            # to delete nan in loaded csv
            # df = pd.read_csv(fname, keep_default_na=False)

            # not deleting nan in loaded csv
            df = pd.read_csv(fname)


            # self.setCentralWidget(QPlainTextEdit(f))
            # print(list(df))
            self.displayDf(df)
        
        except Exception as err:
            print("could not open csv file through pandas\n{}".format(err))

    def displayDf(self, df):
        """
        Display dataframe: df
        """
        # number of headers needed to correct and list of wrongs in df
        global headercorrections
        global columncorrections
        global dfwrongs
        try:
            ################################################################
            #   GET DF HEADERS AND TEMPLATE HEADERS, DF ROWS AND COLUMNS   #
            ################################################################
            # get df headers as Index and convert it to a list via tolist()
            dfheaders = df.columns.tolist()

            # get template headers
            templheaders = templdata['mylaps']['header']

            # get number of columns and rows of df
            count_row = df.shape[0]  
            count_col = df.shape[1]

            # get next row and insert new row
            # rowPosition = self.table.rowCount()
            # self.table.insertRow(rowPosition)

            # add templheaders to table
            # for counter, value in enumerate(templheaders):
            #     self.table.insertColumn(counter)

            ######################################################
            #   RESET ROWS, COLUMNS, FIXHEADERBTH, INFOTEXTAREA  #
            ######################################################
            # reset infotextarea, fixheaderbtn, infotextarea
            self.infoTextArea.clear()
            self.fixHeaderBtn.setEnabled(False)
            self.table.setRowCount(0)
            
            # get next row and insert new row
            rowPosition = self.table.rowCount()
            self.table.insertRow(rowPosition)

            # reset columns
            self.table.setColumnCount(0)

            ##################
            #   SET HEADER   #
            ##################
            # add dfheader to table
            for counter, value in enumerate(dfheaders):
                self.table.insertColumn(counter)
                self.table.setItem(rowPosition, counter, QTableWidgetItem(str(value)))

                # if not corresponding to template append to headercorrections
                if templheaders[counter] != value:
                    self.table.item(rowPosition, counter).setBackground(Qt.red)
                    dfwrongs.append(dfheaders[counter])
                    headercorrections.append(templheaders[counter])
                else:
                    self.table.item(rowPosition, counter).setBackground(Qt.green)

            ###################
            #   SET COLUMNS   #
            ###################
            # get template datatypes: array [int, str, float,...]
            datatypes = templdata['mylaps']['datatypes']

            for row in range(1, count_row):
                # insert new row in rowPosition
                rowPosition = self.table.rowCount()
                self.table.insertRow(rowPosition)

                for column, value in enumerate(df):
                    cellvalue = df.iloc[row, column]
                    typeof = self.npType(cellvalue)
                    
                    if self.dtype(datatypes[column]) == typeof:
                        value = "{}".format(cellvalue)
                        self.table.setItem(row, column, QTableWidgetItem(value))
                       
                        self.table.item(row, column).setBackground(Qt.green)
                    else:
                        value = "{} \n IS {}/SHOULD BE {}".format(cellvalue, typeof, self.dtype(datatypes[column]))
                        self.table.setItem(row, column, QTableWidgetItem(value))
                        
                        self.table.item(row, column).setBackground(Qt.red)

                        columncorrections.append(datatypes[column])
                        # print("Appended to columncorrections")
                    
            
            #################################
            #   SET INFO ON INFOTEXTAREA    #
            #################################
            # get number of columns in df and in template
            info = "dataframe: " + str(len(dfheaders)) + ", "
            info += "template: " + str(len(templheaders))

            # adding headercorrections to info
            info += "\n\n" + str(len(headercorrections)) + "/" + str(len(dfheaders)) +" headers needs to be corrected:"

            if len(dfwrongs) > 0:
                info += "\nFROM\t\t -> \tTO"
                for counter, element in enumerate(headercorrections):
                    if len(dfwrongs[counter]) < 11:
                        info += "\n" + dfwrongs[counter] + "\t\t -> \t" + element
                    else:
                        info += "\n" + dfwrongs[counter] + "\t -> \t" + element

            # enable 'Fix Header' btn if there is headers to correct
            if len(dfwrongs) > 0:
                self.fixHeaderBtn.setEnabled(True)
            
            if len(columncorrections) > 0:
                self.fixColumnsBtn.setEnabled(True)

            # output info about df
            self.infoTextArea.setPlainText(info)

        except Exception as err:
            print("could not display file\n{}".format(err))

    # slot
    # actionOpen
    def getfile(self):
        # Opens filedialog that returns path to chosen file
        
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        fltr = "CSV files (*.csv)"
        dlg.setFilter(fltr)
        fname = dlg.getOpenFileName(self, 'Open file')
        
        # fname = QFileDialog.getOpenFileName(self, 'Open file')
        try:
            # open file: f
            f = open(fname, 'r')
            
            # adds file text to a QPlainTextEdit Widget and then adds widget to mainwindow via setCentralWidget
            self.setCentralWidget(QPlainTextEdit(f.read()))
        except:
            print("Could not open file {}".format(fname))

    # slot
    # actionSkolmaten
    def skolmaten(self):

        # Skolmaten url
        url = "https://skolmaten.se/klockarhagsskolan/rss/weeks/"

        try:
            # download the file contents in binary format
            r = requests.get(url)

            # open method to open a file on your system and write the contents
            with open("skolmaten.xml", "wb") as xml_file:
                xml_file.write(r.content)

            # get tree from xml file
            tree = ET.parse('skolmaten.xml')

            # get root element from tree
            root = tree.getroot()

            week = {}
            # get week days from xml file
            for i in range(6,11):
                daylist = [root[0][i][0].text, root[0][i][2].text]
                week[str(i-6)] = daylist
                
            # set skolmaten_text to this weeks menu
            skolmaten_text  = ""
            for day in week:
                meals = week[day][1].split('<br/>')
                skolmaten_text += week[day][0] + "\n"
                try:
                    skolmaten_text += meals[1] + "\n"
                except:
                    skolmaten_text += "no meal nr 1"
                try:
                    skolmaten_text += meals[0] + "\n\n"
                except: 
                    skolmaten_text += "no meal nr 2"
                
            # print(skolmaten_text)
            # self.displayText.setText(skolmaten_text)

            # creates a QPlayTextEdit widget, add 'skolmaten_text' to it and then adds widget to mainwindow via setCentralWidget
            # self.setCentralWidget(QPlainTextEdit(skolmaten_text))
            self.infoTextArea.setPlainText(skolmaten_text)
        except Exception as err:
            error = str(type(err)) + "\n" + str(err)
            self.infoTextArea.setPlainText(error)

    def npType(self, t):
        if type(t) is str:
            res = type(t)
            # print("res is str")
        elif type(t) is float:
            res = type(t)
            # print("res is float")
        elif type(t) is int:
            res = type(t)
            # print("res is int")
        else:
            res = type(t.item())
            # print("res val.item()")
        
        return res

    def dtype(self, t):
        if t == 'int':
            res = type(1)
        elif t == 'str':
            res = type("string")
        elif t == "float":
            res = type(1.5)
        else:
            res = "error {}".format(type(t))
        
        return res

    # slot
    # actionExit
    def exiting(self):
        exit()

def prepTemplates():
    """
    Prepare templates 'mylaps' and 'hardcard by reading data/templates/template.json7
    and put value in dicitonary templdata
    """
    # Open and read the template files
    fp = open('data/templates/mylaps.json', 'r')
    
    # Convert json to dictionary and set value to global variable jn
    global templdata 
    templdata = json.loads(fp.read())
    
    # close handler to jsonfile
    fp.close()

prepTemplates()
app = QApplication(sys.argv)
maintest = Maintest()
maintest.show()
# maintest.showFullScreen()
app.exec_()