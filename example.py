# -*— coding:utf-8 -*-

from reconnectWebsocketClient import ReconnectWebsocketClient
from datetime import datetime

def on_message(ws, message):
    print(datetime.now(),"on_message:",message)

def on_error(ws, error):
    print(datetime.now(),"on_error",error)

def on_close(ws):
    print(datetime.now(),"on_close")

def on_open(ws):
    ws.send("Hello World")
    print(datetime.now(),"on_open")




if __name__ == "__main__":
    import websocket
    websocket.enableTrace(True)  # 打印额外信息，属调试功能

    # url = "ws://echo.websocket.org/"

    # 本地并没有这样一个websocket服务器，所以会连接不上，然后会尝试重连
    url = "ws://localhost:8001/"
    ws = ReconnectWebsocketClient(url,
                         on_open=on_open,
                         on_message=on_message,
                         on_error=on_error,
                         on_close=on_close)
    # 重连5次，若为负数，则无限次尝试重连
    ws.setReconnectTimes(5)
    # ws.setReconnectTimes(-1)

    # 每次重连时间间隔为10s
    ws.setReconnectIntervalTime(10)

    # 启动连接并run_forever()
    ws.run()

