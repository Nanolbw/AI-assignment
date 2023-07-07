# -*- coding: utf-8 -*-
# @Time    : 2023/5/15 9:18
# @Author  : HanYanze
# @Description : 串口收发
import serial # 串口通信库
import threading # 线程库
import crcmod.predefined # CRC校验库
from queue import Queue # 消息队列库
import serial.tools.list_ports # 列出可用串口设备的模块

print("导入serial库...")


class CRCGenerator:
    """
    CRC校验的类
    """

    def __init__(self):
        self.module = 'crc-8'

    def crc_8(self, hexData):
        # 定义使用crc-8的方式进行校验
        crc8 = crcmod.predefined.Crc('crc-8')
        hexData = bytes.fromhex(hexData)  # 使用 bytes.fromhex()
        # 进行crc-8的计算
        crc8.update(hexData)
        result = hex(crc8.crcValue)[2:]  # 直接使用字符串切片去除开头的 "0x"
        return result.zfill(2)  # 使用 str.zfill() 补齐结果至两位数


class MySerial:
    """
    串口类 MySerial，包含了一些串口操作的方法和属性。
    """

    def __init__(self):
        self.recdata = ""  # 接收到的数据
        self.crc_send = True  # 是否对发送的数据进行校验
        self.crc_recv = True  # 是否对接收到的数据进行校验
        self.recvmsg = Queue(maxsize=1)  # 存放接收到的数据的队列，最多只能有1个元素
        self.port_name = ""  # 串口名称
        # 实例化
        self.crc = CRCGenerator()

    # 静态方法，可直接通过类名调用，不需要实例化类
    @staticmethod
    def serach_dev_port():
        """搜索可用的串口"""
        serial_port = []
        # 获取系统串口列表
        serial_port_list = list(serial.tools.list_ports.comports())
        if len(serial_port_list) <= 0:
            pass
        else:
            # 将所有的串口添加到串口列表
            for spl in serial_port_list:
                serial_port.append(spl[0])
        return serial_port

    def open_port(self, port, baudrate=115200):
        """打开指定串口"""
        self.port = serial.Serial(port, baudrate, timeout=1)
        self.port_name = port
        return self.port.is_open

    def close_port(self):
        """关闭当前串口"""
        self.port.close()

    def hexshow(self, data):
        """将二进制数据转换为十六进制字符串"""
        hex_data = ''
        hLen = len(data)
        for i in range(hLen):
            # %02x表示将一个字节转换为两位的十六进制字符串，如果不足两位在前面补0
            hhex = '%02x' % data[i]
            hex_data += hhex
        return hex_data

    def hexsend(self, string_data):
        """将十六进制字符串转换为二进制数据"""
        # python内置函数bytes.fromhex将十六进制字符串转化为二进制数据
        hex_data = bytes.fromhex(string_data)
        return hex_data

    def receivemsg(self):
        """接收数据"""
        while True:
            try:
                # 获取当前在缓冲区等待读取的数据量
                # print('111')
                size = self.port.in_waiting
                if size:
                    # 读取串口中所有的数据，放在recdata里，返回字节数组（bytes类型，以十六进制显示）
                    self.recdata = self.port.read_all()
                    # print('serial:')
                    i = 0
                    while i < len(self.recdata):
                        # 判断开头是不是30
                        if self.recdata[i] == 0x30:
                            # print('30')
                            # 数据长度，不包括CRC
                            length = self.recdata[i + 1] + self.recdata[i + 2]
                            # 将接受的二进制数据转化为十六进制
                            rcvData = self.hexshow(self.recdata[i: i + length + 1])
                            # print(rcvData)
                            # CRC校验
                            crc_value = self.crc.crc_8(rcvData[:-2])
                            if rcvData[-2:] == crc_value:
                                # 判断消息队列是否满了
                                if not self.recvmsg.full():
                                    # 放入队列
                                    # print('input')
                                    self.recvmsg.put(rcvData)
                                else:
                                    print("消息队列满了")
                                i = i + length
                            else:
                                i += 1
                                continue
                        elif self.recdata[i] == 0x21:
                            # print("21")
                            # 数据长度，不包括CRC
                            length = self.recdata[i + 1] + self.recdata[i + 2]
                            # 将接受的二进制数据转化为十六进制
                            rcvData = self.hexshow(self.recdata[i: i + length + 1])
                            # CRC校验
                            crc_value = self.crc.crc_8(rcvData[:-2])
                            if rcvData[-2:] == crc_value:
                                # 判断消息队列是否满了
                                if not self.recvmsg.full():
                                    # 放入队列
                                    self.recvmsg.put(rcvData)
                                else:
                                    pass
                                i = i + length
                            else:
                                i += 1
                                continue
                        else:
                            i += 1
                            continue
            except:
                pass

    def sendmsg(self, sendData):
        """发送数据"""
        if self.crc_send:
            sendData = sendData + self.crc.crc_8(sendData)
        senddata = self.hexsend(sendData)
        self.port.write(senddata)


# if __name__ == '__main__':
#
#     # 实例化串口对象
#     myserial = MySerial()
#     # port = myserial.serach_dev_port()
#     # print(port)
#     # 打开com6口
#     open_flag = myserial.open_port("COM6")
#
#     if open_flag:
#         # 开启线程，接受串口数据
#         t_serial_recv = threading.Thread(target=myserial.receivemsg)
#         t_serial_recv.start()
#         # 发送一条协议
#         myserial.sendmsg("300107005A4801316C")
