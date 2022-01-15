
from getWebsocket import *
from MainWindow import *
from ConfigWindow import *
from DisplayWindow import *
from AboutInfo import *
from TUOPAN import *


class BiliDanmuji():
    def __init__(self):
        # 主要对象
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # 最小化托盘用,关闭所有窗口也不结束程序
        self.scan() # 扫描文件夹，若不存在报错
        self.w = MainWindow()   # 主窗口
        self.settingWindow = ConfigWindow() # 设置窗口
        self.display = DisplayWindow()  # 弹幕展示窗口
        self.about = AboutInfo()  # 关于窗口
        self.tuopan = TUOPAN()  # 托盘对象
        # 爬虫对象
        self.bilisocket = BiliSocket()
        # 开始运行、弹幕窗口隐藏标志
        self.startFlag = False
        self.isHide = True
        # 接受子窗口传回来的信号  然后调用主界面的函数
        global_ms.my_Signal.connect(self.SignalHandle)
        # 写日志
        logger.info('----------------------初始化成功-----------------------')

    def run(self):
        try:
            # 显示主窗口，开始处理窗口事件
            self.w.show()
            sys.exit(self.app.exec_())
        except:
            logger.critical('**********************程序异常退出************************')

    def scan(self):
        if not os.path.exists('ui') or not os.path.exists('config'):
            logger.critical('未找到ui/config文件夹')
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '未找到ui/config文件夹')
            msg_box.exec_()
            sys.exit(0)
        elif not os.path.exists('config/background_70.png') or not os.path.exists('config/icon.jpg'):
            logger.critical('config文件夹中未找到配置文件')
            msg_box = QMessageBox(QMessageBox.Warning, '警告', 'config文件夹中未找到配置文件')
            msg_box.exec_()
            sys.exit(0)

    def close_com(self):
        if self.startFlag == True:
            self.display.hide()
            self.isHide = True
            try:
                logger.info('///尝试关闭循环')
                self.bilisocket.close()
                # 等待抛出异常，抛出后线程自动结束
                time.sleep(0.3)
                logger.info(f'loop状态：{self.loop.is_running()}，{self.loop.is_closed()} / '
                            f'SocketTread状态：{self.SocketTread.is_alive()}')
                logger.info('///循环关闭成功')
            except NotImplementedError as e:
                logger.error(u'///关闭循环出错：{}'.format(e))


    def start_run(self):
        try:
            # 获取房间号
            text = self.w.roomidEdit.text()
            if text != '' and text.isdigit():
                if self.startFlag == False:
                    self.startFlag = True
                else:
                    print(self.SocketTread.is_alive())
                    if self.SocketTread.is_alive():
                        self.close_com()
                    self.display.clearWindow()
                    self.bilisocket.comList.clear()
                self.display.show()
                self.isHide = False
                loop = asyncio.new_event_loop()
                self.SocketTread = threading.Thread(target=self.asyncTreadfun, args=(loop, text),
                                                    name='SocketTread')
                self.SocketTread.daemon = True  # 守护线程
                self.SocketTread.start()
                logger.info(f'开启/更新成功，当前房间：{text}')
            else:
                self.startFlag = False
                logger.info('输入房间号有误')
                msg_box = QMessageBox(QMessageBox.Warning, '提示', '请输入正确房间号')
                msg_box.exec_()
        except Exception as e:
            self.startFlag = False
            self.isHide = True
            logger.error(u'开启/更新出错：{}'.format(e))


    def asyncTreadfun(self,new_loop,roomid):
        try:
            asyncio.set_event_loop(new_loop)
            self.loop = asyncio.get_event_loop()
            task = asyncio.ensure_future(self.bilisocket.startup(roomid))
            self.loop.run_until_complete(asyncio.wait([task]))
        except RuntimeError as e:
            logger.warning(u'loop循环未完成退出（若是关闭时为正常现象）。错误信息：{}'.format(e))

    def SignalHandle(self,value):
        if value == 'closeWin':
            print('子窗口被关闭')
        elif value == 'MainWindow':
            self.w.show()
        elif value == 'start':
            self.start_run()
        elif value == 'close':
            self.close_com()
        elif value == 'setting':
            self.settingWindow.show()
        elif value == 'about':
            self.about.show()
        elif value == 'WebSocketError':
            self.close_com()
            msg_box = QMessageBox(QMessageBox.Warning, '警告', '获取弹幕失败')
            msg_box.exec_()
        elif value == 'exit':
            self.quitApp()


    def quitApp(self):
        print('托盘关闭')
        if self.isHide == False:
            self.close_com()
        # 关闭窗体程序
        QCoreApplication.instance().quit()
        self.tuopan.tp.setVisible(False)
        logger.info('----------------------程序正常退出-----------------------')
        sys.exit(0)


if __name__ == '__main__':
    danmuji = BiliDanmuji()
    danmuji.run()
