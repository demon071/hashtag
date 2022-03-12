import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from fe import *
from requests import session
import requests
import threading
import json
import re
import time
import pickle
import validators
from pathlib import Path
from key import *
class Search(QObject):
    stt = pyqtSignal(str, str)
    showlog = pyqtSignal(str, str, str, str, str)
    pcursor = pyqtSignal(str, str, str)
    ketthuc = pyqtSignal()
    def __init__(self, region = 'VN', cursor = 0):
        super(Search, self).__init__()
        self.region = region
        self.cursor = cursor


    def runProccess(self):
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
        }
        s = requests.Session()
        url = f'http://snaptikz.tk/ajax.php?type=list-hashtag&max={self.cursor}&search={self.region}'
        dl = s.get(url, headers = headers).json()
        err = dl.get('error')
        if err == True:
            self.stt.emit('Không tìm thấy', 'red')
            self.ketthuc.emit()
            return 0
        data = dl.get('list')
        if data:
            for x in data:
                category = x.get('category_type')
                if category == 0:
                    cid = x['challenge_info']['cid']
                    name = x['challenge_info']['cha_name']
                    userCount = x['challenge_info']['user_count']
                    viewCount = x['challenge_info']['view_count']
                    self.showlog.emit('Challenge', str(cid), str(name), str(userCount), str(viewCount))
                if category == 1:
                    cid = x['music_info']['mid']
                    name = x['music_info']['title']
                    userCount = x['music_info']['user_count']
                    viewCount = ''
                    self.showlog.emit('Music', str(cid), str(name), str(userCount), str(viewCount))

            min_cursor = self.cursor
            max_cursor = dl.get('cursor', 0)
            has_more = dl.get('hasMore', '')
            self.pcursor.emit(str(min_cursor), str(max_cursor), str(has_more))
            
        self.ketthuc.emit()
        return 1



class MyForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.min_cursor = 0
        self.max_cursor = 0
        self.thread = QThread()
        self.ui.search.clicked.connect(self.RunSearch)
        self.ui.pushButton.clicked.connect(self.RunSearch)
        self.ui.pushButton_2.clicked.connect(self.RunSearch)
        self.ui.pushButton_2.setEnabled(False)
        # self.generationKey()

    def RunSearch(self):
        btn = self.sender()
        self.stt('Đang tải...', 'blue')
        region = self.ui.region.text()
        if btn.objectName() == 'search':
            cursor = 0
        if btn.objectName() == 'pushButton_2':
            cursor = self.min_cursor
        if btn.objectName() == 'pushButton':
            cursor = self.max_cursor
        if self.max_cursor != 0:
            self.ui.pushButton_2.setEnabled(True)
        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.setRowCount(0)
        self.obj = Search(region, cursor)
        self.obj.moveToThread(self.thread)
        self.thread.started.connect(self.obj.runProccess)
        self.obj.showlog.connect(self.showlog)
        self.obj.pcursor.connect(self.pcursor)
        self.obj.stt.connect(self.stt)
        # self.obj.taive.connect(self.status)
        self.obj.ketthuc.connect(self.thread.quit)
        self.thread.start()


    def generationKey(self):
        # Tao key
        keytool = create_key("DownloadPro")
        self.LICENSE = False
        sttus = ''
        # check key
        try:
            check, sttus = check_key(keytool)
            self.LICENSE = check
           
        except:
            pass

        if(self.LICENSE == True):
            self.ui.centralwidget.setEnabled(True)
            self.stt(sttus , 'green')
        else:
            self.ui.centralwidget.setEnabled(False)
            self.stt(sttus , 'red')

    

    def pcursor(self, min_cursor, max_cursor, has_more):
        self.min_cursor = min_cursor
        self.max_cursor = max_cursor
        if has_more == 0:
            self.ui.pushButton.setEnabled(False)
        self.stt('Tải xong!', 'green')


    def stt(self, text, color):
        _translate = QtCore.QCoreApplication.translate
        self.ui.statusbar.showMessage(_translate("MainWindow", text))
        self.ui.statusbar.setStyleSheet(f'color:{color}')

    def showlog(self, category, tid, name, userCount, viewCount):
        rowPosition = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(rowPosition)
        self.ui.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(category))
        self.ui.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(tid))
        self.ui.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(name))
        self.ui.tableWidget.setItem(rowPosition, 3, QTableWidgetItem(userCount))
        self.ui.tableWidget.setItem(rowPosition, 4, QTableWidgetItem(viewCount))
        