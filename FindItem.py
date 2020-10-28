# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xi on 2020-9-28
from PyQt5.QtWidgets import QDialog, QMessageBox
from Resource.Find_ui import Ui_Find
from PyQt5.QtCore import pyqtSignal


class Find_Dialog(QDialog, Ui_Find):
    # 自定义信号，用来向主窗口传递项目信息
    signal_project_info = pyqtSignal(str)

    def __init__(self, parent):
        super(Find_Dialog, self).__init__(parent)
        self.setupUi(self)
        #定义分组对应字典
        self.d={'按类别':'Category','按标签':'Tag','按甲方':'Party_A','按乙方':'Party_B','按工程地址':'Project_Address'}
        #初始化分组信息
        self.comboBox.addItems(self.d)#['--请选择--','按类别','按标签','按甲方','按乙方','按工程地址']
        #初始化单选状态
        self.radioButton_2.setChecked(True)
    def query(self):
        """按照ComboBox中的类别筛选数据并显示"""
        self.listWidget.clear()
        if self.radioButton.isChecked():    #采用分组方放查询数据
            print('采用分组方放查询数据')
            re = self.parent().databaseOprate("SELECT * FROM BASE WHERE  {} LIKE'%%{}%%'".format(self.d[self.comboBox.currentText()],self.comboBox_2.currentText()))
        else:
            print('采用关键字方式查询数据')
            re = self.parent().databaseOprate("SELECT * FROM BASE WHERE  Short_Name LIKE'%%{}%%'".format(self.lineEdit.text()))
        self.listWidget.addItems(["★".join(map(str, _)) for _ in re])  #
    def by_group(self):
        """按照分组信息查询"""
        print('By category')
        self.comboBox_2.clear() #需要随时清空下下拉列表，否则会重复叠加
        # if self.comboBox.currentText()=='按类别':
        #     self.category = self.parent().databaseOprate("select Category from BASE ")
        #     self.comboBox_2.addItems(sorted([_[0] for _ in set(self.category) if _[0]]))

        if self.comboBox.currentText()=='按标签':      #按标签查找需要单独操作
            self.tag = self.parent().databaseOprate("select Tag from BASE ")
            # print('标签：',tag)
            #识别分号分隔的标签,列表推导式不会啊
            l=[]
            for a in self.tag:
                for b in a:
                    if  b:
                        if ';'in b:
                            l.extend(b.split(';'))
                        else:
                            l.append(b)
            self.comboBox_2.addItems(sorted(set(l)))
        elif (_text:=self.comboBox.currentText()) in self.d:
            self.res=self.parent().databaseOprate("select {} from BASE ".format(self.d[_text]))
            self.comboBox_2.addItems(sorted([_[0] for _ in set(self.res) if _[0]]))
        # elif self.comboBox.currentText()=='按甲方':
        #     self.partyA = self.parent().databaseOprate("select Party_A from BASE ")
        #     self.comboBox_2.addItems(sorted([_[0] for _ in set(self.partyA) if _[0]]))
        # elif self.comboBox.currentText()=='按乙方':
        #     self.partyB = self.parent().databaseOprate("select Party_B from BASE ")
        #     self.comboBox_2.addItems(sorted([_[0] for _ in set(self.partyB) if _[0]]))
        # elif self.comboBox.currentText()=='按工程地址':
        #     self.address = self.parent().databaseOprate("select Project_Address from BASE ")
        #     self.comboBox_2.addItems(sorted([_[0] for _ in set(self.address) if _[0]]))


    def set_project(self):
        print('双击获取CurrentItem文本：', self.listWidget.currentItem().text())
        self.signal_project_info.emit(self.listWidget.currentItem().text())
        # self.signal.emit()
        print('已发送!')
        # self.accept() # 不能放到这里，使用按钮唤起子窗口的时候不需要关闭子窗口。

if __name__ == '__main__':
    pass
