import json
import queue
import wave

import numpy as np
import paho.mqtt.client as mqtt
from My import Ui_MainWindow
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import user_mqtt
from main import predict
from Cnn import load_model
from yolov5.detect import *
import record
from yolov5.detect import run

start = 100
q_mqtt_data = queue.Queue(5)
mqtt_client = user_mqtt.MQTTClient("192.168.176.100", 1883, "Gateway_HQYJ/Upload", "Gateway_HQYJ/Issue", q_mqtt_data)


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        # 继承两个父类，并初始化
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.ui_init()

    def ui_init(self):
        # 设置界面左上角的标题
        self.setWindowTitle("语音控制系统")
        self.pushButton.clicked.connect(self.start_warehouse)
        self.pushButton_2.clicked.connect(self.end_warehouse)
        self.pushButton_3.clicked.connect(self.simple_control)


    # 起始仓库识别猫狗
    def start_warehouse(self):
        global start
        record.start_audio()
        list = get()
        for item in list:
            if item['name'] == "cat":
                item['name'] = 5
            elif item['name'] == "dog":
                item['name'] = 6

        print(list)
        # print('co,la',coor,label)
        file = "E:/yolov5/yuyin/test.wav"
        cnn = load_model("cnn_num.pkl")
        start = predict(cnn, file)
        for num in list:
            if start == num["name"]:
                start = num["codex"]

        if start == 1 or 2 or 3 or 4 or 5 or 6:  # 5:cat 6:dog
            mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
                                  json.dumps({
                                      "To_XArm": "Control_XArm_Position"}))
        return start

    # 终点仓库
    def end_warehouse(self):
        global start, mqtt_data
        i = 5
        record.start_audio()
        file = "E:/yolov5/yuyin/test.wav"
        cnn = load_model("cnn_num.pkl")
        end = predict(cnn, file)
        if end == 1 or 2 or 3 or 4 :
            mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
                                  json.dumps({
                                      "To_XArm": {
                                          "Control_XArm_Grab": {
                                              "start": "%d" % start,
                                              "end": "%d" % end}}}))
        # while i >= 0:
        #     mqtt_data = q_mqtt_data.get()
        #     print(mqtt_data)
        #     i -= 1
        # print(mqtt_data)
        # if mqtt_data == "{'Protocol30': {'XArm_Grab_Finished_Upload': 'Finished'}}":
        #     mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
        #                           json.dumps({
        #                               "To_XArm": "Control_XArm_Position"}))

        # mqtt_data1 = mqtt_data.values()
        # mqtt_data2 = mqtt_data1.values()
        # print(mqtt_data1)
        # if mqtt_data2 == "Finished":
        #     print(mqtt_data)
        #     mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
        #                           json.dumps({
        #                               "To_XArm": "Control_XArm_Position"}))

    def simple_control(self):
        record.start_audio()
        file = "E:/yolov5/yuyin/test.wav"
        cnn = load_model("cnn_sim.pkl")
        radio = predict(cnn, file)
        if radio == 3:  # up
            mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
                                  json.dumps({
                                      "To_XArm": {
                                          "Control_XArm_Action": "Nod"}}))
        elif radio == 4:  # down
            mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
                                  json.dumps({
                                      "To_XArm": {
                                          "Control_XArm_Action": "Shake"}}))
        elif radio == 2:  # right
            mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
                                  json.dumps({
                                      "To_XArm": {
                                          "Control_XArm_Action": "Right"}}))

        elif radio == 1:  # left
            mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
                                  json.dumps({
                                      "To_XArm": {
                                          "Control_XArm_Action": "Left"}}))

        elif radio == 5:  # on
            mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
                                  json.dumps({
                                      "To_XArm": {
                                          "Control_XArm_Action": "Grab"}}))

        elif radio == 6:  # off
            mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
                                  json.dumps({
                                      "To_XArm": {
                                          "Control_XArm_Action": "Loose"}}))

        elif radio == 7:  # go
            mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
                                  json.dumps({
                                      "To_XArm": "Control_XArm_Position"}))
            run()

        elif radio == 8:  # stop
            mqtt_client.send_mqtt("Gateway_HQYJ/Issue",
                                  json.dumps({
                                      "To_XArm": {
                                          "Control_XArm_Action": "Stop"}}))

        else:
            print("未检测到指令！")


if __name__ == '__main__':
    # 运行界面必须组件

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 运行界面必须组件
    app = QApplication(sys.argv)
    # 自己写的界面
    MainWindow = MyWindow()
    # 将自己写的界面显示出来
    MainWindow.show()
    # 一直运行界面

    sys.exit(app.exec_())
