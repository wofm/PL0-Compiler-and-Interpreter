# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'compiler_ui.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!
import threading
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog


import Praser
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Main")
        MainWindow.resize(1120, 690)
        self.a=0  #UI中的编译器
        self.clickCnt=0
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.input_code = QtWidgets.QTextEdit(self.centralwidget)
        self.input_code.setGeometry(QtCore.QRect(43, 96, 311, 401))
        self.input_code.setObjectName("input_code")
        self.label_input = QtWidgets.QLabel(self.centralwidget)
        self.label_input.setGeometry(QtCore.QRect(110, 40, 171, 41))
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.label_input.setFont(font)
        self.label_input.setAlignment(QtCore.Qt.AlignCenter)
        self.label_input.setObjectName("label_input")
        self.Compile_Button = QtWidgets.QPushButton(self.centralwidget)
        self.Compile_Button.setGeometry(QtCore.QRect(132, 537, 121, 61))
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.Compile_Button.setFont(font)
        self.Compile_Button.setObjectName("Compile_Button")
        self.Compile_Button.clicked.connect(self.compile)
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(413, 96, 321, 401))
        self.textEdit.setObjectName("textEdit")
        self.textEdit_2 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_2.setGeometry(QtCore.QRect(783, 96, 321, 401))
        self.textEdit_2.setObjectName("textEdit_2")
        self.label_PL0 = QtWidgets.QLabel(self.centralwidget)
        self.label_PL0.setGeometry(QtCore.QRect(491, 40, 171, 41))
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.label_PL0.setFont(font)
        self.label_PL0.setAlignment(QtCore.Qt.AlignCenter)
        self.label_PL0.setObjectName("label_PL0")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(522, 537, 121, 61))
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.interpret)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(890, 537, 121, 61))

        self.pushButton_2.clicked.connect(self.choose_file)
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(870, 40, 171, 41))
        font = QtGui.QFont()
        font.setFamily("Adobe Arabic")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1120, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Compiler"))
        self.label_input.setText(_translate("MainWindow", "code input"))
        self.Compile_Button.setText(_translate("MainWindow", "Compile"))
        self.label_PL0.setText(_translate("MainWindow", "PL0  code"))
        self.pushButton.setText(_translate("MainWindow", "Interpret"))
        self.pushButton_2.setText(_translate("MainWindow", "Choose File"))
        self.label.setText(_translate("MainWindow", "Output"))

    #当点击按钮时触发，修改按钮名                                              <-----------
    def compile(self):
        ff = open('output_pl0.txt', 'w')
        try:
            inputs=self.input_code.toPlainText()

            self.a = Praser.Praser(inputs, ff)
            self.a.Parse()
            self.a.interp.listcode(0)
        except Exception as e:
            #print(traceback.format_exc())
            ff.write(str(e))
            ff.write('\n')
            print(e)

        ff.close()
        ff=open('output_pl0.txt')
        output=ff.read()
        _translate = QtCore.QCoreApplication.translate
        self.textEdit.setText(_translate("MainWindow", output))#在pcode文本框中输出

    def interpret(self):
        self.textEdit_2.setPlainText("")
        signal=list('a')#信号量
        ff = open('output_pcode.txt', 'w')
        try:
            #self.a.interp.interpret(0,ff)
            t=threading.Thread(target=self.a.interp.interpret,args=(self.textEdit_2,ff,signal))
            t.start()
        except Exception as e:
            ff.write(str(e))
            ff.write('\n')

        #ff.close()

        # ff=open('output_pcode.txt')
        # output=ff.read()
        # _translate = QtCore.QCoreApplication.translate
        #self.textEdit_2.append(output)#在pcode文本框中输出
        flash=threading.Thread(target=self.renew,args=(self.textEdit_2,signal))#刷新线程
        flash.start()

    def renew(self,textboard,signal):
        while signal[0]=='a':
            continue
        old_pos=0
        ff = open('output_pcode.txt')
        textboard.append(ff.read())

        # while True:

            # i = 0  # 目前读到的行数
            # time.sleep(0.1)
            # while True:
            #     line=ff.readline()
            #     if not line:
            #         ff.close()
            #         i=0
            #         break
            #     i+=1
            #     if i > old_pos:
            #         textboard.append(line)
            #         old_pos+=1


    def choose_file(self):
        a=QFileDialog()
        filename = QFileDialog.getOpenFileName(a, 'open file', 'C:')
        try:
            with open(filename[0], 'r') as f:
                my_txt = f.read()
                self.input_code.setPlainText(my_txt)
        except Exception as e:
            print(e)








