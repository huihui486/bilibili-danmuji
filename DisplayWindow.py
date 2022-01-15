from preparation import *


class DisplayWindow(QDockWidget):
    def __init__(self, parent=None):
        super(DisplayWindow, self).__init__(parent)
        loadUi('ui/DisplayWindow.ui', self)
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint|Qt.Tool)  # 置顶、无边框、隐藏任务栏
        self.setAttribute(Qt.WA_TranslucentBackground)    # 窗体背景透明
        self.setMouseTracking(True)  # 设置widget鼠标跟踪
        # print(self.width(), self.height())
        # 显示样式
        self.Userfont = QColor(initusercolor)
        self.Comfont = QColor(initcomcolor)
        # 初始化
        self.Ui_init()
        self.SignalConnect_init()
        # 设置鼠标跟踪判断扳机默认值
        self._initDrag()

    def Ui_init(self):
        '''
        由于在qt designer里弄不出理想的效果，所以这个窗口就用代码来写了
        '''
        # 底层label，设置背景图片
        self.backLabel = QLabel()
        self.backLabel.setObjectName("backLabel")
        pix = QPixmap(initbackground)
        self.backLabel.setPixmap(pix)
        self.backLabel.setScaledContents(True)
        self.gridLayout.addWidget(self.backLabel, 0, 26, 11, 11)

        # 中间层
        self.comWidget = QWidget()
        self.gridLayout.addWidget(self.comWidget, 0, 26, 11, 11)
        self.comVerticalLayout = QVBoxLayout(self.comWidget)
        self.comVerticalLayout.setObjectName("comVerticalLayout")
        # 添加textEdit用于显示弹幕，并初始化
        self.textEdit = QPlainTextEdit(self.comWidget)
        self.textEdit.setReadOnly(True)
        self.textEdit.setUndoRedoEnabled(False)
        self.textEdit.setMaximumBlockCount(initlinenum)
        font = QFont(initfont)
        font.setWordSpacing(20)
        self.textEdit.setFont(font)
        self.textEdit.setStyleSheet(
            f"font-size:{initsize}px;border: none; background-color: transparent; font-weight: bold;")
        self.comVerticalLayout.addWidget(self.textEdit)
        # 指针
        self.FontFormat = QTextCharFormat()
        self.BlockFormat = QTextBlockFormat()
        self.tc = self.textEdit.textCursor()
        # 设置行高，但不明显，可有可无
        self.BlockFormat.setLineHeight(initlineheight, QTextBlockFormat.FixedHeight)
        self.BlockFormat.setAlignment(Qt.AlignRight)
        self.tc.setBlockFormat(self.BlockFormat)
        self.textEdit.setTextCursor(self.tc)

        # 顶层，3个label用于调整大小时改变鼠标样式，并隔离textEdit
        self.topWidget = QWidget()
        self.bottomLabel = QLabel(self.topWidget)
        self.rightLabel = QLabel(self.topWidget)
        self.cornerLabel = QLabel(self.topWidget)
        self.bottomLabel.setObjectName("bottomLabel")
        self.rightLabel.setObjectName("rightLabel")
        self.cornerLabel.setObjectName("cornerLabel")
        self.gridLayout.addWidget(self.topWidget, 0, 26, 11, 11)
        self.topLayout = QGridLayout(self.topWidget)
        self.topLayout.setObjectName("topLayout")
        self.bottomLabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.rightLabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.cornerLabel.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.bottomLabel.setMaximumSize(999999999,20)
        self.rightLabel.setMaximumSize(20,999999999)
        self.cornerLabel.setMaximumSize(20,20)
        self.topLayout.addWidget(self.bottomLabel,1,0,Qt.AlignBottom)
        self.topLayout.addWidget(self.rightLabel,0,1,Qt.AlignRight)
        self.topLayout.addWidget(self.cornerLabel,1,1,Qt.AlignBottom|Qt.AlignRight)

    def SignalConnect_init(self):
        global_ms.new_comment.connect(self.addComment)
        global_ms.sizeChange.connect(self.modifySize)
        global_ms.fontChange.connect(self.modifyFont)
        global_ms.otherChange.connect(self.modifyOther)

    def addComment(self,bool,msg):
        '''
        这里必须在主线程里添加，否则显示会延迟，但消息多时可能会导致窗口无响应。
        装在列表里for循坏也不行，目前还没找到更好的方法
        '''
        if bool:
            # 设置发送者id样式
            self.FontFormat.setForeground(self.Userfont)
            self.textEdit.mergeCurrentCharFormat(self.FontFormat)
            self.textEdit.appendPlainText("".join(msg.split(': ')[0]) + ": ")
            # 设置弹幕内容样式
            self.FontFormat.setForeground(self.Comfont)
            self.textEdit.mergeCurrentCharFormat(self.FontFormat)
            self.tc.movePosition(QTextCursor.End)
            self.textEdit.insertPlainText("".join(msg.split(': ')[1]))
            # 刷新,可有可无
            QApplication.processEvents()

    def modifySize(self,type,value):
        '''多线程减轻主线程压力，防止窗口无响应'''
        def aa():
            try:
                if type == 'charactersSize':
                    self.textEdit.setStyleSheet(
                        f"font-size:{value}px;font-weight:bold;border: none; background-color: transparent;")
                    logger.info('修改 文字大小 成功')
                elif type == 'lineNum':
                    self.textEdit.setMaximumBlockCount(value)
                    logger.info('修改 行数 成功')
                elif type == 'lineHeight':
                    self.BlockFormat.setLineHeight(value, QTextBlockFormat.FixedHeight)
                    self.tc.setBlockFormat(self.BlockFormat)
                    self.textEdit.setTextCursor(self.tc)
                    logger.info('修改 行高 成功')
            except Exception as e:
                logger.error(u'修改参数失败：{}'.format(e))
        threading.Thread(target=aa).start()

    def modifyOther(self,type,value):
        def aa():
            try:
                if type == 'userColor':
                    self.Userfont = QColor(value)
                    logger.info('修改 发送者id颜色 成功')
                elif type == 'comColor':
                    self.Comfont = QColor(value)
                    logger.info('修改 弹幕内容颜色 成功')
                elif type == 'background':
                    pix = QPixmap(value)
                    self.backLabel.setPixmap(pix)
                    logger.info('修改 背景图片 成功')
            except Exception as e:
                logger.error(u'修改参数失败：{}'.format(e))
        threading.Thread(target=aa).start()

    def modifyFont(self,font):
        def aa():
            try:
                self.textEdit.setFont(font)
                logger.info('修改 文字字体 成功')
            except Exception as e:
                logger.error(u'修改参数失败：{}'.format(e))
        threading.Thread(target=aa).start()

    def clearWindow(self):
        self.textEdit.clear()

    # ----------------------无边框鼠标拖动及改变窗口大小---------------------
    def _initDrag(self):
        # 设置鼠标跟踪判断扳机默认值
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False
        # 判断鼠标位置切换鼠标手势
        self.cornerLabel.setCursor(Qt.SizeFDiagCursor)
        self.bottomLabel.setCursor(Qt.SizeVerCursor)
        self.rightLabel.setCursor(Qt.SizeHorCursor)

    def eventFilter(self, obj, event):
        # 事件过滤器,用于解决鼠标进入其它控件后还原为标准鼠标样式
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super(DisplayWindow, self).eventFilter(obj, event)  # 注意 ,MyWindow是所在类的名称
        # return QWidget.eventFilter(self, obj, event)  # 用这个也行，但要注意修改窗口类型

    def resizeEvent(self, QResizeEvent):
        # 自定义窗口调整大小事件
        # 改变窗口大小的三个坐标范围
        ran = 30
        self._right_rect = [QPoint(x, y) for x in range(self.width() - ran, self.width() )
                            for y in range(1, self.height()-ran)]
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - ran)
                             for y in range(self.height() - ran, self.height())]
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - ran, self.width() )
                             for y in range(self.height() - ran, self.height() )]

    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if (event.button() == Qt.LeftButton) and (event.pos() in self._corner_rect):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._right_rect):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._bottom_rect):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.y() < self.height()-30):
            # 鼠标左键点击其他位置
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        # 当鼠标左键点击不放及满足点击区域的要求后，分别实现不同的窗口调整
        # 没有定义左方和上方相关的5个方向，主要是因为实现起来不难，但是效果很差，拖放的时候窗口闪烁，再研究研究是否有更好的实现
        if Qt.LeftButton and self._right_drag:
            # 右侧调整窗口宽度
            self.resize(QMouseEvent.pos().x(), self.height())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(QMouseEvent.pos().x(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._move_drag:
            # 其他位置拖放窗口位置
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标释放后，各扳机复位
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False