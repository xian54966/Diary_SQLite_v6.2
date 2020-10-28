#！/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xi on 2019-07-22
from  PyQt5.QtWidgets import QSystemTrayIcon,QMenu,QApplication,QAction
from PyQt5.QtGui import QIcon
import os

class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent):
        super(TrayIcon, self).__init__(parent)
        # self.tray = QSystemTrayIcon()  # 创建系统托盘对象

        self.icon = QIcon('Dairy.ico')  # 为了避免打包成EXE之后找不到图标，直接使用程序主目录
        # self.icon = QIcon(r'D:\OneDrive\PycharmProjects\Diary_SQLite\Diary_SQLite_v6.0\Resource\Images\Dairy.ico')  # 创建图标,得使绝对路径，要不打包exe后不能生成托盘
        self.setIcon(self.icon)  # 设置系统托盘图标
        self.activated.connect(self.iconClied)  # 设置托盘点击事件处理函数
        self.tray_menu = QMenu(QApplication.desktop())  # 创建菜单
        self.RestoreAction = QAction(u'还原 ', self, triggered=parent.restore)  # 添加一级菜单动作选项(还原主窗口)
        self.QuitAction = QAction(u'退出 ', self, triggered=parent.quit)  # 添加一级菜单动作选项(退出程序)
        self.tray_menu.addAction(self.RestoreAction)  # 为菜单添加动作
        self.tray_menu.addAction(self.QuitAction)
        self.setContextMenu(self.tray_menu)  # 设置系统托盘菜单

    def iconClied(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击"
        # print(reason)
        if reason == 2 or reason == 3:
            self.parent().restore()

    # def restore(self):
    #     print('还原')
    #     if self.parent().isVisible():
    #         self.parent().hide()
    #     else:
    #         self.parent().show()



    # def close(self):
    #     self.setVisible(False)
    #     self.parent().quit()