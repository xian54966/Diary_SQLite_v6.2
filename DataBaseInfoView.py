# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xi on 2020-10-25
from PyQt5 import QtSql, QtCore
from PyQt5.QtWidgets import QHeaderView, QDialog

from Resource.DataBaseInfoView_ui import Ui_DataBaseInfo


class BaseInfoView_Dialog(QDialog, Ui_DataBaseInfo):
    def __init__(self, parent):
        super(BaseInfoView_Dialog, self).__init__(parent)
        self.setupUi(self)

        self.showMaximized()
        # setWindowFlags(Qt.WindowMinMaxButtonsHint)

        # 使用QTableview内置'QsqlTabelModel'数据模型，https://www.codercto.com/a/19041.html
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        # db.setHostName('主机名')
        db.setDatabaseName(self.parent().lineEdit_mdb_path.text())
        # db.setUserName('用户名')
        # db.setPassword('Diray')
        db.open()
        # 实例化一个可编辑数据模型
        self.model = QtSql.QSqlTableModel()
        # 设置代理模型
        self.proxy_model = QtCore.QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.tableView.setModel(self.proxy_model)

        self.model.setTable(self.parent().comboBox.currentText())  # 设置数据模型的数据表
        self.model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)  # 模型的所有更改将立即作用于数据库
        self.model.select()  # 查询所有数据
        # 首次加载只加载256行数据，所以rowCount只能取到256
        while self.model.canFetchMore():
            self.model.fetchMore()

        # 水平方向标签拓展剩下的窗口部分，填满表格
        # self.tableView.horizontalHeader().setStretchLastSection(True)
        # 水平方向，表格大小拓展到适当的尺寸
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 对列单独设置固定宽度
        column_width = {}
        if self.parent().comboBox.currentText() == 'BASE':
            print('查询BASE表')
            column_width = {1: 120, 2: 45, 4: 80, 6: 80, 7: 80}  # {列号：宽度}
        elif self.parent().comboBox.currentText() == 'Diary':
            print('查询Diary表')
            column_width = {0: 40, 1: 15, 2: 130, 3: 130, 4: 180, 6: 200}  # {列号：宽度}
        print('width:', column_width)
        for k, v in column_width.items():
            self.tableView.horizontalHeader().setSectionResizeMode(k, QHeaderView.Fixed)
            self.tableView.setColumnWidth(k, v)  # 设置固定宽度

    def add_row(self):
        """表格最后追加一行空行。一次只能增加一行，输入数据自动更新至数据库。简单方法看新增加行行号由星号转为数字的时候可以新增下一行"""
        # print(self.tableView.currentIndex())
        # print('RowCount1:',self.model.rowCount())
        # #首次加载只加载256行数据，所以rowCount只能取到256
        # while self.model.canFetchMore():
        #     self.model.fetchMore()
        self.model.insertRow(self.model.rowCount())
        self.tableView.scrollToBottom()

    def del_row(self):
        """删除所选单元格所在整行数据，支持多选连续或者不连续单元格"""
        indexs = self.tableView.selectionModel().selection().indexes()
        print(indexs)
        if len(indexs) > 0:
            for index in indexs:
                self.model.removeRows(index.row(), 1)
        self.model.select()  # 刷新显示
        # 滚动到之前的焦点
        while self.model.canFetchMore():  # 还是先需要加载完成所有数据
            self.model.fetchMore()
        self.tableView.verticalScrollBar().setSliderPosition(index.row() - 1)

    # def locate_up(self):
    #     # http://www.voidcn.com/article/p-kjemvkao-bwn.html
    #     print('start1:',self.start.row(),self.start.column())
    #     matches = (self.model.match(self.start, QtCore.Qt.DisplayRole, '{}'.format(self.lineEdit.text()), 1, QtCore.Qt.MatchContains|QtCore.Qt.MatchRecursive))
    #     if matches:
    #         index = matches[0]
    #         # index.row(), index.column()
    #         # print(index.row(), index.column())
    #         self.tableView.clearSelection()
    #         self.tableView.selectionModel().select(index, QtCore.QItemSelectionModel.Select)    #https://blog.csdn.net/LaoYuanPython/article/details/104101572
    #         # a=3 if index.row()>=3 else 0
    #         # self.tableView.verticalScrollBar().setSliderPosition(index.row()-a)
    #         self.start = self.model.index(self.tableView.selectionModel().selectedIndexes()[0].row()+1,self.tableView.selectionModel().selectedIndexes()[0].column())
    #         print('start2:',self.start.row(),self.start.column())
    #     else:
    #         QMessageBox.warning(self,'提示','未找到关于“{}”的内容！'.format(self.lineEdit.text()))
    #

    def filter(self):
        self.proxy_model.setFilterKeyColumn(-1)  # 设置-1为过滤所有列
        self.proxy_model.setFilterFixedString('{}'.format(self.lineEdit.text()))

    def jump_to(self):
        if a:=int(self.lineEdit_2.text()):
            if a==1:
                self.tableView.scrollToTop()
            elif a==-1:
                self.tableView.scrollToBottom()
            else:
                self.tableView.verticalScrollBar().setSliderPosition(a - 1) #定位到目标行的上一行，美观。
