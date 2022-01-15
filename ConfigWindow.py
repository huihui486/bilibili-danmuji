from preparation import *


class ConfigWindow(QWidget):
    def __init__(self, parent=None):
        super(ConfigWindow, self).__init__(parent)
        loadUi('ui/ConfigWindow.ui', self)
        # 标题、图标
        self.setWindowTitle('设置')
        self.setWindowIcon(QIcon(iconPath))
        # 值
        self.size = initsize
        self.linenum = initlinenum
        self.lineheight = initlineheight
        self.usercolor = initusercolor
        self.comcolor = initcomcolor
        self.font = '宋体'
        self.background = initbackground
        # 初始化
        self.Ui_init()
        self.buttonConncet()

    def buttonConncet(self):
        # 关键词TAB页按钮
        self.insertButton1.clicked.connect(lambda: self.InsertListElement('用户id',self.listWidget1,whiteUser))
        self.delButton1.clicked.connect(lambda: self.DelListElement(self.listWidget1,whiteUser))
        self.insertButton2.clicked.connect(lambda: self.InsertListElement('用户id',self.listWidget2,blackUser))
        self.delButton2.clicked.connect(lambda: self.DelListElement(self.listWidget2,blackUser))
        self.insertButton3.clicked.connect(lambda: self.InsertListElement('筛选关键词',self.listWidget3,keywords))
        self.delButton3.clicked.connect(lambda: self.DelListElement(self.listWidget3,keywords))
        self.insertButton4.clicked.connect(lambda: self.InsertListElement('屏蔽关键词',self.listWidget4,filterKWs))
        self.delButton4.clicked.connect(lambda: self.DelListElement(self.listWidget4,filterKWs))
        # 菜单栏按钮
        self.importButton.clicked.connect(self.GetOpenXlsxPath)
        self.deriveButton.clicked.connect(self.GetSaveXlsxPath)
        self.clearButton.clicked.connect(self.clearAllSetting)

    def Ui_init(self):
        # TAB页标题
        self.tabWidget.setTabText(0,'只看TA')
        self.tabWidget.setTabText(1,'不看TA')
        self.tabWidget.setTabText(2,'筛选关键词')
        self.tabWidget.setTabText(3,'屏蔽关键词')
        # 发送者id颜色
        self.userColorView.setText(initusercolor)
        self.userColorButton.clicked.connect(self.getUserColor)
        self.userColorView.textChanged.connect(self.UserColorChange)
        # 弹幕内容颜色
        self.comColorView.setText(initcomcolor)
        self.comColorButton.clicked.connect(self.getComColor)
        self.comColorView.textChanged.connect(self.ComColorChange)
        # 字体大小
        self.charactersSize.setValue(initsize)
        self.charactersSize.valueChanged.connect(self.getSize)
        # 显示行数
        self.LineNumber.setValue(initlinenum)
        self.LineNumber.valueChanged.connect(self.getLineNum)
        # 行高
        self.LineHeight.setValue(initlineheight)
        self.LineHeight.valueChanged.connect(self.getLineHeight)
        # 字体样式
        self.fontComboBox.currentFontChanged.connect(self.fontChange)
        self.fontComboBox.addItems(['所有字体', '可缩放字体', '不可缩放字体', '等宽字体', '等比例字体'])
        # 背景图片
        self.backgroundView.setText(initbackground)
        self.backgroundButton.clicked.connect(self.getBackgroundPath)
        self.backgroundView.textChanged.connect(self.BackgroundChange)
        # 判断是否存在配置文件，若存在直接导入
        if os.path.exists(settingPath):
            print('存在文件')
            self.ImportXlsx()
        else:
            print('不存在文件，请手动导入')

    def getBackgroundPath(self):
        filePath, _ = QFileDialog.getOpenFileName(
            self,  # 父窗口对象
            "选择文件",  # 标题
            os.getcwd() + '\\config',  # 起始目录
            "图片类型 (*.jpg *.jpeg *.png *bmp *tif *gif)"  # 选择类型过滤项，过滤内容在括号中
        )
        if filePath != '':
            self.backgroundView.setText(filePath)

    def BackgroundChange(self,filePath):
        self.background = filePath
        global_ms.otherChange.emit('background',filePath)


    def fontChange(self,font):
        self.font = font.key().split(',')[0]   # 提取出Qfont中的字体样式
        font.setPointSize(self.size)
        global_ms.fontChange.emit(font)

    def getSize(self,size):
        self.size = size
        global_ms.sizeChange.emit('charactersSize',self.size)

    def getLineNum(self,linenum):
        self.linenum = linenum
        global_ms.sizeChange.emit('lineNum',self.linenum)

    def getLineHeight(self,lineheight):
        self.lineheight = lineheight
        global_ms.sizeChange.emit('lineHeight',self.lineheight)

    def getUserColor(self):
        c = QColorDialog.getColor()
        colorName = c.name()
        # getColor对话框点击取消时会返回缺省值#000000
        # 为避免这种情况直接ban掉#000000，未找到更好方案
        if colorName != '#000000':
            # print(colorName)
            self.userColorView.setText(colorName)
        else:
            msg_box = QMessageBox(QMessageBox.Warning, '提示', '#000000禁止设置，黑色请尝试#000001等')
            msg_box.exec_()

    def UserColorChange(self,colorName):
        self.usercolor = colorName
        global_ms.otherChange.emit('userColor',colorName)

    def getComColor(self):
        c = QColorDialog.getColor()
        colorName = c.name()
        if colorName != '#000000':
            # print(colorName)
            self.comColorView.setText(colorName)
        else:
            msg_box = QMessageBox(QMessageBox.Warning, '提示', '#000000禁止设置，黑色请尝试#000001等')
            msg_box.exec_()

    def ComColorChange(self,colorName):
        self.comcolor = colorName
        global_ms.otherChange.emit('comColor',colorName)

    def InsertListElement(self,text,listWidget,List):
        try:
            content, okPressed = QInputDialog.getText(
                self,   # 父窗口
                "请输入",  # 标题
                f"{text}:", # 提示文本
                QLineEdit.Normal,   # 单行输入框
                "")
            if okPressed and content != '':
                content = content.strip()
                # print(content)
                listWidget.addItem(content)
                if content not in List:
                    List.append(content)
        except Exception as e:
            logger.error(u'增加项目错误：{}'.format(e))
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '增加项目错误')
            msg_box.exec_()

    def DelListElement(self,listWidget,List):
        try:
            item = listWidget.currentItem()
            if item != None:
                listWidget.takeItem(listWidget.row(item))
                if item.text() in List:
                    List.remove(item.text())
        except Exception as e:
            logger.error(u'删除项目错误：{}'.format(e))
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '删除项目错误')
            msg_box.exec_()

    def clearAllSetting(self):
        try:
            # 清空TAB页内容和列表
            for ListWidget,List in zip([self.listWidget1,self.listWidget2,self.listWidget3,self.listWidget4],[whiteUser,blackUser,keywords,filterKWs]):
                ListWidget.clear()
                List.clear()
            # 清各种参数
            self.userColorView.setText(initusercolor)
            self.comColorView.setText(initcomcolor)
            self.charactersSize.setValue(initsize)
            self.LineNumber.setValue(initlinenum)
            self.LineHeight.setValue(initlineheight)
            self.fontComboBox.setCurrentFont(QFont(initfont))
            self.backgroundView.setText(initbackground)
        except Exception as e:
            logger.error(u'清空/还原错误：{}'.format(e))
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '清空/还原错误')
            msg_box.exec_()

    def GetOpenXlsxPath(self):
        logger.info('***尝试导入')
        if os.path.exists(settingPath):
            self.ImportXlsx()
        else:
            logger.warning('***文件不存在')
            msg_box = QMessageBox(QMessageBox.Warning, '提示', f'{settingPath}不存在！请先导出配置')
            msg_box.exec_()

    def GetSaveXlsxPath(self):
        logger.info('***尝试导出')
        self.SaveXlsx()

    def ImportXlsx(self):
        # 从文件中读取参数
        try:
            self.listWidget1.clear()
            self.listWidget2.clear()
            self.listWidget3.clear()
            self.listWidget4.clear()
            # 只读模式下读取速度更快，但没有columns这个属性
            wb = openpyxl.load_workbook(settingPath)
            ws = wb.active
            for column in ws.columns:
                if column[0].value == 'white':
                    self.ImportAdd(column,self.listWidget1,whiteUser)
                elif column[0].value == 'black':
                    self.ImportAdd(column,self.listWidget2,blackUser)
                elif column[0].value == 'kw':
                    self.ImportAdd(column,self.listWidget3,keywords)
                elif column[0].value == 'filterKW':
                    self.ImportAdd(column,self.listWidget4,filterKWs)
                elif column[0].value == 'size':
                    self.charactersSize.setValue(column[1].value)
                    self.LineNumber.setValue(column[2].value)
                    self.LineHeight.setValue(column[3].value)
                elif column[0].value == 'color':
                    self.userColorView.setText(column[1].value)
                    self.comColorView.setText(column[2].value)
                elif column[0].value == 'font':
                    self.fontComboBox.setCurrentFont(QFont(column[1].value))
                elif column[0].value == 'background':
                    filePath = column[1].value
                    if filePath != None and os.path.exists(filePath):
                        self.backgroundView.setText(filePath)
                    else:
                        logger.warning('图片修改失败。原因：图片不存在')
                        msg_box = QMessageBox(QMessageBox.Warning, '提示', '图片修改失败。原因：图片不存在')
                        msg_box.exec_()
                else:
                    continue
            logger.info('***导入成功')
            msg_box = QMessageBox(QMessageBox.Warning, '提示', f'导入成功： {settingPath}')
            msg_box.exec_()
        except Exception as e:
            logger.error(u'***导入时出现异常：{}'.format(e))
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '导入时出现异常')
            msg_box.exec_()

    def ImportAdd(self,column,listWidget,List):
        for cell in column[1:]:
            value = str(cell.value)
            if value != 'None':
                listWidget.addItem(value)
                List.append(value)

    def SaveXlsx(self):
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(['white', 'black', 'kw','filterKW','size','color','font','background'])
            for a,b,c,d in itertools.zip_longest(whiteUser,blackUser,keywords,filterKWs):
                ws.append([a, b, c, d])
            ws['E2'],ws['E3'],ws['E4'],ws['F2'],ws['F3'],ws['G2'],ws['H2'] = \
                self.size,self.linenum,self.lineheight,self.usercolor,self.comcolor,self.font,self.background
            wb.save(settingPath)
            logger.info('***导出成功')
            msg_box = QMessageBox(QMessageBox.Information, '提示', f'导出成功！保存路径：{settingPath}')
            msg_box.exec_()
        except PermissionError as e:
            print('请先关闭文件')
            logger.warning('***文件未关闭')
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '请先关闭文件')
            msg_box.exec_()
        except Exception as e:
            logger.error(u'***导入时出现异常：{}'.format(e))
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '导出时出现异常')
            msg_box.exec_()

    def closeEvent(self, event):
        '''关闭子窗口时发送信号给主窗口'''
        global_ms.my_Signal.emit('closeWin')