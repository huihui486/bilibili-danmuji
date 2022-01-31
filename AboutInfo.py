from preparation import *
import os.path


class AboutInfo():
    def __init__(self):
        self.path = os.path.join("config", "关于.txt")
        self.info = '# 声明：\n'\
                    '此软件只做学习交流，禁止商用\n\n'\
                    '# 项目/资料地址：\n'\
                    'B站（https://www.bilibili.com/video/BV1LP4y177sa）\n'\
                    'gitee（https://gitee.com/huihui486/bilibili-danmuji）\n'\
                    'github（https://github.com/huihui486/bilibili-danmuji）\n'\
                    'CSDN（https://blog.csdn.net/Sharp486/article/details/122516917）\n\n'\
                    '# 开发人员信息：\n'\
                    'B站：@了不起的灰灰（https://space.bilibili.com/12910396）\n'\
                    'gitee：@huihui486（https://gitee.com/huihui486）\n'\
                    'github：@huihui486（https://github.com/huihui486）\n'\
                    'CSDN：@Sharp486（https://blog.csdn.net/Sharp486）'
        self.__addInfo()

    def __addInfo(self):
        if not os.path.exists(self.path):
            with open(self.path,'w') as f:
                f.write(self.info)

    def show(self):
        self.__addInfo()
        os.startfile(self.path)

