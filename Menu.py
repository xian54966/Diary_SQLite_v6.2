# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xi on 2019-07-28
import configparser
from PyQt5.QtWidgets import QMenu, QMessageBox


class MenuProject():  # 动态菜单，随调随用
    def __init__(self, parent):
        # 加载配置文件中上次成功保存的数据库地址
        try:
            self.config = configparser.ConfigParser()
            self.config.read('config.ini', encoding='utf-8-sig')

            # 创建菜单5，用于选择项目名称
            self.menu5 = QMenu()
            # print(self.config.sections())
            if self.config.has_section('ProjectName') and self.config.options('ProjectName'):
                for option in self.config.options('ProjectName'):
                    self.d = self.menu5.addMenu(option)
                    for item in tuple((self.config.get('ProjectName', option).split(','))) + tuple('+'):
                        self.a = self.d.addAction(item)
            else:
                QMessageBox.warning(parent,'Error','ProjectName下无类别！请前往config.ini确认',QMessageBox.Yes)
        except Exception as e:
            print(e)
            QMessageBox.information(parent, 'Error', str(e), QMessageBox.Yes)
