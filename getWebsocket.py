from preparation import *




class BiliSocket():
    def __init__(self):
        # 入口链接地址
        self.remote = 'ws://broadcastlv.chat.bilibili.com:2244/sub'
        # 21733344
        self.roomid = '21733344'
        # 查询真实房间号的api
        self.realRoomidUrl = 'https://api.live.bilibili.com/room/v1/Room/room_init?id='
        # heartbeat包及发送间隔
        self.heartbeat ='00 00 00 10 00 10 00 01  00 00 00 02 00 00 00 01'
        self.heartbeatInterval = 30
        # 关闭标志位
        self.__closeFlag = False
        # 允许显示标志
        self.allowFlag = False
        # header
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        }

    async def startup(self,roomid):
        '''
        首先请求api将用户输入的房间号转为真实房间号
        然后创建异步任务，一个负责发送HeartBeat包，另一个负责接收消息
        :param roomid: 用户输入的房间号
        '''
        self.__closeFlag = False
        self.roomid = self.getRealRoomid(self.realRoomidUrl + str(roomid))
        logger.info(f'获取真实房间号成功： {self.roomid}')
        self.data_raw = '000000{headerLen}0010000100000007000000017b22726f6f6d6964223a{roomid}7d'
        self.data_raw = self.data_raw.format(headerLen=hex(27 + len(self.roomid))[2:],
                                             roomid=''.join(map(lambda x: hex(ord(x))[2:], list(self.roomid))))

        async with AioWebSocket(self.remote) as aws:
            converse = aws.manipulator
            await converse.send(bytes.fromhex(self.data_raw))
            tasks = [self.receDM(converse), self.sendHeartBeat(converse),self.check2close()]
            await asyncio.wait(tasks)

    def getRealRoomid(self,url):
        try:
            res = requests.get(url,headers=self.headers)
            if res.status_code == 200:
                room_json = json.loads(res.text)
                room_id = room_json['data']['room_id']
                return str(room_id)
            else:
                raise Exception('请求真实房间号出错')
        except Exception as e:
            global_ms.my_Signal.emit('WebSocketError')
            logger.error(u'请求真实房间号出错：{}'.format(e))

    async def check2close(self):
        '''
        循环判断关闭标志位closeFlag是否为真
        若为真则抛出异常来结束该子线程
        一定要设置休眠否则占据资源导致卡死
        '''
        while True:
            await asyncio.sleep(0.2)
            if self.__closeFlag == True:
                raise KeyboardInterrupt

    def close(self):
        '''通过设置标志位来结束线程'''
        self.__closeFlag = True

    async def sendHeartBeat(self, websocket):
        logger.info('创建 sendHeartBeat 任务成功')
        while True:
            try:
                # 每隔一段时间向服务端发送heartbeat包防止断开连接
                await asyncio.sleep(self.heartbeatInterval)
                await websocket.send(bytes.fromhex(self.heartbeat))
                print('[Notice] Sent HeartBeat.')
            except Exception as e:
                global_ms.my_Signal.emit('WebSocketError')
                logger.error(u'发送heartbeat包失败：{}'.format(e))




    async def receDM(self, websocket):
        logger.info('创建 receDM 任务成功')
        while True:
            try:
                # 接收消息
                recv_text = await websocket.receive()
                # 这里必须加上这个if，否则不能持续输出弹幕。未解之谜
                if recv_text == None:
                    recv_text = b'\x00\x00\x00\x1a\x00\x10\x00\x01\x00\x00\x00\x08\x00\x00\x00\x01{"code":0}'
                # 接收到消息的处理
                self.printDM(recv_text)
            except Exception as e:
                global_ms.my_Signal.emit('WebSocketError')
                logger.error(u'receDM函数出错：{}'.format(e))


    # 将数据包传入：
    def printDM(self, data):
        # 获取数据包的长度，版本和操作类型
        packetLen = int(data[:4].hex(), 16)
        ver = int(data[6:8].hex(), 16)
        op = int(data[8:12].hex(), 16)

        # 有的时候可能会两个数据包连在一起发过来，所以利用前面的数据包长度判断，
        if (len(data) > packetLen):
            self.printDM(data[packetLen:])
            data = data[:packetLen]

        # 有时会发送过来 zlib 压缩的数据包，这个时候要去解压。
        if (ver == 2):
            data = zlib.decompress(data[16:])
            self.printDM(data)
            return


        # ver 不为2也不为1目前就只能是0了，也就是普通的 json 数据。
        # op 为5意味着这是通知消息，cmd 基本就那几个了。
        if (op == 5):
            jd = json.loads(data[16:].decode('utf-8', errors='ignore'))
            if (jd['cmd'] == 'DANMU_MSG'):
                self.DANMU_handle(jd['info'])
            elif (jd['cmd'] == 'LIVE'):
                global_ms.new_comment.emit(True, '[Notice]: LIVE Start!')
            elif (jd['cmd'] == 'PREPARING'):
                global_ms.new_comment.emit(True, '[Notice]: LIVE Ended!')

    def DANMU_handle(self,data):
        '''
        弹幕的处理，包括对用户输入的关键词进行筛选，及筛选后将弹幕传到展示窗口
        这种方法的缺点：信号传值的方法会有延迟，并且在消息很多的时候会吞掉几条
        另一种方法：定义一个列表，将新消息添加到列表，并创建一个刷新线程来不断取列表中的新弹幕
        '''
        try:
            fromUser = data[2][1]
            text = data[1]
            msg = fromUser + ': ' + text
            self.allowFlag = False
            if blackUser != []:
                if fromUser in blackUser:
                    return
            for i in filterKWs:
                if i in text:
                    return
            if whiteUser == [] and keywords == []:
                self.allowFlag = True
            elif whiteUser == [] and keywords != []:
                for i in keywords:
                    if i in text:
                        self.allowFlag = True
                        break
            elif whiteUser != [] and keywords == []:
                if fromUser in whiteUser:
                    self.allowFlag = True
            else:
                if fromUser in whiteUser:
                    for i in keywords:
                        if i in text:
                            self.allowFlag = True

            if self.allowFlag == True:
                global_ms.new_comment.emit(True,msg)
                self.allowFlag = False
        except Exception as e:
            global_ms.my_Signal.emit('WebSocketError')
            logger.error(u'弹幕筛选处理出错：{}'.format(e))






if __name__ == '__main__':
    try:
        roomid = 33989
        asyncio.get_event_loop().run_until_complete(BiliSocket().startup(roomid))
    except KeyboardInterrupt as exc:
        print('Quit.')
