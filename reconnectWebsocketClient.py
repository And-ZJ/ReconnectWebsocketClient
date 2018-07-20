import websocket
import threading

class ReconnectWebsocketClient(websocket.WebSocketApp):

    def __init__(self, *args, **kwargs):
        self.__user_on_open = kwargs.get("on_open", None)
        self.__user_on_message = kwargs.get("on_message", None)
        self.__user_on_error = kwargs.get("on_error",None)
        self.__user_on_close = kwargs.get("on_close", None)
        kwargs["on_open"] = self.__on_open
        kwargs["on_message"] = self.__on_message
        kwargs["on_error"] = self.__on_error
        kwargs["on_close"] = self.__on_close
        ## 将代码注册相关函数上，以实现重连功能
        super(ReconnectWebsocketClient, self).__init__(*args, **kwargs)
        # 默认重连次数5次，断线后重连间隔5s
        self.setReconnectIntervalTime(5)
        self.setReconnectTimes(5)
        self.__timer = None

    def setReconnectTimes(self, reconnectTimes):
        """
            reconnectTimes > 0, 最大重连尝试次数为 reconnectTimes
            reconnectTimes == 0，不重连
            reconnectTimes < 0, 不限制重连次数（可永久尝试重连）
            当连接成功时，此值会重置
        :param reconnectTimes: 设置最大重连次数
        :return: None
        """
        self.__remainReconnectTimes = reconnectTimes
        self.reconnectTimes = reconnectTimes

    def getReconnectTimes(self):
        """
            返回设置的重连次数
        :return: int
        """
        return self.reconnectTimes

    def getRemainReconnectTimes(self):
        """
            返回剩余的重连次数（当连接成功之后，此值会重置为设置的重连次数）
        :return: int
        """
        return self.__remainReconnectTimes

    def setReconnectIntervalTime(self, reconnectIntervalTime):
        """
            当on_close被触发之后，间隔多久开始进行重连操作
            注意，如果掉线了，可能会有1分多钟的超时时长才会提示掉线了（on_error被调用）
        :param reconnectIntervalTime: 每次重连时的间隔时间，单位 seconds
        :return: None
        """
        self.reconnectIntervalTime = reconnectIntervalTime

    def __reconnect(self):
        """
            进行重连操作
        :return: None
        """
        if self.reconnectTimes < 0:
            # 如果设置的是负数，则无限次尝试重连
            self.run()
        elif self.__remainReconnectTimes > 0:
            self.__remainReconnectTimes = self.__remainReconnectTimes - 1
            self.run() # 进行重连
        else:
            exit(0)

    def __on_open(self,ws):
        """
            on_open，被调用
        :param ws: 自动传递
        :return: None
        """
        if self.__user_on_open is not None:
            # 调用用户设置的on_open
            self.__user_on_open(ws)
        # 连接成功，重置重连次数
        self.setReconnectTimes(self.reconnectTimes)

    def __on_message(self,ws,message):
        """
            on_message，被调用
        :param ws: 自动传递
        :return: None
        """
        if self.__user_on_message is not None:
            self.__user_on_message(ws,message)

    def __on_error(self,ws,error):
        """
            on_error，被调用
        :param ws: 自动传递
        :param error:  自动传递，异常对象（Exception）
        :return: None
        """
        if self.__user_on_error is not None:
            self.__user_on_error(ws,error)
        if isinstance(error, KeyboardInterrupt):
            # print("Ctrl-C Detected.Exit!")
            exit(-1)

    def __on_close(self, ws):
        """
            on_close，被调用，在这里实现断开重连
        :param ws: 自动传递
        :return: None
        """
        if self.__user_on_close is not None:
            self.__user_on_close(ws)
        if self.reconnectTimes == 0:
            return
        # 设置定时器
        if self.__timer is not None:
            self.__timer.cancel()
        self.__timer = threading.Timer(self.reconnectIntervalTime, self.__reconnect)
        self.__timer.start()

    def run(self):
        """
            run_forever()
        :return: None
        """
        try:
            self.run_forever()
        except KeyboardInterrupt as e:
            # print("Ctrl-C Detected.Exit!")
            exit(-1)
        except Exception as e:
            # 防止此处报错导致程序退出
            pass