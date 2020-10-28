# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xi on 2019-06-18
# from PyQt5.Qt import *
import sys
from Hotkey import Hotkey
from Trayicon import TrayIcon
from Resource.MainWindow_ui import Ui_MainWindow
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, pyqtSignal
from PyQt5.QtWidgets import QApplication, QStatusBar, QMenu, QFileDialog, QTreeWidgetItem, \
    QMainWindow, QTableWidgetItem, QLabel, QInputDialog, QMessageBox, QHeaderView
from PyQt5.QtNetwork import QLocalSocket, QLocalServer
# from pysqlcipher3 import dbapi2 as sqlite
import sqlite3
import os, threading
from datetime import datetime
import configparser
import time
import xlwings as xw
import pythoncom
from AddProject import AddProject_Dialog
from FindItem import Find_Dialog
from DataBaseInfoView import BaseInfoView_Dialog

class Main_Window(QMainWindow, Ui_MainWindow):
    signal_shortname = pyqtSignal(str)

    def __init__(self):
        super(Main_Window, self).__init__()
        self.setupUi(self)
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.m_flag = None  # 鼠标按、松标志
        self.s_flage = 0  # 按照时间还是项目查询标志
        self.file_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前绝对路径
        # 启动热键
        self.hotkey_thread = Hotkey()
        self.hotkey_thread.hotkey.connect(self.restore)
        self.hotkey_thread.start()

        self.setWindowOpacity(0.95)  # 设置窗口透明度
        self.setWindowFlag(Qt.FramelessWindowHint)  # 无边框，置顶，| Qt.WindowStaysOnTopHint

        # 状态栏显示当前时间
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.timelabel = QLabel()
        self.statusbar.addPermanentWidget(self.timelabel)

        self.timer = QTimer()
        self.timer.timeout.connect(self.brushTime)
        self.timer.start(1000)

        self.verlabel = QLabel()
        self.statusbar.addPermanentWidget(self.verlabel)
        self.verlabel.setText('v_6.2')

        # 设置QTbaleWidegt初始行数一行
        self.tableWidget1.setRowCount(1)
        self.tableWidget2.setRowCount(1)
        self.tableWidget3.setRowCount(1)
        # 设置列宽

        # self.tableWidget1.horizontalHeader().setStretchLastSection(True)#最后一列自动填充空白
        # self.tableWidget1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # 按文本长度调整列宽
        # self.tableWidget1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # 平均分配列宽
        # 字段名
        self.field = ['ID', 'State', 'Start_Time', 'Finsh_Time', 'Project_Name', 'Contents', 'Remarks']

        # 将ContextMenuPolicy设置为Qt.CustomContextMenu，否则无法使用customContextMenuRequested信号
        # self.tableWidget1.setContextMenuPolicy(Qt.CustomContextMenu)
        # 创建菜单1，设置任务状态,静态菜单创建一次，后期调用
        self.menu1 = QMenu()
        self.item1 = self.menu1.addAction('→')
        self.item2 = self.menu1.addAction('√')
        self.item3 = self.menu1.addAction('↓')
        self.item4 = self.menu1.addAction('●')
        # 创建菜单2，用于QTableWidget表单项增删清空，静态菜单创建一次，后期调用
        self.menu2 = QMenu()
        self.item5 = self.menu2.addAction('Add')
        self.item6 = self.menu2.addAction('Delete')
        self.item7 = self.menu2.addAction('Clear')
        ## 创建菜单3，用于日期目录树的右键导出到Excel操作
        self.menu3 = QMenu()
        self.item8 = self.menu3.addAction('Export Completed Tasks')
        self.item9 = self.menu3.addAction('Export Migrated Tasks')
        self.item10 = self.menu3.addAction('Export Cancelled Tasks')
        self.item11 = self.menu3.addAction('Export All Tasks')
        ## 创建菜单4，用于项目分类目录树的右键导出到Excel操作
        self.menu4 = QMenu()
        self.item12 = self.menu4.addAction('Export Project Data')

        # s设置托盘图标
        self.tray = TrayIcon(self)
        self.tray.show()

        # 设置数据文件夹，存放导出的数据文件
        if not os.path.exists('Data'):
            os.mkdir('Data')
            print('创建数据文件夹成功')
            self.statusbar.showMessage('创建数据文件夹成功')
        else:
            print('附件文件夹已存在')
            self.statusbar.showMessage('附件文件夹已存在')
        # # 加载配置文件中上次成功保存的数据库地址
        self.config = configparser.ConfigParser()
        self.config.read('config.ini', encoding='utf-8-sig')  # ini文件存在即读取，不存在即创建
        if self.config.has_section('Path') and self.config.has_section('TableName'):
            self.lineEdit_mdb_path.setText(self.config.get('Path', 'path'))
            self.comboBox.addItem(self.config.get('TableName', 'tablename'))

        self.clearTableWdiget()
        self.treeWidget.clear()
        # 连接数据库
        if os.path.exists(self.lineEdit_mdb_path.text()) and os.path.isfile(self.lineEdit_mdb_path.text()):
            self.conn = sqlite3.connect(self.lineEdit_mdb_path.text(), check_same_thread=False)
            self.statusbar.showMessage('数据库连接成功')
            self.drawTreeByDate()
        else:
            self.conn = None
        # 因为resizeEvent事件调整TableWidget宽度时，只对当前QToolBox当前page生效,所以监听ToolBox的currentChanged事件，手动触发reziseEvent事件
        # self.toolBox.currentChanged.connect(lambda: self.resize(self.width() + 1, self.height() + 1))

        # 设置列宽
        for i in range(5, 7):
            self.tableWidget1.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            self.tableWidget2.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            self.tableWidget3.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        for a, b in enumerate([30, 40, 90, 90, 100]):
            self.tableWidget1.setColumnWidth(a, b)
            self.tableWidget2.setColumnWidth(a, b)
            self.tableWidget3.setColumnWidth(a, b)

        # # 初始化窗口时禁用备注栏QTextEdit
        # self.frame.setVisible(False)

        # 设置当前ToolBox页面
        self.toolBox.setCurrentIndex(0)

        # 实时检测线程数，用来判断导出Excel线程是否都完成。
        self.thread_count1 = threading.activeCount()
        s = threading.Thread(target=self.checkthread, args=(self.thread_count1,))
        s.setDaemon(True)  # 否则窗口关闭后，子线程不退出
        s.start()

    #############################（开始）窗口拖动##################################
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)  # 更改窗口位置
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(Qt.ArrowCursor)

        #############################（结束）窗口拖动##################################

    def brushTime(self):
        """实时刷新状态栏时间显示"""
        self.timelabel.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S %A"))

    def isFieldExist(self):
        """判断字段是否存在，从而判断数据库文件是否存在。
        根据combobox当前表名，尝试查询数据库内置表SQLITE_MASTER，
        根据返回当前表结构判断是否含有‘Start_Time'字段，从而确定是否为需要的主表。有时候会连接到当前数据库其他表
        根据返回值判断是否连接成功"""
        if self.conn:
            cursor = self.conn.cursor()
            # cursor.execute("PRAGMA key = 'Diray';")
            # sql="select sql from sqlite_master where name='%s';"%(self.comboBox.currentText())
            cursor.execute("select * from sqlite_master where name='%s';" % (self.comboBox.currentText()))
            res = cursor.fetchall()
            print('zhel', res[0][4])
            if 'Start_Time' not in (res[0][4]):
                QMessageBox.warning(self, '错误', '表名选择错误,重新选择数据库文件并选择正确表名', QMessageBox.Yes)
                cursor.close()
                return False
            else:
                # self.creatIni()  # 既然都成功，更新下关键信息
                return True
        else:
            QMessageBox.warning(self, '错误', '未连接数据库', QMessageBox.Yes)
            return False

    def createMDB(self):
        """用于初始使用时创建数据库使用。以Combox内容为文件名创建数据库，并初始化数据库结构"""
        # 判断Combox文本是否为空
        if self.comboBox.currentText() == '':
            print('请输入表名，且表名不能为数字开头，建议使用英文，可以使用中文！')
            QMessageBox.warning(self, '提示', '请输入表名，且表名不能为数字开头，建议使用英文，可以使用中文！', QMessageBox.Yes)
            self.statusbar.showMessage(u'请输入表名，且表名不能为数字开头，建议使用英文，可以使用中文！')
            return
        path = QFileDialog.getExistingDirectory(self, '选择数据库保存位置')
        if not path:
            print('取消选择！！')
            return
        print(path)
        self.conn = sqlite3.connect(path + '/Data.db', check_same_thread=False)
        self.lineEdit_mdb_path.setText(path + '/Data.db')
        cursor = self.conn.cursor()
        # cursor.execute("PRAGMA key = 'Diray';")
        cursor.execute("CREATE TABLE  %s "
                       "('ID' INTEGER  PRIMARY KEY AUTOINCREMENT, "
                       "'State'   TEXT ,   "
                       "'Start_Time'  TEXT, "
                       "'Finsh_Time'  TEXT,"
                       "'Contents'    TEXT ,"
                       "'Remarks' TEXT );" % (self.comboBox.currentText()))
        cursor.execute(
            "INSERT INTO  %s(State,Start_Time)  VALUES('→','%s')" % (self.comboBox.currentText(), datetime.now()))
        # 创建BASE表，来存储项目基本信息
        cursor.execute(
            'CREATE TABLE "BASE" ("Project"	TEXT,"Short_Name"	TEXT,"Project_Address"	TEXT,"Party_A"	TEXT,"Project_Num"	TEXT,"Party_B"	TEXT,"Contract_Amount"	INTEGER,"Category"	TEXT,"Tag" TEXT,PRIMARY KEY("Short_Name"));')
        # 创建一条数据，Category='待分类'，供后续没有明确项目归属的记录使用，方便使用ByName方式下查看
        cursor.execute(
            "insert into BASE(Category) values ('待分类')")
        self.conn.commit()
        print('创建成功')
        self.creatIni()
        self.drawTreeByDate()
        self.statusbar.showMessage('数据库创建成功')

    def choose_mdb(self):
        """选择数据库按钮，查询数据库表名，加载到Combox供下拉使用"""
        path = QFileDialog.getOpenFileName(self, '选择数据库文件', '', 'All(*.*);;SQLite数据库(*.db)',
                                           'SQLite数据库(*.db)')
        if path[0] == '':
            print('取消选择！')
            return

        print(path)
        self.lineEdit_mdb_path.setText(path[0])
        try:
            self.conn = sqlite3.connect(path[0], check_same_thread=False)
            cursor = self.conn.cursor()
            # cursor.execute("PRAGMA key = 'Diray';")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            name = cursor.fetchall()
            print(name)
            self.comboBox.clear()
            for item in name:
                self.comboBox.addItem(item[0])
            cursor.close()
            # self.conn.close()
        except Exception as e:
            print(e)
            self.statusbar.showMessage(str(e))

    def creatIni(self):
        """记录更新数据库路径，记录当前表名，供下次直接读取使用"""
        # 写配置文件，记录常用配置
        if not self.config.has_section('Path'):
            self.config.add_section('Path')
        self.config.set('Path', 'path', self.lineEdit_mdb_path.text())
        if not self.config.has_section('TableName'):
            self.config.add_section('TableName')
        self.config.set('TableName', 'tablename', self.comboBox.currentText())
        with open('config.ini', 'w', encoding='UTF-8') as f:
            self.config.write(f)

    def drawTreeByDate(self):
        """按照时间分组绘制树形列表
        """
        if self.isFieldExist():  # 判断当前表为所要查询的主表
            self.treeWidget.clear()
            self.s_flage = 1  # 设置项目分组标识，1为时间分组，2为项目分组

            # 当使用ByDate方式查询时，解禁TableWidget123
            self.toolBox.setItemEnabled(1, True)
            self.toolBox.setItemEnabled(2, True)
            # self.creatIni()     #记录配置文件
            # 绘制树形列表
            ##########################
            cursor = self.conn.cursor()
            # cursor.execute("PRAGMA key = 'Diray';")
            year_list = [year for year in cursor.execute(
                " SELECT DISTINCT strftime('%%Y',  Start_Time)  as year from %s;" % self.comboBox.currentText())]
            print('year_list', year_list)

            for year in list(year_list):
                child1 = QTreeWidgetItem(self.treeWidget)
                child1.setText(0, str(year[0]) + '年')
                # print(year)
                # 设置月份节点
                for month in cursor.execute(
                        "SELECT DISTINCT strftime('%%m', Start_Time)  as month from  %s  where strftime('%%Y', Start_Time) = '%s'" % (
                                self.comboBox.currentText(), year[0])):
                    child2 = QTreeWidgetItem(child1)
                    child2.setText(0, str(month[0]) + '月')
                    # print(year[0], month[0])

            # 设置日期节点
            # 获取根目录个数
            for i in range(self.treeWidget.topLevelItemCount()):
                nyear = self.treeWidget.topLevelItem(i).text(0)
                # print('年',nyear)
                for x in range(self.treeWidget.topLevelItem(i).childCount()):
                    # 遍历顶层菜单的子菜单，获取月份
                    nmonth = self.treeWidget.topLevelItem(i).child(x).text(0)
                    # print('月',nmonth)

                    # 查询数据库获取天
                    days = ((cursor.execute(
                        "SELECT DISTINCT strftime('%%d', Start_Time)  as day from  %s  where strftime('%%Y', Start_Time) = '%s' and strftime('%%m', Start_Time) = '%s'" % (
                            self.comboBox.currentText(), nyear.rstrip('年'), nmonth.rstrip('月')))).fetchall())

                    for c, day in enumerate(sorted(days)):  # 这里需要列表排一下序，虽然获取到的list是顺序排列但是有奇怪的事发生
                        # "SELECT distinct day (Start_Time) from 表1 where year (Start_Time)=%s and month (Start_Time)=%s;" % (
                        #         nyear.rstrip('年'), nmonth.rstrip('月'))):
                        week = datetime(year=int(nyear.rstrip('年')), month=int(nmonth.rstrip('月')),
                                        day=int(day[0])).strftime('%w')  # 星期（0-6），星期天为星期的开始
                        if week == '0':
                            week = 7
                        # print('星期', week)
                        child3 = QTreeWidgetItem(self.treeWidget.topLevelItem(i).child(x))
                        child3.setText(0, str(day[0]) + '日 星期%s' % week)
                        # print(nyear, nmonth, day[0])

                        # 找到最新日期设置为当前且点击查看，解决最新日期节点展开而其他闭合问题；解决新建行后刷新问题（ByDate方式）
                        if i == self.treeWidget.topLevelItemCount() - 1:  # 最新年份
                            if x == self.treeWidget.topLevelItem(i).childCount() - 1:  # 最新月份
                                if c == len(days) - 1:  # 最新日期
                                    self.treeWidget.setCurrentItem(child3)
                                    self.tree_item_click()

            self.statusbar.showMessage('节点树绘制完毕！')
            cursor.close()

    def drawTreeByName(self):
        """按照项目分类绘制树形列表        """
        if self.isFieldExist():
            self.s_flage = 2  # 设置ByName标志
            self.treeWidget.clear()
            # 当使用ByName方式查询时，结果显示在TableWidget1中，禁用其他两个
            self.toolBox.setItemEnabled(1, False)
            self.toolBox.setItemEnabled(2, False)
            '''按照项目名称分组绘制左侧树形列表'''
            categorys = [_[0] for _ in set(self.databaseOprate("select Category from Base")) if _[
                0]]  # [('主体沉降',), ('基坑监测',), ('基坑监测',), ('基坑监测',), (None,), ('主体沉降',)] --->> ['主体沉降', '基坑监测']
            for category in sorted(categorys):
                root = QTreeWidgetItem(self.treeWidget)
                root.setText(0, category)  # 设置根目录
                for i in sorted(self.databaseOprate("select * from BASE WHERE Category='{}'".format(category))):
                    child = QTreeWidgetItem(root)
                    child.setText(0, i[1])
        self.treeWidget.expandAll()

    def clearTableWdiget(self):
        # 每次点击初始化窗口为0行
        self.tableWidget1.setRowCount(0)
        self.tableWidget2.setRowCount(0)
        self.tableWidget3.setRowCount(0)

    def writeTable(self, content, tablewidget):
        """查询信息写入表格"""
        for y in range(len(self.field)):  # 一共有7列
            item = content[y]
            newItem = QTableWidgetItem(str(item))
            # 设置首列‘ID’为不可编辑
            if y == 0:
                newItem.setFlags(Qt.ItemIsEnabled)
            newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 文本居中
            tablewidget.setItem(tablewidget.rowCount() - 1, y, newItem)
            tablewidget.resizeRowsToContents()  # 设置根据内容调整行高

    def tree_item_click(self):
        """树形列表项单击事件"""
        self.resize(self.width() - 1, self.height() - 1)  # 这里重置下窗口大小，需要触发resizeEvent事件进行列的宽度分配。这里使用减，因为最大化的时候+1不好使。
        # 每次点击初始化窗口为0行
        self.clearTableWdiget()

        # 临时关闭cellchanged()的信号
        self.tableWidget1.blockSignals(True)
        self.tableWidget2.blockSignals(True)
        self.tableWidget3.blockSignals(True)
        print('关闭信号监听')
        # print('点击')
        # print('当前节点：',self.treeWidget.currentItem().text(0))
        # print('当前节点父节点：',self.treeWidget.currentItem().parent().text(0))
        # print('当前节点子节点：',self.treeWidget.currentItem().child(0))
        cursor = self.conn.cursor()
        # cursor.execute("PRAGMA key = 'Diray';")
        if self.s_flage == 2:  # 按照项目查询
            print('按照项目查询')
            name = self.treeWidget.currentItem().text(0)
            for item in cursor.execute(
                    "SELECT * from %s where Project_Name LIKE'%%%s%%'" % (self.comboBox.currentText(), name)):  # 百分号要写俩
                self.tableWidget1.insertRow(self.tableWidget1.rowCount())
                self.writeTable(item, self.tableWidget1)

        else:  # 按照时间查询
            print('按照时间查询')
            if not self.treeWidget.currentItem().child(0):
                print('当前为第三节点！')
                day = self.treeWidget.currentItem().text(0).split('日')[0]
                # day = self.treeWidget.currentItem().text(0).rstrip('日')
                month = self.treeWidget.currentItem().parent().text(0).rstrip('月')
                year = self.treeWidget.currentItem().parent().parent().text(0).rstrip('年')
                # print(year)

                # 绘制当天任务清单
                for content in cursor.execute(
                        "SELECT *  from %s where strftime('%%Y-%%m-%%d',Start_Time)='%s' ;" % (
                                self.comboBox.currentText(), '-'.join([year, month, day]))):
                    # print('00000',self.tableWidget1.rowCount())
                    self.tableWidget1.insertRow(self.tableWidget1.rowCount())
                    self.writeTable(content, self.tableWidget1)
                    # 绘制迁移清单
                for content in cursor.execute(
                        "SELECT *  from %s  where strftime('%%Y-%%m-%%d',Start_Time)<'%s' and state ='→';" % (
                                self.comboBox.currentText(),
                                '-'.join([year, month, day]))):
                    self.tableWidget2.insertRow(self.tableWidget2.rowCount())
                    self.writeTable(content, self.tableWidget2)
                # 绘制取消及长期任务清单
                for content in cursor.execute(
                        "SELECT *  from %s where strftime('%%Y-%%m-%%d',Start_Time)<='%s' and (state ='↓' or state ='●');" % (
                                self.comboBox.currentText(),
                                '-'.join([year, month, day]))):
                    self.tableWidget3.insertRow(self.tableWidget3.rowCount())
                    self.writeTable(content, self.tableWidget3)

            else:
                print('非第三节点！')
        cursor.close()
        # 临时打开cellchanged()的信号
        self.tableWidget1.blockSignals(False)
        self.tableWidget2.blockSignals(False)
        self.tableWidget3.blockSignals(False)
        print('打开信号监听！')

    def modify(self):  # 槽函数中调用sender()，可以获取信号来源
        """单元格修改事件，右ItemChange事件触发"""
        if not self.conn:  # 说明没有连接数据库，itemChanged事件不起作用
            self.statusbar.showMessage('请先登录!!')
            return

        print('进入单元格修改')
        self.statusbar.showMessage('进入单元格修改')
        if cur_item := self.sender().currentItem():  # 判断当前单元格是否已经附加了Item
            print('当前行号：', self.sender().currentRow())
            print('当前列号：', self.sender().currentColumn())
            text = cur_item.text()
            print('当前cell文本：', text)

            # 判断手动修改日期时的日期格式是否正确
            if self.sender().currentColumn() in (2, 3):
                try:
                    datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
                except:
                    QMessageBox.warning(self, "提示", "日期格式错误", QMessageBox.Yes)
                    return

            id = self.sender().item(self.sender().currentRow(), 0).text()
            print('当前行ID:', id)
        else:
            return
        cursor = self.conn.cursor()
        # cursor.execute("PRAGMA key = 'Diray';")
        try:
            # print(self.field[self.sender().currentColumn()])
            sql = "UPDATE %s SET '%s' = '%s'  WHERE ID = %d" % (
                self.comboBox.currentText(), self.field[self.sender().currentColumn()], text, int(id))
            self.databaseOprate(sql)
            self.statusbar.showMessage('内容更新成功', 10 * 1000)
            print('内容更新成功')
        except Exception as e:
            # print(e)
            self.statusbar.showMessage(str(e), 10 * 1000)
        cursor.close()

    def tableMenu(self, pos):  # 用于TableWidegt右键菜单弹出
        # if self.conn and self.s_flage > 0:  # 说明没有连接数据库，TableWidegt右键菜单不起效
        if self.s_flage > 0:  # s_flage>0,说明已有数据连接
            print('弹出右键菜单')
            # 先判断当前单元格是在‘State’列
            if self.sender().currentColumn() == 1:
                print('State列右击')
                # menu.exec_(self.tableWidget1.mapToGlobal(pos))
                action = self.menu1.exec_(QCursor.pos())
                # try:  # 因为表格在初始化的时候设置了一行，并没有添加item，这里回报“AttributeError: 'NoneType' object has no attribute 'text'”
                if action == self.item1:
                    self.sender().currentItem().setText(u'→')
                    self.sender().setItem(self.sender().currentRow(), 3, QTableWidgetItem(""))
                elif action == self.item2:
                    self.sender().currentItem().setText('√')
                    # if self.sender().objectName()=='tableWidget2':
                    #     print('当前在tableWidget2里点击')
                    # 自动添加FInish_Time
                    strTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # self.sender().currentItem().setSelected(False)
                    # self.sender().item(self.sender().currentRow(),3).setSelected(True)
                    # 要命了，设置State为对号后同时填充Finshed_Time,,竟然只能触发State列的更改，还是两次。Modify()里只能是更新CurrentItemD数据，所以手动设置焦点或者手动再更新一次Finished_Time
                    self.sender().setCurrentItem(self.sender().item(self.sender().currentRow(), 3))
                    self.sender().setItem(self.sender().currentRow(), 3, QTableWidgetItem(strTime))
                    self.sender().currentItem().setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # 文本居中

                elif action == self.item3:
                    self.sender().currentItem().setText('↓')
                elif action == self.item4:
                    self.sender().currentItem().setText('●')

            else:
                print('其他列右击')
                action = self.menu2.exec_(QCursor.pos())
                try:  # 因为表格在初始化的时候设置了一行，并没有添加item，这里回报“AttributeError: 'NoneType' object has no attribute 'text'”
                    if action == self.item5:
                        self.newRow()
                    elif action == self.item6:
                        self.deleteRow()
                    elif action == self.item7:
                        self.clearCell()
                except Exception as e:
                    #     self.statusbar.showMessage(str(e), 20 * 1000)
                    QMessageBox.information(self, '错误', str(e), QMessageBox.Yes)
        else:
            QMessageBox.critical(self, '错误', '尚未生成目录索引或尚未连接数据库！', QMessageBox.Yes)

    def newRow(self):
        """添加新行"""
        print('增加行')
        print('当前行数：', self.sender().rowCount())
        # self.sender().setRowCount(self.sender().rowCount())
        # self.sender().insertRow(self.sender().rowCount())
        # 临时关闭cellchanged()的信号
        self.sender().blockSignals(True)
        strTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # self.sender().setItem(self.sender().rowCount() - 1, 2, QTableWidgetItem(strTime))
        if self.s_flage == 1:  # ByDate形式绘制目录树
            print('当前使用Date形式绘制目录')
            sql = "INSERT INTO  %s(State,Start_Time)  VALUES('→','%s')" % (self.comboBox.currentText(), strTime)
            self.databaseOprate(sql)
            self.drawTreeByDate()

        elif self.s_flage == 2:  # ByName形式绘制目录树
            print('当前使用Name形式绘制目录')
            if _treew_cur := self.treeWidget.currentItem():
                proName = _treew_cur.parent().text(0) + ' -> ' + _treew_cur.text(0)
                print(proName)
                sql = "INSERT INTO  %s(State,Start_Time,Project_Name)  VALUES('→','%s','%s')" % (
                    self.comboBox.currentText(), strTime, proName)
                self.databaseOprate(sql)
                self.drawTreeByName()
                # self.tree_item_click()  # 这里很巧妙，
                QMessageBox.warning(self, '提示', '请重新点击项目名称！', QMessageBox.Yes)
            else:
                QMessageBox.warning(self, '错误', '当前没有选中项目以刷新列表！', QMessageBox.Yes)

        # 临时打开cellchanged()的信号
        self.sender().blockSignals(False)

    def deleteRow(self):
        """删除新行并在数据库中删除相应数据"""
        id = self.sender().item(self.sender().currentRow(), 0).text()
        sql = "DELETE FROM %s WHERE ID = %s " % (self.comboBox.currentText(), id)
        self.databaseOprate(sql)
        # 相当于重新点击日期树中的天，刷新
        self.tree_item_click()

    def clearCell(self):
        """清空单元格数据"""
        self.sender().setItem(self.sender().currentRow(), self.sender().currentColumn(), QTableWidgetItem(''))

    def databaseOprate(self, sql):
        """数据库操作函数"""
        print('SQL语句:', sql)
        cursor = self.conn.cursor()
        # cursor.execute("PRAGMA key = 'Diray';")
        try:
            cursor.execute(sql)
            self.conn.commit()  # 提交更改
            result = cursor.fetchall()
            print('数据库查询结果：', result)
            print('数据库提交成功')
            self.conn.rollback()  # 错误回滚
            cursor.close()
            return result
        except Exception as e:
            QMessageBox.warning(self, 'Error', str(e), QMessageBox.Yes)

    def showTips(self):
        """气泡显示单元格内容"""
        print('单击单元格')
        tips = self.sender().currentItem().text()
        print(tips)
        self.sender().blockSignals(True)
        self.sender().currentItem().setToolTip(tips)  # 搞不懂为啥，设置气泡提示就触发ItemChanged()信号
        self.statusbar.showMessage(tips)
        self.sender().blockSignals(False)
        # # 隐藏备注栏
        # if self.frame.isVisible():
        #     self.frame.setVisible(False)
        #     self.resize(self.width() - 1, self.height() - 1)  # 这里重置下窗口大小，需要触发resizeEvent事件进行列的宽度分配。这里使用减，因为最大化的时候+1不好使。

    def quit(self):
        """退出程序"""
        self.statusbar.showMessage('正在保存，有点慢！！')
        self.creatIni()  # 退出前更新下配置信息
        if self.conn:
            self.conn.close()

        self.close()
        self.tray.setVisible(False)  # 关闭托盘图标显示

    def closewindow(self):  # 关闭按钮
        """最小化到托盘，并且断开数据库连接"""
        print('最小化')
        if self.conn:
            print(self.conn)
            self.conn.close()
            self.statusbar.showMessage('断开数据库连接！')
            print('断开数据库连接！')
        self.hide()

    def maximize(self):  # 最大化按钮
        """最大化窗口"""
        print('最大化')
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def minimize(self):  # 最小化按钮
        """最小化窗口显示"""
        print('最小化')
        if self.conn:
            print(self.conn)
            self.conn.close()
            self.statusbar.showMessage('断开数据库连接！')
            print('断开数据库连接！')
        self.hide()

    def restore(self):
        """还原窗口显示，并且重连数据库"""
        if self.isHidden():
            print('还原')
            if self.lineEdit_mdb_path.text():
                self.conn = sqlite3.connect(self.lineEdit_mdb_path.text(), check_same_thread=False)
                self.conn = sqlite3.connect(self.lineEdit_mdb_path.text(), check_same_thread=False)
                self.statusbar.showMessage('数据库已重新连接！')
                print('数据库已重新连接！')
            self.show()
        # self.setWindowFlag(Qt.WindowStaysOnTopHint)  # 窗口置顶
        else:
            self.minimize()

    def addProject(self):
        if self.conn:  # 检测是否已连接数据库
            # 先实例化新增项目子窗口，等待发送信息
            self.addproject = AddProject_Dialog(self)
            if self.sender().inherits('QTreeWidget'):  # 窗口打开信号来自ByName模式下双击Item
                print('双击来自QTreeWidget')
                self.signal_shortname.emit(self.sender().currentItem().text(0))
            self.addproject.show()
        else:
            QMessageBox.warning(self, 'Error', '请先连接数据库！', QMessageBox.Yes)

    def open_find_item(self):
        if self.conn:  # 检测是否已连接数据库
            # 实例化新增项目子窗口
            self.find = Find_Dialog(self)
            if self.sender().inherits('QTableWidget'):  # 判断信号来源
                print('操作来自双击QTableWidget')
                if self.sender().currentColumn() == 4:  # 限定接受Project_Name列双击
                    print('双击来自Project列')
                    self.find.signal_project_info.connect(self.get_data)
                    self.find.show()
            else:
                self.find.show()
        else:
            QMessageBox.warning(self, 'Error', '请先连接数据库！', QMessageBox.Yes)

    def get_data(self, data):  # 好麻烦！！！
        """Project列双击信号的槽函数，用于接收对话框传来的参数"""
        # print(self.sender().parent().toolBox.currentIndex())
        new_data = data.split('★')[-2] + ' -> ' + data.split('★')[1]
        print('new_data:', new_data)
        if self.sender().parent().toolBox.currentIndex() == 0:
            self.sender().parent().tableWidget1.setItem(self.sender().parent().tableWidget1.currentRow(), 4,
                                                        QTableWidgetItem(new_data))
            self.sender().parent().tableWidget1.currentItem().setTextAlignment(
                Qt.AlignHCenter | Qt.AlignVCenter)  # 文本居中
        elif self.sender().parent().toolBox.currentIndex() == 1:
            self.sender().parent().tableWidget2.setItem(self.sender().parent().tableWidget2.currentRow(), 4,
                                                        QTableWidgetItem(new_data))
            self.sender().parent().tableWidget1.currentItem().setTextAlignment(
                Qt.AlignHCenter | Qt.AlignVCenter)  # 文本居中
        elif self.sender().parent().toolBox.currentIndex() == 2:
            self.sender().parent().tableWidget3.setItem(self.sender().parent().tableWidget3.currentRow(), 4,
                                                        QTableWidgetItem(new_data))
            self.sender().parent().tableWidget1.currentItem().setTextAlignment(
                Qt.AlignHCenter | Qt.AlignVCenter)  # 文本居中
        # 信号源来自TableWidget双击，需要自动关闭子窗口
        self.find.accept()

    def show_base_info(self):
        """呼出对话框进行BASE表的查看编辑"""
        b_dialog=BaseInfoView_Dialog(self)
        b_dialog.exec()  #创建模态对话框

    def checkthread(self, count):  #
        """"监测开启写Excel线程前后，线程数差，用以检查写线程是否退出，推出后显示禁用的分类按钮.
        为啥禁用按钮？
        因为在时间目录树导出数据，马上切换到项目目录树内导出数据，未完成的线程会丢失焦点报错"""
        while True:
            # print('实时线程数差%s' % (threading.activeCount() - count))
            if threading.activeCount() - count == 1:
                if not self.pushButton_7.isVisible():
                    self.pushButton_7.setVisible(True)
                    print('项目按钮开启成功')

                elif not self.pushButton_6.isVisible():
                    self.pushButton_6.setVisible(True)
                    print('时间按钮开启成功')

            time.sleep(1)

    def treeMenu(self, pos):  # 用于目录树的右键菜单弹出
        print('弹出目录树右键菜单')
        self.tree_item_click()
        if self.conn and self.s_flage > 0:  # 判断是否连接数据库并且是否已生产目录，TreeWidegt右键菜单不起效
            if self.s_flage == 2:  # 按照项目分类标识
                # print(self.s_flage)
                print('项目模式，准备弹出菜单')

                action = self.menu4.exec_(QCursor.pos())
                if action == self.item12:
                    print("导出该项目数据%s" % self.treeWidget.currentItem().text(0))
                    t = threading.Thread(target=self.export,
                                         args=(self.s_flage, self.treeWidget.currentItem(), 'Project'))
                    t.start()
                    self.pushButton_6.setVisible(False)  # 开启新线程之后再禁用按钮，因为1s监测一次，要不新线程开启之前瞬间恢复禁用
            else:  # 按照日期分类标识
                print('日期模式，准备弹出菜单')

                action = self.menu3.exec_(QCursor.pos())
                if action == self.item8:
                    print("导出今日完成任务")
                    t = threading.Thread(target=self.export,
                                         args=(self.s_flage, self.treeWidget.currentItem(), 'Today'))
                    t.start()
                elif action == self.item9:
                    print("导出迁移任务")
                    t = threading.Thread(target=self.export,
                                         args=(self.s_flage, self.treeWidget.currentItem(), 'Migrated'))
                    t.start()
                elif action == self.item10:
                    print("导出取消任务")
                    t = threading.Thread(target=self.export,
                                         args=(self.s_flage, self.treeWidget.currentItem(), 'Cancel'))
                    t.start()
                elif action == self.item11:
                    print('按时间导出所有数据')
                    t = threading.Thread(target=self.export,
                                         args=(self.s_flage, self.treeWidget.currentItem(), 'All'))
                    t.start()
                self.pushButton_7.setVisible(False)  # 开启新线程之后再禁用按钮，因为1s监测一次，要不新线程开启之前瞬间恢复禁用
        else:
            QMessageBox.critical(self, '错误', '尚未生成目录索引或尚未连接数据库！', QMessageBox.Yes)

    def export(self, modle, current_item, im):
        """导出数据库到EXCEL文件"""
        # 连接数据库
        cursor = self.conn.cursor()
        # cursor.execute("PRAGMA key = 'Diray';")
        # 初始化
        pythoncom.CoInitialize()
        # Excel操作
        app = xw.App(visible=True, add_book=False)
        wb = app.books.add()
        wb.sheets[0].range('A1').value = self.field

        if modle == 2:  # ByName分类模式
            print('项目模式，准备生产excel文件')
            print('当前点击%s' % current_item.text(0))
            wb.sheets[0].range('A2').value = [item for item in cursor.execute(
                "SELECT * from %s where Project_Name LIKE'%%%s%%'" % (
                    self.comboBox.currentText(), current_item.text(0)))]
            self.xlsformat(wb.sheets[0], im, current_item.text(0))
            wb.save('{}\\Data\\{}({}).xlsx'.format(self.file_dir, current_item.text(0),
                                                   datetime.now().strftime('%Y-%m-%d')))
        else:  # ByDate分类模式
            print('日期模式，准备生产excel文件')
            day = current_item.text(0).split('日')[0]
            month = current_item.parent().text(0).rstrip('月')
            year = current_item.parent().parent().text(0).rstrip('年')
            cucrrent_date = '-'.join([year, month, day])  # 拼接当前日期  YYYY-MM-DD
            if im == 'All':
                wb.sheets[0].range('A2').value = [item for item in cursor.execute(
                    "SELECT * FROM %s" % (self.comboBox.currentText()))]
            elif im == 'Today':  # 此段代码参考tree_item_click()
                wb.sheets[0].range('A2').value = [item for item in cursor.execute(
                    "SELECT *  from %s where strftime('%%Y-%%m-%%d',Start_Time)='%s' ;" % (
                        self.comboBox.currentText(), cucrrent_date))]

            elif im == 'Migrated':
                wb.sheets[0].range('A2').value = [item for item in cursor.execute(
                    "SELECT *  from %s  where strftime('%%Y-%%m-%%d',Start_Time)<'%s' and state ='→';" % (
                        self.comboBox.currentText(),
                        cucrrent_date))]
            elif im == 'Cancel':
                wb.sheets[0].range('A2').value = [item for item in cursor.execute(
                    "SELECT *  from %s where strftime('%%Y-%%m-%%d',Start_Time)<='%s' and (state ='↓' or state ='●');" % (
                        self.comboBox.currentText(),
                        cucrrent_date))]
            self.xlsformat(wb.sheets[0], im, '-'.join([year, month, day]))  # 设置xls格式
            # wb.save('{}\\Data\\{}({}).xlsx'.format(self.file_dir, datetime.now().strftime('%Y-%m-%d'), im))
            wb.save('{}\\Data\\{}({}).xlsx'.format(self.file_dir, cucrrent_date, im))
        cursor.close()
        wb.close()
        app.quit()
        # 释放资源
        pythoncom.CoInitialize()

    def xlsformat(self, ws, im, date):
        """设置导出EXCEL文件格式"""
        # 设置列宽
        width_list = [4, 5, 15, 15, 25, 40, 28]
        for a, b in enumerate(width_list):
            ws.range(1, a + 1).column_width = b
        # 设置字体
        ws.used_range.api.Font.Name = '宋体'  # 设置字体
        ws.used_range.api.Font.Size = 10  # 设置字体大小
        ws.range('a1:g1').api.Font.Bold = True  # 首行标题加粗
        # 设置单元格属性
        ws.used_range.api.HorizontalAlignment = -4108  # 设置水平居中,默认垂直居中
        # ws.api.Columns(5).VerticalAlignment = -4130     #设置ProjectName列自动换行
        ws.api.Columns(6).VerticalAlignment = -4130  # 设置Contect列自动换行
        ws.api.Columns(7).VerticalAlignment = -4130  # 设置Remarks列自动换行
        # 设置边框
        ws.used_range.api.Borders(8).LineStyle = 1  # 上边框
        ws.used_range.api.Borders(9).LineStyle = 1  # 下边框
        ws.used_range.api.Borders(7).LineStyle = 1  # 左边框
        ws.used_range.api.Borders(10).LineStyle = 1  # 右边框
        ws.used_range.api.Borders(12).LineStyle = 1  # 内横边框
        ws.used_range.api.Borders(11).LineStyle = 1  # 内纵边框
        # 插入标题
        ws.api.Rows(1).Insert()  # 插入新行
        ws.range('a1:g1').api.merge()  # 合并单元格
        # 写入标题
        if im == 'All':
            ws.range('a1').value = '截至 %s 所有任务列表' % date
        elif im == 'Today':
            ws.range('a1').value = '今日 %s 完成任务列表' % date
        elif im == 'Migrated':
            ws.range('a1').value = '截至 %s 迁移任务列表' % date
        elif im == 'Project':
            ws.range('a1').value = ' %s 项目所有任务列表' % date  # 此处date为项目名
        ws.range('a1').api.Font.Size = 20
        ws.range('a1').api.Font.Bold = True
        ws.range('a1').api.HorizontalAlignment = -4108


if __name__ == '__main__':
    # 设置支持高分辨率屏幕自适应，否则，高分屏下位置错乱，尺寸失真
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    # 单实例运行
    serverName = 'myuniqueservername'
    socket = QLocalSocket()
    socket.connectToServer(serverName)

    # 如果连接成功，表明server已经存在，当前已有实例在运行
    if socket.waitForConnected(500):
        sys.exit(app.quit())

    # 没有实例运行，创建服务器
    localServer = QLocalServer()
    localServer.listen(serverName)

    try:
        window = Main_Window()
        window.show()
        sys.exit(app.exec_())
    finally:
        localServer.close()
