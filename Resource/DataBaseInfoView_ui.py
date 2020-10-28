# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DataBaseInfoView.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DataBaseInfo(object):
    def setupUi(self, DataBaseInfo):
        DataBaseInfo.setObjectName("DataBaseInfo")
        DataBaseInfo.resize(448, 274)
        self.gridLayout = QtWidgets.QGridLayout(DataBaseInfo)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_4 = QtWidgets.QPushButton(DataBaseInfo)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout.addWidget(self.pushButton_4)
        self.lineEdit_2 = QtWidgets.QLineEdit(DataBaseInfo)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_2.sizePolicy().hasHeightForWidth())
        self.lineEdit_2.setSizePolicy(sizePolicy)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout.addWidget(self.lineEdit_2)
        self.label_2 = QtWidgets.QLabel(DataBaseInfo)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushButton = QtWidgets.QPushButton(DataBaseInfo)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(DataBaseInfo)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.lineEdit = QtWidgets.QLineEdit(DataBaseInfo)
        self.lineEdit.setMaximumSize(QtCore.QSize(180, 16777215))
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButton_3 = QtWidgets.QPushButton(DataBaseInfo)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableView = QtWidgets.QTableView(DataBaseInfo)
        self.tableView.setInputMethodHints(QtCore.Qt.ImhNone)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(DataBaseInfo)
        self.pushButton.clicked.connect(DataBaseInfo.add_row)
        self.pushButton_2.clicked.connect(DataBaseInfo.del_row)
        self.lineEdit.textChanged['QString'].connect(DataBaseInfo.filter)
        self.pushButton_3.clicked.connect(DataBaseInfo.filter)
        self.pushButton_4.clicked.connect(DataBaseInfo.jump_to)
        QtCore.QMetaObject.connectSlotsByName(DataBaseInfo)

    def retranslateUi(self, DataBaseInfo):
        _translate = QtCore.QCoreApplication.translate
        DataBaseInfo.setWindowTitle(_translate("DataBaseInfo", "Dialog"))
        self.pushButton_4.setText(_translate("DataBaseInfo", "跳转到："))
        self.lineEdit_2.setToolTip(_translate("DataBaseInfo", "-1:To Bottom;1:To Top"))
        self.label_2.setText(_translate("DataBaseInfo", "行"))
        self.pushButton.setText(_translate("DataBaseInfo", "Add Row"))
        self.pushButton_2.setText(_translate("DataBaseInfo", "Del Row"))
        self.pushButton_3.setText(_translate("DataBaseInfo", "Filter "))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DataBaseInfo = QtWidgets.QDialog()
    ui = Ui_DataBaseInfo()
    ui.setupUi(DataBaseInfo)
    DataBaseInfo.show()
    sys.exit(app.exec_())
