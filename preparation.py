
'''
导入模块
'''
# import logging
import logging.handlers
import datetime,time
import os

import itertools
import sys
import openpyxl
import threading
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject, QPoint, QCoreApplication
from PyQt5.QtGui import QFont, QIcon, QPixmap, QTextCharFormat, QPen, QTextCursor, QColor, \
    QEnterEvent, QTextBlockFormat
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog, QInputDialog, QLineEdit, \
    QDockWidget, QLabel, QSystemTrayIcon, QAction, QMessageBox, QMenu, QColorDialog, QGridLayout, QVBoxLayout, \
    QTextEdit, QPlainTextEdit, QSizePolicy
from PyQt5.uic import loadUi


import asyncio
import zlib
import json
import requests
from aiowebsocket.converses import AioWebSocket



'''
关键词筛选列表
'''
whiteUser = []
blackUser = []
keywords = []
filterKWs = []


'''
初始值
'''
initsize = 25
initlinenum = 7
initlineheight = 40
initusercolor = '#ff6600'
initcomcolor = '#006600'
initfont = '宋体'
initbackground = os.getcwd() + r'\config\background_70.png'


'''
配置文件路径
'''
iconPath = os.getcwd() + r'\config\icon.jpg'
settingPath = os.getcwd() + r'\config\BiliComment.xlsx'



'''
日志对象 
'''
if not os.path.exists('log'):
    os.mkdir('log')

def creatLogger():
    logger = logging.getLogger('mylogger')
    logger.setLevel(logging.DEBUG)
    # 全部日志处理器
    rf_handler = logging.handlers.TimedRotatingFileHandler('log/all.log', when='midnight', interval=1, backupCount=7,
                                                               atTime=datetime.time(0, 0, 0, 0))
    rf_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    # error日志处理器
    f_handler = logging.FileHandler('log/error.log')
    f_handler.setLevel(logging.ERROR)
    f_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"))
    # 加入logger
    logger.addHandler(rf_handler)
    logger.addHandler(f_handler)
    # 返回设置好的logger对象
    return logger

# 实例化
logger = creatLogger()


'''
自定义信号源对象类型，一定要继承自 QObject
'''
class MySignals(QObject):
    # 定义一种信号，两个参数 类型分别是： QTextBrowser 和 字符串
    # 调用 emit方法 发信号时，传入参数 必须是这里指定的 参数类型
    text_print = QtCore.pyqtSignal(int, str)
    # 还可以定义其他种类的信号
    my_Signal = QtCore.pyqtSignal(str)
    new_comment = QtCore.pyqtSignal(bool,str)
    otherChange = QtCore.pyqtSignal(str,str)
    sizeChange = QtCore.pyqtSignal(str,int)
    fontChange = QtCore.pyqtSignal(QFont)

# 实例化
global_ms = MySignals()