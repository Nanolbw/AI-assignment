# -*- coding: utf-8 -*-
# @Time    : 2023/5/10 10:49
# @Author  : HanYanze
# @Description :用户的MQTT的类，用于连接、订阅与发布

import json  # 处理JSON数据的库
import queue  # 消息队列库
import paho.mqtt.client as mqtt  # 用于与MQTT服务器通信的库


class MQTTClient:
    """
    mqtt
    """

    def __init__(self, target_ip, default_port, sub_topic, pub_topic, q_mqtt_data):
        """
        初始化
        :param target_ip: mqtt服务器IP
        :param default_port: mqtt端口号
        :param sub_topic: sub的topic
        :param pub_topic: pub的topic
        """
        self.client = mqtt.Client()  # 创建MQTT client实例
        self.q_mqtt_data = q_mqtt_data  # 接收MQTT数据的消息队列
        self.client.on_connect = self.on_connect  # 绑定MQTT的on_connect回调函数
        self.client.on_message = self.on_message  # 绑定MQTT的on_message回调函数
        try:
            self.client.connect(target_ip, default_port, 60)  # 连接到MQTT服务器
        except Exception as e:
            self.q_mqtt_data.put({"connect": e})  # 连接失败，将错误信息加入消息队列
        self.pub_topic = pub_topic  # 发布MQTT消息的主题
        self.client.subscribe(sub_topic, qos=0)  # 订阅MQTT消息
        self.client.loop_start()  # 启动MQTT客户端的消息循环
        self.message = ""  # 初始化消息变量

    def on_connect(self, client, userdata, flags, rc):
        """
        连接功能
        :param client: MQTT client实例
        :param userdata: 用户数据，通常为None
        :param flags: 连接标志
        :param rc: 连接结果码 0：代表连接成功。
                            1：代表连接被服务端拒绝，原因是不支持客户端的MQTT协议版本。
                            2：代表连接被服务端拒绝，原因是不支持客户端标识符的编码。
                            3：代表连接被服务端拒绝，原因是服务端不可用。
                            4：代表连接被服务端拒绝，原因是用户名或密码无效。
                            5：代表连接被服务端拒绝，原因是客户端未被授权连接到此服务端。
        :return: none
        """
        if rc == 0:
            print("Connected to MQTT OK!")  # 连接成功，输出提示信息
            self.q_mqtt_data.put({"connect": "success"})  # 将连接成功的信息加入消息队列
        else:
            print("Failed to connect, return code %d\n", rc)  # 连接失败，输出提示信息
            self.q_mqtt_data.put({"connect": rc})  # 将连接失败的信息加入消息队列

    def on_message(self, client, userdata, msg):
        """
        接收数据
        :param client: MQTT client实例
        :param userdata:
        :param msg: 接收到的信息
        :return: none
        """
        try:
            self.q_mqtt_data.put(json.loads(msg.payload.decode()))  # 将接收到的MQTT数据解码后加入消息队列
        except Exception as e:
            print(e)  # 解码失败，输出错误信息

    def send_mqtt(self, pub_topic, data):
        """
        发送mqtt
        :param data: 发送的数据
        :return: none
        """
        self.client.publish(pub_topic, payload=data, qos=0)  # 发送MQTT消息到指定主题


# if __name__ == '__main__':
#     q_mqtt_data = queue.Queue(5)
#     mqtt_client = MQTTClient("127.0.0.1", 1883, "state/#", "control", q_mqtt_data)
#     mqtt_client.send_mqtt("control", json.dumps({"irrigation": "on"}))
#     while True:
#         mqtt_data = q_mqtt_data.get()
#         print(mqtt_data)
