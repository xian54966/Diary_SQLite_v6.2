# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xi on 2020-9-28
from Resource.AddProject_ui import Ui_AddProject
from PyQt5.QtWidgets import QDialog, QMessageBox


class AddProject_Dialog(QDialog, Ui_AddProject):
    def __init__(self, parent):
        super(AddProject_Dialog, self).__init__(parent)
        self.setupUi(self)

        # 初始化乙方、类别等信息，过滤None
        party_b = self.parent().databaseOprate("select Party_B from BASE ")
        self.comboBox.addItems(sorted([_[0] for _ in set(party_b) if _[0]]))
        address = self.parent().databaseOprate("select Project_Address from BASE")
        self.comboBox_3.addItems(sorted([_[0] for _ in set(address) if _[0]]))
        category = self.parent().databaseOprate("select Category from BASE")
        self.comboBox_2.addItems(sorted([_[0] for _ in set(category) if _[0]]))
        tag = self.parent().databaseOprate("select Tag from BASE")
        #识别分号分隔的标签,列表推导式不会啊
        l=[]
        for a in tag:
            for b in a:
                if  b:
                    if ';'in b:
                        l.extend(b.split(';'))
                    else:
                        l.append(b)
        self.comboBox_4.addItems(sorted(set(l)))
        # 接收主窗口发来项目简称，查询并显示项目信息
        self.parent().signal_shortname.connect(self.show_info)

    def show_info(self, data):
        print('打开工程信息窗口')
        """当窗口打开信号来自主窗口的TreeWidget双击时，即为查询模式，接收项目简称，查询并显示项目信息"""
        sql = "select * from BASE where Short_Name='{}'".format(data)
        result = self.parent().databaseOprate(sql)
        # 因为ShortName是主键，不重复，这里只能查询到一个结果，所以控件显示文本写死，查询结果：[('工程名称', '简称', '项目地址', '甲方', '项目编号', '乙方', 合同金额, '类别', '标签')]
        self.lineEdit.setText(result[0][0])
        self.lineEdit_2.setText(result[0][1])
        self.comboBox_3.setCurrentText(result[0][2])
        self.lineEdit_4.setText(result[0][3])
        self.lineEdit_3.setText(result[0][4])
        self.comboBox.setCurrentText(result[0][5])
        self.lineEdit_5.setText(str(result[0][6]))
        self.comboBox_2.setCurrentText(result[0][7])
        self.comboBox_4.setCurrentText(result[0][8])
    def accept(self):
        _Project = self.lineEdit.text()
        _Short_Name = self.lineEdit_2.text()
        _Project_Address = self.comboBox_3.currentText()
        _Party_A = self.lineEdit_4.text()
        _Project_Num = self.lineEdit_3.text()
        _Party_B = self.comboBox.currentText()
        if _:=self.lineEdit_5.text():
            _Contract_Amount = float(_)
        else:
            _Contract_Amount = 0
        _Category = self.comboBox_2.currentText()
        _Tag = self.comboBox_4.currentText()
        # 根据Project字段查重

        if int(self.parent().databaseOprate("select count(*) from BASE where Short_Name='{}'".format(_Short_Name))[0][
                   0]) > 0:  # [(0,)]
            choice = QMessageBox.question(self, 'Change', '项目已存在，确认修改项目信息？', QMessageBox.Yes | QMessageBox.No)
            if choice == QMessageBox.Yes:  # 使用Short_Name做为主键，不可重复
                sql = "UPDATE BASE SET Project='{Project}',Project_Address='{Project_Address}',Party_A='{Party_A}',Project_Num='{Project_Num}',Party_B='{Party_B}',Contract_Amount={Contract_Amount},Category='{Category}',Tag='{Tag}' where Short_Name='{Short_Name}'".format(
                    Project=_Project, Project_Address=_Project_Address, Party_A=_Party_A, Project_Num=_Project_Num,
                    Party_B=_Party_B, Contract_Amount=_Contract_Amount, Category=_Category, Tag=_Tag,
                    Short_Name=_Short_Name)
                self.parent().databaseOprate(sql)
            elif choice == QMessageBox.No:
                self.reject()
        else:
            sql = "INSERT INTO  BASE(Project,Short_Name,Project_Address,Party_A,Project_Num,Party_B,Contract_Amount,Category,Tag)  VALUES('{Project}','{Short_Name}','{Project_Address}','{Party_A}','{Project_Num}','{Party_B}',{Contract_Amount},'{Category}','{Tag}')".format(
                Project=_Project, Short_Name=_Short_Name, Project_Address=_Project_Address, Party_A=_Party_A,
                Project_Num=_Project_Num, Party_B=_Party_B, Contract_Amount=_Contract_Amount, Category=_Category,
                Tag=_Tag)
            self.parent().databaseOprate(sql)
        self.reject()
        # print(self.parent())


if __name__ == '__main__':
    pass
