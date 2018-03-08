import word_anay
import SymbolTable as ST
import Praser
import PyQt5
import traceback
import sys

from PyQt5.QtWidgets import QApplication , QMainWindow
from compiler_ui import *

# f = open("test5.txt", "r")
# input = ""
# while True:
#     line = f.readline()
#     if len(line) == 0:  # Zero length indicates EOF
#         break
#     input += line
# fff = open('output_pl0.txt', 'w')
# a = Praser.Praser(input,fff)
# ff = open('output.txt', 'w')
# try:
#     a.Parse()
# except Exception as e:
#     print(e)
#
# a.interp.interpret(1, ff)
#
# ff.close()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())






