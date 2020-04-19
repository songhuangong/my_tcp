#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

import libclient


def create_request(action, value):
    return dict(
        type="text/json",
        encoding="utf-8",
        content=dict(action=action, value=value),
    )


class AskCli:
    def __init__(self):
        self.sel = selectors.DefaultSelector()
        self.message = None
        self.host = '127.0.0.1'
        self.port = 8000

    def start_connection(self, host, port, request):
        addr = (host, port)
        print("starting connection to", addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.message = libclient.Message(self.sel, sock, addr, request)
        self.sel.register(sock, events, data=self.message)

    def ask(self, request):
        self.start_connection(self.host, self.port, request)
        # 询问返回的结果
        result_info = None
        try:
            while True:
                events = self.sel.select(timeout=1)
                for key, mask in events:
                    self.message = key.data
                    try:
                        self.message.process_events(mask)
                    except Exception:
                        print(
                            "main: error: exception for",
                            f"{self.message.addr}:\n{traceback.format_exc()}",
                        )
                        self.message.close()
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    result_info = self.message.response
                    break
        except Exception as e:
            print(f"未知错误：f{e} --> {type(e)}")
        finally:
            # 保持长链接先不能关闭！
            # self.sel.close()
            pass
        return result_info


if __name__ == '__main__':
    request = create_request('cmd', "123")

    ask_cli = AskCli()
    r = ask_cli.ask(request)
    print('获取结果：', r)