from preparation import *


class TUOPAN(QObject):
    def __init__(self):
        super(TUOPAN, self).__init__()
        self.Ui_init()

    def Ui_init(self):
        # -------------------- 托盘开始 ----------------
        # 在系统托盘处显示图标
        self.tp = QSystemTrayIcon(self)
        self.tp.setIcon(QIcon('./config/icon.jpg'))
        # 设置系统托盘图标的菜单
        self.a1 = QAction('&主窗口', triggered=lambda:global_ms.my_Signal.emit('MainWindow'))
        self.a2 = QAction('&开始/更新', triggered=lambda:global_ms.my_Signal.emit('start'))
        self.a3 = QAction('&关闭', triggered=lambda:global_ms.my_Signal.emit('close'))
        self.a4 = QAction('&设置', triggered=lambda:global_ms.my_Signal.emit('setting'))
        self.a5 = QAction('&退出', triggered=lambda:global_ms.my_Signal.emit('exit'))  # 直接退出可以用qApp.quit
        self.tpMenu = QMenu()
        self.tpMenu.addAction(self.a1)
        self.tpMenu.addAction(self.a2)
        self.tpMenu.addAction(self.a3)
        self.tpMenu.addAction(self.a4)
        self.tpMenu.addAction(self.a5)
        self.tp.setContextMenu(self.tpMenu)
        # 点击活动连接到函数处理
        self.tp.activated.connect(self.act)
        # 不调用show不会显示系统托盘
        self.tp.show()
        # -------------------- 托盘结束 ------------------


    def act(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2:
            global_ms.my_Signal.emit('MainWindow')