# -*- coding: utf-8 -*-


from scipy.stats import norm
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog


import pyqtgraph
from PyQt5.QtWidgets import QApplication, QMainWindow
from rover import *
from PyQt5.QtCore import *
from pyqtgraph import *

import sqlite3
import numpy as np
import pandas
import datetime
import time
import matplotlib

matplotlib.use('Qt5Agg')


rawDataPath = "C:\\Users\\qiliu102\\Documents\\ROVERGUI\\firsttest\\0612.csv"
selCh = ["GFX_FB_V", "CORE_FB_V", "SOC_FB_V", "VDDP_V", "GFX_PH1_CSR", "CORE_PH1_CSR", "SOC_PH1_CSR", "VDDP_CSR"]
refresh = [0.1, 0.1, 1]
chList = [0, 1, 2, 3]
dataList = []
graph_data = []

dataList_graph = []
graph_x = []
graph_y = []
graph_y2 = []
graph_y3 = []
graph_y4 = []
ch_list_default = ['VDDCR_P', 'TOTAL_IO_POWER', 'TOTAL_APU_POWER', 'MEMIO_MEM_P']
timing = 0
timing2 = 0
timing_p1 = 0
arr_g2 = []
data_cfg = []
energy = [0, 0, 0, 0]
conn = sqlite3.connect("rover.db", check_same_thread=False)
cursor = conn.cursor()
cursor1 = conn.cursor()


def DataPaser(refreshRate, powerrail0_v, powerrail1_v, powerrail2_v, powerrail3_v, powerrail0_csr, powerrail1_csr,
              powerrail2_csr, powerrail3_csr):
    cmd_data_filter = 'select ' + powerrail0_v + ',' + powerrail1_v + ',' + powerrail2_v + ',' + powerrail3_v + ',' + powerrail0_csr + ',' + powerrail1_csr + ',' + powerrail2_csr + ',' + powerrail3_csr + ' from roverdata WHERE Seconds LIKE \'_\' OR Seconds LIKE \'__\' '
    print(cmd_data_filter)
    conn = sqlite3.connect("rover.db")
    cursor = conn.cursor()
    cursor.execute(cmd_data_filter)

    global dataList
    tmp = cursor.fetchall()
    dataList = numpy.array(tmp, dtype=numpy.float64)


def calculate_I(data, cnt):
    I = str(format((float(data) / float(data_cfg['CSR'][cnt])), '.2f'))
    return I


def calculate_P(data1, data2):
    p = str(format((float(data1) * float(data2)), '.2f'))
    return p


class BackendThread(QThread):
    upadte_data = pyqtSignal(str, str, str, str, str, str, str, str, str)

    def run(self):
        global timing
        cnt = 0
        while True:
            for row in range(len(dataList)):
                print(len(dataList))
                cnt = cnt + float(refresh[0])
                self.upadte_data.emit(str(dataList[row][0]), str(dataList[row][1]), str(dataList[row][2]),
                                      str(dataList[row][3]), str(dataList[row][4]), str(dataList[row][5]),
                                      str(dataList[row][6]), str(dataList[row][7]), str('{:g}'.format(timing)))
                time.sleep(refresh[0])
                timing = timing + refresh[0]
                if timing > 30:
                    return


class BackendThreadTable(QThread):
    upadte_table = pyqtSignal(str, str, str, str, str, str, str, str)
    global timing

    def run(self):
        cnt = 0
        while True:
            for row in range(len(dataList)):
                self.upadte_table.emit(str(dataList[row][0]), str(dataList[row][1]), str(dataList[row][2]),
                                       str(dataList[row][3]), str(dataList[row][4]), str(dataList[row][5]),
                                       str(dataList[row][6]),
                                       str(dataList[row][7]))
                cnt = cnt + refresh[1]
                time.sleep(refresh[1])
                if timing > 30:
                    return


class graph_drawing(QThread):
    #draw_graph = pyqtSignal(str, str, str, str, str, str, str, str)
    def __init__(self):
        super(graph_drawing, self).__init__()

    def run(self):
        global graph_x
        global graph_y
        global graph_y2
        global graph_y3
        global graph_y4
        global timing_p1
        while True:
            while (timing_p1 <= 30):
                # print("timeing is %d" % timing)
                cmd_data_filter = 'select Seconds,' + selCh[0] + ',' + selCh[1] + ',' + selCh[2] + ',' + selCh[
                    3] + ' from roverdata WHERE (Seconds LIKE \'_\' OR Seconds LIKE \'__\' OR Seconds LIKE \'_._\' OR Seconds LIKE \'__._\') AND Seconds = ' + str('{:g}'.format(timing_p1))
                timing_p1 = timing_p1 + 0.4
                # print(cmd_data_filter)
                cursor.execute(cmd_data_filter)
                tmp = cursor.fetchall()
                tmp1 = numpy.array(tmp, dtype=numpy.float64)
                graph_x.append(float(tmp1[:, 0]))
                graph_y.append(float(tmp1[:, 1]))
                graph_y2.append(float(tmp1[:, 2]))
                graph_y3.append(float(tmp1[:, 3]))
                graph_y4.append(float(tmp1[:, 4]))
                    # print('####')
                    # print(timing_p1)
                    # print(graph_x)
                    # print(graph_y)
                    # print(graph_y2)
                    # print(graph_y3)
                    # print(graph_y4)
                myRoverUI.curver.setData(graph_x, graph_y)
                myRoverUI.curver2.setData(graph_x, graph_y2)
                myRoverUI.curver3.setData(graph_x, graph_y3)
                myRoverUI.curver4.setData(graph_x, graph_y4)
                # time.sleep(0.1)
                if timing_p1 > 30:
                    return


class graph2_drawing(QThread):
    draw_graph2 = pyqtSignal(object, str, object, object, object, object, object)

    def __init__(self):
        super(graph2_drawing, self).__init__()

    def run(self):
        global timing2
        global arr_g2
        arr_tmp = arr_g2.copy()
        while timing2 <= 30:
            start = time.time()
            hist_bins = 30
            timing2 = timing2 + 0.5
            A = 'select ' + selCh[0] + ' from roverdata WHERE (Seconds LIKE \'_._\' OR Seconds LIKE \'__._\' OR Seconds LIKE \'_\' OR Seconds LIKE \'__\') AND Seconds = ' + str('{:g}'.format(timing2))
            # print(A)
            cursor1.execute(A)

            values = cursor1.fetchall()
            # print(values)
            arr = np.array(values, dtype=np.float64)
            arr_tmp = numpy.append(arr_tmp, arr.copy(), axis=0)
            # print("#####ori")
            # print(arr_tmp)
            if timing2 > 10:
                count = int((timing2 - 10) * 2)
            else:
                count = 0
            # print(count)
            arr_g2 = arr_tmp[count:]
            # print("#####after")
            # print(arr_g2)
            m = arr_g2.copy()

            mu = np.mean(m)
            sigma = np.std(m)
            xMin = min(arr_g2).copy()
            xMax = max(arr_g2).copy()
            #n, bins, patches = plt.hist(m, hist_bins, density=0, alpha=0.75)
            bin_range = np.linspace(float(xMin), float(xMax), hist_bins)  # float((xMax-xMin)/hist_bins)
            # print(bin_range)
            histo = numpy.histogram(m, bins=bin_range)
            # histo = plt.hist(m, hist_bins, density=0)
            # print(histo.type())

            title = 'Histogram: μ= ' + str(round(mu, 2)) + ' σ= ' + str(round(sigma, 2))  # 中文标题 u'xxx'
            #self.draw_graph2.emit(histo, title)
            # myRoverUI.graphicsView.setLabels(title=title)
            # time.sleep(1)
            #
            width = histo[1][1] - histo[1][0]
            yMax = max((histo[0] / len(arr_g2))).copy()
            # myRoverUI.graphicsView.clear()
            #myRoverUI.graphicsView.setRange(xRange=(xMin, xMax), yRange=(0, yMax))
            #bg1 = pyqtgraph.BarGraphItem(x=histo[1][0:(len(bin_range)-1)], height=histo[0] / len(arr_g2), width=width, brush='g')
            # myRoverUI.graphicsView.addItem(bg1)
            self.draw_graph2.emit(histo, title, width, yMax, xMax, xMin, bin_range)
            end = time.time()

            stri = "run time: %f seconds" % (end - start)
            print(stri)

#         global timing2
#         global arr_g2
#         hist_bins = 30
#         timing2 = timing2 + 500
#         A = 'select ' + 'MEMIO_MEM_P' + ' from roverdata WHERE (Seconds LIKE \'_._\' OR Seconds LIKE \'__._\' OR Seconds LIKE \'_\' OR Seconds LIKE \'__\') AND Seconds = ' + str(
#             timing2/1000).rstrip('.0')
#         print(A)
#         cursor.execute(A)
#
#         values = cursor.fetchall()
#         arr = np.array(values, dtype=np.float64)
#         arr_g2 = numpy.append(arr_g2, arr.copy(), axis=0)
#         m = arr_g2.copy()
#         mu = np.mean(m)
#         sigma = np.std(m)
#         #n, bins, patches = plt.hist(m, hist_bins, density=0, alpha=0.75)
#         histo = plt.hist(m, hist_bins, density=0)
#         title = 'Histogram: μ= ' + str(round(mu, 2)) + ' σ= ' + str(round(sigma, 2))  # 中文标题 u'xxx'
#         self.graphicsView.setLabels(title=title)
#
#         width = histo[1][1]-histo[1][0]
#
#         xMin = min(arr_g2).copy()
#         xMax = max(arr_g2).copy()
#         yMax = max((histo[0] / len(arr_g2))).copy()
#         self.graphicsView.setRange(xRange=(xMin, xMax), yRange=(0, yMax))
#         bg1 = pyqtgraph.BarGraphItem(x=histo[1][0:hist_bins], height=histo[0] / len(arr_g2),width=width, brush='g')
#         self.graphicsView.clear()
#         self.graphicsView.addItem(bg1)


class RoverUI(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super(RoverUI, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Rover - Power Diagnostic Tool Kits')
        self.init_ui()

    def init_ui(self):
        # self.plotWin = Graph_init(self.widget_g2)
        self.graphicsView_2.showGrid(x=True, y=True)
        # pyqtgraph.setConfigOptions(leftButtonPan=False, antialias=True)  #打开抗锯齿
        self.graphicsView_2.setLabels(left='Voltage/V', bottom='Time/Sec', title='Real Time Scope')
        self.graphicsView.showGrid(x=True, y=True)
        title = 'Histogram: μ= ##' + ' σ= ##'
        self.graphicsView.setLabels(left='Probability', bottom='Values', title=title)
        # self.graphicsView.setBackgroundColor('w')
        # self.graphicsView.setConfigOption('foreground', 'k')
        self.timer = pyqtgraph.QtCore.QTimer()
        self.timer2 = pyqtgraph.QtCore.QTimer()
        self.backend = BackendThread()
        self.backend_table = BackendThreadTable()
        self.backend_graph1 = graph_drawing()
        self.backend_graph2 = graph2_drawing()
        self.timer.timeout.connect(self.graph_update_data)
        self.timer2.timeout.connect(self.graph_update_data2)
        # self.checkBox_1.setChecked(True)
        # self.checkBox_2.setChecked(True)
        # self.checkBox_3.setChecked(True)
        # self.checkBox_4.setChecked(True)
        self.checkBox_1.stateChanged.connect(self.btn_select_ch1_action)
        self.checkBox_2.stateChanged.connect(self.btn_select_ch2_action)
        self.checkBox_3.stateChanged.connect(self.btn_select_ch3_action)
        self.checkBox_4.stateChanged.connect(self.btn_select_ch4_action)
        self.comboBox_refresh_chs.currentIndexChanged.connect(self.btnSelectRefresh1Action)
        self.comboBox_refresh_table.currentIndexChanged.connect(self.btnSelectRefresh2Action)
        self.comboBox_graph.currentTextChanged.connect(self.btn_select_graph2_action)
        self.pushButton_start_table.clicked.connect(self.btn_start_table)
        self.pushButton_start_p1.clicked.connect(self.btn_start_graph)
        self.pushButton_start_p2.clicked.connect(self.btn_start_graph2)
        self.pushButton_loadCFG.clicked.connect(self.btn_load_cfg)
        self.pushButton_clear_g1.clicked.connect(self.btn_clear_g1)
        self.pushButton_clear_g2.clicked.connect(self.btn_clear_g2)
        # self.backend.upadte_data.connect(self.dataDisplay)
        # self.backend.start()
        # self.backend_table.start()

    def btn_select_ch1_action(self):
        selCh[0] = data_cfg['NAME'][0]
        self.label_dislay_ch1.setText(selCh[0])
        self.label_dislay_ch1_2.setText(selCh[0])

    def btn_select_ch2_action(self):
        selCh[1] = data_cfg['NAME'][1]
        self.label_dislay_ch2.setText(selCh[1])
        self.label_dislay_ch2_2.setText(selCh[1])

    def btn_select_ch3_action(self):
        selCh[2] = data_cfg['NAME'][2]
        self.label_dislay_ch3.setText(selCh[2])
        self.label_dislay_ch3_2.setText(selCh[2])

    def btn_select_ch4_action(self):
        selCh[3] = data_cfg['NAME'][3]
        self.label_dislay_ch4.setText(selCh[3])
        self.label_dislay_ch4_2.setText(selCh[3])

    def btnSelectRefresh1Action(self):
        myStr = self.comboBox_refresh_chs.currentText()
        refresh[0] = myStr[0]

    def btnSelectRefresh2Action(self):
        myStr = self.comboBox_refresh_table.currentText()
        refresh[1] = myStr[0]

    def btn_select_graph2_action(self):
        myStr = self.comboBox_graph.currentText()
        selCh[0] = myStr
        print(myStr)

    def btn_start_table(self):
        self.backend.start()
        self.backend_table.start()
        DataPaser(float(refresh[0]), selCh[0], selCh[1], selCh[2], selCh[3], selCh[4], selCh[5], selCh[6], selCh[7])
        self.backend.upadte_data.connect(self.dataDisplay)
        self.backend_table.upadte_table.connect(self.tableDisplay)
        print('start')

    def btn_clear_g1(self):
        self.graphicsView_2.clear()

    def btn_clear_g2(self):
        self.graphicsView.clear()

    def dataDisplay(self, data0, data1, data2, data3, data4, data5, data6, data7, time_data):
        self.label_timing.setText(time_data)
        self.label_ch1_e.setText(calculate_P(data0, calculate_I(data4, 0)))
        self.label_ch2_e.setText(calculate_P(data1, calculate_I(data5, 1)))
        self.label_ch3_e.setText(calculate_P(data2, calculate_I(data6, 2)))
        self.label_ch4_e.setText(calculate_P(data3, calculate_I(data7, 3)))
        self.label_ch1_i.setText(calculate_I(data4, 0))
        self.label_ch2_i.setText(calculate_I(data5, 0))
        self.label_ch3_i.setText(calculate_I(data6, 0))
        self.label_ch4_i.setText(calculate_I(data7, 0))
        self.label_ch1_v.setText(data0)
        self.label_ch2_v.setText(data1)
        self.label_ch3_v.setText(data2)
        self.label_ch4_v.setText(data3)

    def tableDisplay(self, data0, data1, data2, data3, data4, data5, data6, data7):
        _translate = QtCore.QCoreApplication.translate
        global energy
        item = self.tableWidget.item(0, 2)
        item.setText(_translate("Dialog", data0))
        item = self.tableWidget.item(0, 3)
        item.setText(_translate("Dialog", calculate_I(data4, 0)))
        item = self.tableWidget.item(0, 4)
        item.setText(_translate("Dialog", calculate_P(data0, calculate_I(data4, 0))))
        energy[0] = energy[0] + float(calculate_P(data0, calculate_I(data4, 0))) * float(refresh[0])
        item = self.tableWidget.item(0, 5)
        item.setText(_translate("Dialog", str('%.2f' % energy[0])))

        item = self.tableWidget.item(1, 2)
        item.setText(_translate("Dialog", data1))
        item = self.tableWidget.item(1, 3)
        item.setText(_translate("Dialog", calculate_I(data5, 1)))
        item = self.tableWidget.item(1, 4)
        item.setText(_translate("Dialog", calculate_P(data1, calculate_I(data5, 1))))
        energy[1] = energy[1] + float(calculate_P(data1, calculate_I(data5, 1))) * float(refresh[0])
        item = self.tableWidget.item(1, 5)
        item.setText(_translate("Dialog", str('%.2f' % energy[1])))

        item = self.tableWidget.item(2, 2)
        item.setText(_translate("Dialog", data2))
        item = self.tableWidget.item(2, 3)
        item.setText(_translate("Dialog", calculate_I(data6, 2)))
        item = self.tableWidget.item(2, 4)
        item.setText(_translate("Dialog", calculate_P(data2, calculate_I(data6, 2))))
        energy[2] = energy[2] + float(calculate_P(data2, calculate_I(data6, 2))) * float(refresh[0])
        item = self.tableWidget.item(2, 5)
        item.setText(_translate("Dialog", str('%.2f' % energy[2])))

        item = self.tableWidget.item(3, 2)
        item.setText(_translate("Dialog", data3))
        item = self.tableWidget.item(3, 3)
        item.setText(_translate("Dialog", calculate_I(data7, 3)))
        item = self.tableWidget.item(3, 4)
        item.setText(_translate("Dialog", calculate_P(data3, calculate_I(data7, 3))))
        energy[3] = energy[3] + float(calculate_P(data3, calculate_I(data7, 3))) * float(refresh[0])
        item = self.tableWidget.item(3, 5)
        item.setText(_translate("Dialog", str('%.2f' % energy[3])))

    def btn_start_graph(self):
        # data_collect(int(refresh[2]), selCh[0], selCh[1], selCh[2], selCh[3])
        global timing_p1

        self.curver = self.graphicsView_2.plot(graph_x, graph_y, pen='y')
        self.curver2 = self.graphicsView_2.plot(graph_x, graph_y2, pen='r')
        self.curver3 = self.graphicsView_2.plot(graph_x, graph_y3, pen='g')
        self.curver4 = self.graphicsView_2.plot(graph_x, graph_y4, pen=(0, 255, 255))
        self.backend_graph1.start()
        # self.timer.start(100)
        #timing_p1 = timing

    def graph_update_data(self):
        global graph_x
        global graph_y
        global graph_y2
        global graph_y3
        global graph_y4
        global timing_p1

        # start = time.time()
        #
        # cmd_data_filter = 'select Seconds,' + selCh[0] + ',' + selCh[1] + ',' + selCh[2] + ',' + selCh[
        #     3] + ' from roverdata WHERE (Seconds LIKE \'_\' OR Seconds LIKE \'__\' OR Seconds LIKE \'_._\' OR Seconds LIKE \'__._\') AND Seconds = ' + str('{:g}'.format(timing_p1))
        # timing_p1 = timing_p1 + 0.1
        # #print(cmd_data_filter)
        # cursor.execute(cmd_data_filter)
        # tmp = cursor.fetchall()
        # tmp1 = numpy.array(tmp, dtype=numpy.float64)
        # #print(tmp)
        #
        # graph_x.append(float(tmp1[:, 0]))
        # graph_y.append(float(tmp1[:, 1]))
        # graph_y2.append(float(tmp1[:, 2]))
        # graph_y3.append(float(tmp1[:, 3]))
        # graph_y4.append(float(tmp1[:, 4]))
        #
        # # print(graph_x)
        # # print(graph_y)
        # # print(graph_y2)
        # # print(graph_y3)
        # # print(graph_y4)
        # self.curver.setData(graph_x, graph_y)
        # self.curver2.setData(graph_x, graph_y2)
        # self.curver3.setData(graph_x, graph_y3)
        # self.curver4.setData(graph_x, graph_y4)
        # end = time.time()
        #
        # stri = "run time: %f seconds" % (end - start)
        # print(stri)

    def btn_start_graph2(self):
        global timing2
        global arr_g2
        # time.sleep(9)
        hist_bins = 30
        A = 'select ' + selCh[0] + ' from roverdata WHERE Seconds = 0'
        #A = 'select ' + selCh[0] + ' from roverdata WHERE Seconds LIKE \'_.5\' OR Seconds LIKE \'_\''
        print(A)
        # conn = sqlite3.connect("rover.db")
        # cursor = conn.cursor()
        cursor1.execute(A)
        values = cursor1.fetchall()
        print(values)
        arr_g2 = np.array(values, dtype=np.float64)
        print(arr_g2)
        x = arr_g2.copy()
        mu = np.mean(x)
        sigma = np.std(x)
        #n, bins, patches = plt.hist(x, hist_bins, density=0, alpha=0.75)
        xMin = min(arr_g2).copy()
        xMax = max(arr_g2).copy()
        bin_range = np.linspace(float(xMin), float(xMax), hist_bins)
        histo = numpy.histogram(x, bins=bin_range)
        # y = norm.pdf(bins, mu, sigma)  # 拟合一条最佳正态分布曲线y
        # plt.grid(True)
        # plt.plot(bins, y, 'r--')  # 绘制y的曲线
        title = 'Histogram: μ= ' + str(round(mu, 2)) + ' σ= ' + str(round(sigma, 2))  # 中文标题 u'xxx'
        self.graphicsView.setLabels(left='Probability', bottom='Values', title=title)
        width = histo[1][1] - histo[1][0]
        print(histo[0])
        print(len(arr_g2))
        yMax = max((histo[0] / len(arr_g2))).copy()
        self.graphicsView.setRange(xRange=(xMin, xMax), yRange=(0, yMax))
        bg1 = pyqtgraph.BarGraphItem(x=histo[1][0:(len(bin_range) - 1)], height=histo[0] / len(arr_g2), width=width, brush='g')
        self.graphicsView.addItem(bg1)
        # self.graphicsView.plot(y)
        # self.timer2.start(500)
        self.backend_graph2.start()
        self.backend_graph2.draw_graph2.connect(self.graph_update_data3)

    def graph_update_data3(self, histo, title, width, yMax, xMax, xMin, bin_range):
        # print(object)
        # print(data)
        #self.draw_graph2.emit(histo, title)
        myRoverUI.graphicsView.setLabels(title=title)
        myRoverUI.graphicsView.clear()
        myRoverUI.graphicsView.setRange(xRange=(xMin, xMax), yRange=(0, yMax))
        bg1 = pyqtgraph.BarGraphItem(x=histo[1][0:(len(bin_range) - 1)], height=histo[0] / len(arr_g2), width=width, brush='g')
        myRoverUI.graphicsView.addItem(bg1)

    def graph_update_data2(self):
        global timing2
        global arr_g2

        # start = time.time()
        # hist_bins = 30
        # timing2 = timing2 + 0.5
        # A = 'select ' + 'GFX_FB_V' + ' from roverdata WHERE (Seconds LIKE \'_._\' OR Seconds LIKE \'__._\' OR Seconds LIKE \'_\' OR Seconds LIKE \'__\') AND Seconds = ' + str('{:g}'.format(timing2))
        # #print(A)
        # cursor1.execute(A)
        #
        # values = cursor1.fetchall()
        # arr = np.array(values, dtype=np.float64)
        # arr_g2 = numpy.append(arr_g2, arr.copy(), axis=0)
        # m = arr_g2.copy()
        # mu = np.mean(m)
        # sigma = np.std(m)
        # xMin = min(arr_g2).copy()
        # xMax = max(arr_g2).copy()
        # #n, bins, patches = plt.hist(m, hist_bins, density=0, alpha=0.75)
        # bin_range = np.linspace(float(xMin), float(xMax), hist_bins)#float((xMax-xMin)/hist_bins)
        # #print(bin_range)
        # histo = numpy.histogram(m, bins=bin_range)
        # # histo = plt.hist(m, hist_bins, density=0)
        # #print(histo)
        #
        # title = 'Histogram: μ= ' + str(round(mu, 2)) + ' σ= ' + str(round(sigma, 2))  # 中文标题 u'xxx'
        # self.graphicsView.setLabels(title=title)
        #
        # width = histo[1][1]-histo[1][0]
        # yMax = max((histo[0] / len(arr_g2))).copy()
        # self.graphicsView.clear()
        # self.graphicsView.setRange(xRange=(xMin, xMax), yRange=(0, yMax))
        # bg1 = pyqtgraph.BarGraphItem(x=histo[1][0:(len(bin_range)-1)], height=histo[0] / len(arr_g2), width=width, brush='g')
        # self.graphicsView.addItem(bg1)
        #
        # end = time.time()
        #
        # stri = "run time: %f seconds" % (end - start)
        # print(stri)
    def btn_load_cfg(self):
        global data_cfg
        _translate = QtCore.QCoreApplication.translate
        cfg_diag = QFileDialog()
        cfg_diag.setFileMode(QFileDialog.AnyFile)
        cfg_diag.setFilter(QDir.Files)
        if cfg_diag.exec():
            filenames = cfg_diag.selectedFiles()
            data_cfg = pandas.read_csv(filenames[0])
            print(data_cfg)
        for i in range(0, 8):
            item = self.tableWidget.verticalHeaderItem(i)
            item.setText(_translate("Dialog", data_cfg['Device'][i]))
            item = self.tableWidget.item(i, 0)
            item.setText(_translate("Dialog", data_cfg['NAME'][i]))
            item = self.tableWidget.item(i, 1)
            item.setText(_translate("Dialog", str(data_cfg['Voltage'][i].astype('float'))))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myRoverUI = RoverUI()
    myRoverUI.show()
    sys.exit(app.exec())
    cursor.close()
    conn.close()
