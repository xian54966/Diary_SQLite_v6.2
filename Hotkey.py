# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Xi on 2019-07-22
from PyQt5.QtCore import QThread, pyqtSignal
import win32con
import ctypes
import ctypes.wintypes
import time

user32 = ctypes.windll.user32  # 加载user32.dll

class Hotkey(QThread):  # 创建一个Thread.threading的扩展类
    # 自定义信号
    hotkey = pyqtSignal()

    def run(self):
        print('开启监听线程')
        if not user32.RegisterHotKey(None, 99, win32con.MOD_CONTROL, ord('Q')):  # 注册快捷键Ctrl+Q并判断是否成功，该热键用于执行一次需要执行的内容。
            print("Unable to register id", 99)  # 返回一个错误信息

        # 以下为检测热键是否被按下，并在最后释放快捷键
        try:
            msg = ctypes.wintypes.MSG()

            while True:
                if user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == win32con.WM_HOTKEY:
                        if msg.wParam == 99:
                            print('快捷键按下')
                            self.hotkey.emit()
                            time.sleep(0.1)

                            # return

                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageA(ctypes.byref(msg))

        finally:
            user32.UnregisterHotKey(None, 99)  # 必须得释放热键，否则下次就会注册失败，所以当程序异常退出，没有释放热键，
            # 那么下次很可能就没办法注册成功了，这时可以换一个热键测试
