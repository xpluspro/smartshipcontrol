#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import base64
import hashlib
import socket

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
sys.path.append("..")

sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# 绑定host, 默认端口5000
sock.bind(("192.168.1.161", 9900))
sock.listen(5)


def get_headers(data):
    """
    将请求头转换为字典
    :param data: 解析请求头的data
    :return: 请求头字典
    """
    header_dict = {}
    data = str(data, encoding="utf-8")
    header, body = data.split("\r\n\r\n", 1)  # 因为请求头信息结尾都是\r\n,并且最后末尾部分是\r\n\r\n; 所以以此分割
    header_list = header.split("\r\n")
    for i in range(0, len(header_list)):
        if i == 0:
            if len(header_list[0].split(" ")) == 3:
                header_dict['method'], header_dict['url'], header_dict['protocol'] = header_list[0].split(" ")
        else:
            k, v = header_list[i].split(":", 1)
            header_dict[k] = v.strip()
    return header_dict


def decode_info(info):
    """
    对返回消息进行解码
    :param info: 原始消息
    :return: 解码之后的汉字
    """
    if len(info) < 1:
        return "no data"
    payload_len = info[1] & 127
    if payload_len == 126:
        extend_payload_len = info[2:4]
        mask = info[4:8]
        decoded = info[8:]
    elif payload_len == 127:
        extend_payload_len = info[2:10]
        mask = info[10:14]
        decoded = info[14:]
    else:
        extend_payload_len = None
        mask = info[2:6]
        decoded = info[6:]
    bytes_list = bytearray()  # 使用字节将数据全部收集，再去字符串编码，这样不会导致中文乱码
    for i in range(len(decoded)):
        chunk = decoded[i] ^ mask[i % 4]  # 解码方式
        bytes_list.append(chunk)
    body = str(bytes_list, encoding='utf-8')
    return body


# 等待用户连接
conn, addr = sock.accept()
print("conn from==>", conn, addr)
# 获取握手消息, magic string,sha1加密
# 发送给客户端
# 握手消息
data = conn.recv(8096)
headers = get_headers(data)

# 对请求头中的sec - websocket - key进行加密
response_tpl = "HTTP/1.1 101 Switching Protocols\r\n" \
               "Upgrade:websocket\r\n" \
               "Connection: Upgrade\r\n" \
               "Sec-WebSocket-Accept: %s\r\n" \
               "WebSocket-Location: ws://%s%s\r\n\r\n"

magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
# 确认握手Sec - WebSocket - Key固定格式: headers头部的Sec - WebSocket - Key+'258EAFA5-E914-47DA-95CA-C5AB0DC85
value = headers['Sec-WebSocket-Key'] + magic_string
ac = base64.b64encode(hashlib.sha1(value.encode('utf-8')).digest())
response_str = response_tpl % (ac.decode('utf-8'), headers['Host'], headers['url'])

# 响应【握手】信息
conn.send(bytes(response_str, encoding='utf-8'))

# 可以进行通信-接收客户端发送的消息
while True:
    data = conn.recv(8096)
    data = decode_info(data)
    print("Receive msg==>", data)
    if data == "no data":
        conn.close()