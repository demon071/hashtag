import sys 
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from be import *
app = QApplication(sys.argv)
w = MyForm()
w.show()
sys.exit(app.exec_())

