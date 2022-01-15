from preparation import *


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        loadUi('ui/MainWindow.ui', self)
        # 标题、图标
        self.setWindowTitle('主窗口')
        self.setWindowIcon(QIcon(iconPath))
        # 禁止最大化按钮
        self.setWindowFlags(Qt.WindowMinimizeButtonHint|Qt.WindowCloseButtonHint)
        # ui按钮链接
        self.Ui_init()

    def Ui_init(self):
        self.openSettingWinButton.triggered.connect(lambda: global_ms.my_Signal.emit('setting'))
        self.openAboutWinButton.triggered.connect(lambda: global_ms.my_Signal.emit('about'))
        self.startButton.clicked.connect(lambda: global_ms.my_Signal.emit('start'))
        self.closeButton.clicked.connect(lambda: global_ms.my_Signal.emit('close'))
