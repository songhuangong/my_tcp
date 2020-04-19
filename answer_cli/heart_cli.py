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


class HeartCli:
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
        events = selectors.EVENT_WRITE
        self.message = libclient.Message(self.sel, sock, addr, request)
        self.sel.register(sock, events, data=self.message)

    def send_heart(self, request):
        self.start_connection(self.host, self.port, request)
        try:
            while True:
                events = self.sel.select(timeout=1)
                for key, mask in events:
                    self.message = key.data
                    try:
                        self.message.write_without_reply()
                    except Exception:
                        print(
                            "main: error: exception for",
                            f"{self.message.addr}:\n{traceback.format_exc()}",
                        )
                        self.message.close()
                        return False
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    # result_info = self.message.response
                    break
        except OSError:
            return False
        except Exception as e:
            return False
            print(f"未知错误：f{e} --> {type(e)}")
        finally:
            self.sel.close()
        return True


if __name__ == '__main__':
    request = create_request('heart', "")
    cli = HeartCli()
    r = cli.send_heart(request)
    print('发送是否成功：', r)