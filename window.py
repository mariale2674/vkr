#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style
import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
import load_balance as lb
import codecs
import random

LARGE_FONT = ("Verdana, 12")
NORMAL_FONT = ("TimesNewRoman, 10")
SMALL_FONT = ("TimesNewRoman, 8")

style.use("ggplot")

M = 5
var_u = '0'
var_forecast = '0'
var_queue = '0'
var_lost = '0'


def popupmsg(msg):
    popup = tk.Tk()

    def leavemini():
        popup.destroy()

    popup.wm_title('!')

    label = tk.Label(popup, text=msg)
    label.pack()

    b1 = tk.Button(popup, text="Ok", width=10, command = leavemini)
    b1.pack()

    popup.mainloop()


class LoadBalance(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, 'Система мониторинга загруженности серверов')

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # scrollbar = tk.Scrollbar(self)
        # scrollbar.pack(side = tk.RIGHT, fill = Y)

        menu = tk.Menu(container)
        filemenu = tk.Menu(menu, tearoff=0)
        filemenu.add_command(label="Выход", command=lambda: container.quit())

        helpmenu = tk.Menu(menu, tearoff=0)
        helpmenu.add_command(label='Помощь',
                             command = lambda: popupmsg('Никто вам не поможет.\n'))
        helpmenu.add_command(label="О программе")

        menu.add_cascade(label="Файл", menu=filemenu)
        menu.add_cascade(label="Справка", menu=helpmenu)

        tk.Tk.config(self, menu=menu)

        self.frames = {}

        for F in (StartPage, ThreeServerWindow, FourServerWindow, FiveServerWindow):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, count):
        frame = self.frames[count]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.label = tk.Label(self, text='Выберите количество серверов:', width=50, height=5, font=LARGE_FONT)
        self.label.grid(row=0, column=0, columnspan=3)

        self.button1 = tk.Button(self, text='3 сервера',
                                  command=lambda: controller.show_frame(ThreeServerWindow))
        self.button1.grid(row=2, column=0)

        self.button2 = tk.Button(self, text='4 сервера',
                                 command=lambda: controller.show_frame(FourServerWindow))
        self.button2.grid(row=2, column=1)

        self.button3 = tk.Button(self, text='5 серверов',
                                 command=lambda: controller.show_frame(FiveServerWindow))
        self.button3.grid(row=2, column=2)


class ThreeServerWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text='Загруженность сети',
                              font=LARGE_FONT)
        self.label.grid(sticky=tk.N, column=0, columnspan=3, pady=7)

        self.img = ImageTk.PhotoImage(Image.open("img/N3.jpg"))
        self.topology = tk.Label(self, image=self.img)
        self.topology.grid(row=1, column=0, columnspan=2, padx=7)

        self.info = tk.Frame(self)
        self.info.grid(row=2, column=0)
        self.info_text1 = tk.Label(self.info, text='Загруженность:',
                                  font=NORMAL_FONT)
        self.info_text2 = tk.Label(self.info, text='Прогноз:',
                                  font=NORMAL_FONT)
        self.info_text3 = tk.Label(self.info, text='Очередь:',
                                  font=NORMAL_FONT)
        self.info_text4 = tk.Label(self.info, text='Потерянные запросы:',
                                  font=NORMAL_FONT)
        self.info_text1.grid(row=0, sticky=tk.W, padx=7)
        self.info_text2.grid(row=1, sticky=tk.W, padx=7)
        self.info_text3.grid(row=2, sticky=tk.W, padx=7)
        self.info_text4.grid(row=3, sticky=tk.W, padx=7)

        self.data_u = tk.Label(self.info, text=var_u,
                               font=SMALL_FONT)
        self.data_forecast = tk.Label(self.info, text=var_forecast,
                               font=SMALL_FONT)
        self.data_queue = tk.Label(self.info, text=var_queue,
                               font=SMALL_FONT)
        self.data_lost = tk.Label(self.info, text=var_lost,
                               font=SMALL_FONT)
        self.data_u.grid(row=0, column=2, sticky=tk.W, padx=7)
        self.data_forecast.grid(row=1, column=2, sticky=tk.W, padx=7)
        self.data_queue.grid(row=2, column=2, sticky=tk.W, padx=7)
        self.data_lost.grid(row=3, column=2, sticky=tk.W, padx=7)

        self.button1 = tk.Button(self, text='Старт',
                                 command=lambda: ThreeServerWindow.start(self))
        self.button1.grid(row=3, column=0, pady=7)
        self.button2 = tk.Button(self, text='Назад',
                                 command=lambda: controller.show_frame(StartPage))
        self.button2.grid(row=3, column=1, pady=7)

        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=2, rowspan=3)

        # self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        # self.toolbar.update()

    def start(self):
        self.N = 3
        self.u = np.array([0] * self.N)
        self.u_max = np.array([3000, 4000, 5000])
        self.time = np.array([100, 200, 300])
        self.X = np.array([[1, 0, 1, 0, 1],
                           [0, 1, 1, 0, 1],
                           [1, 0, 1, 1, 0]])

        LB = lb.LoadBalance(self.u, self.u_max, self.X, self.time, self.N)
        LB.distribution(LB.u, LB.u_max, LB.X, LB.time, LB.N)

        ThreeServerWindow.build_graph(self, self.fig,
                                     self.ax1, self.ax2, self.ax3,
                                     self.canvas)

        try:
            pullData = open("buf.txt", "r").read()
            dataList = pullData.split('\n')

            self.data_u = tk.Label(self.info, text=dataList[0],
                                   font=SMALL_FONT)
            self.data_forecast = tk.Label(self.info, text=dataList[1],
                                          font=SMALL_FONT)
            self.data_queue = tk.Label(self.info, text=dataList[2],
                                       font=SMALL_FONT)
            self.data_lost = tk.Label(self.info, text=dataList[3],
                                      font=SMALL_FONT)
            self.data_u.grid(row=0, column=2, sticky=tk.W, padx=7)
            self.data_forecast.grid(row=1, column=2, sticky=tk.W, padx=7)
            self.data_queue.grid(row=2, column=2, sticky=tk.W, padx=7)
            self.data_lost.grid(row=3, column=2, sticky=tk.W, padx=7)
        except IOError:
            print("An IOError has occurred!")

    def test_graph(self, fig, ax1, ax2, ax3, canvas):
        xList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        yList = [5, 2, 7, 7, 8, 0, 6, 4, 3, 3]

        ax1.plot(xList, yList, "black", label='CPU')

        # self.canvas = FigureCanvasTkAgg(self.fig, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=2, rowspan=3)

    def build_graph(self, fig, ax1, ax2, ax3, canvas):
        try:
            file1 = open("N2.txt", "r").read()
            ax1_list = file1.split('\n')
            xList = []
            yList = []

            for eachLine in ax1_list:
                if len(eachLine) > 1:
                    x, y = eachLine.split(',')
                    xList.append(int(x))
                    yList.append(int(y))

            ax1.plot(xList, yList, "black", label='CPU')
            ax1.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3, ncol=2, borderaxespad=0)

            title = "Сервер N1"
            ax1.set_title(title)

            file2 = open("N2.txt", "r").read()
            ax2_list = file2.split('\n')
            xList = []
            yList = []

            for eachLine in ax2_list:
                if len(eachLine) > 1:
                    x, y = eachLine.split(',')
                    xList.append(int(x))
                    yList.append(int(y))

            ax2.plot(xList, yList, "black", label='CPU')
            ax2.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3, ncol=2, borderaxespad=0)

            title = "Сервер N2"
            ax2.set_title(title)

            file3 = open("N3.txt", "r").read()
            ax3_list = file3.split('\n')
            xList = []
            yList = []

            for eachLine in ax3_list:
                if len(eachLine) > 1:
                    x, y = eachLine.split(',')
                    xList.append(int(x))
                    yList.append(int(y))

            ax3.plot(xList, yList, "black", label='CPU')
            ax3.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3, ncol=2, borderaxespad=0)

            title = "Сервер N3"
            ax3.set_title(title)

            canvas.draw()
            canvas.get_tk_widget().grid(row=1, column=2, rowspan=3)
        except IOError:
            print("An IOError has occurred!")


class FourServerWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text='Загруженность сети', font=LARGE_FONT)
        self.label.grid(row=0, column=0, columnspan=3)

        self.img = ImageTk.PhotoImage(Image.open("img/N3.jpg"))
        self.topology = tk.Label(self, image=self.img)
        self.topology.grid(row=1, column=0, columnspan=2)

        self.info = tk.Label(self, text='Информация:\n', width=50, height=5)
        self.info.grid(row=2, column=0, columnspan=2)

        self.button1 = tk.Button(self, text='Старт',
                                 command=lambda: FourServerWindow.start(self))
        self.button1.grid(row=3, column=0, pady=7)
        self.button2 = tk.Button(self, text='Назад',
                                 command=lambda: controller.show_frame(StartPage))
        self.button2.grid(row=3, column=1, pady=7)

        # canvas = FigureCanvasTkAgg(fig, self)
        # canvas.draw()
        # canvas.get_tk_widget().grid(row=1, column=2, rowspan=3)

    def start(self):
        self.N = 4
        self.u = np.array([0] * self.N)
        self.u_max = np.array([3000, 4000, 5000, 4000])
        self.time = np.array([100, 150, 200, 300])
        self.X = np.array([[1, 0, 0, 0, 1],
                           [0, 1, 0, 0, 0],
                           [0, 0, 1, 0, 0],
                           [0, 0, 0, 1, 0]])

        LB = lb.LoadBalance(self.u, self.u_max, self.X, self.time, self.N)
        LB.distribution(LB.u, LB.u_max, LB.X, LB.time, LB.N)


class FiveServerWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text='Загруженность сети', font=LARGE_FONT)
        self.label.grid(row=0, column=0, columnspan=3)

        self.img = ImageTk.PhotoImage(Image.open("img/N3.jpg"))
        self.topology = tk.Label(self, image=self.img)
        self.topology.grid(row=1, column=0, columnspan=2)

        self.info = tk.Label(self, text='Информация:\n', width=50, height=5)
        self.info.grid(row=2, column=0, columnspan=2)

        self.button1 = tk.Button(self, text='Старт',
                                 command=lambda: FiveServerWindow.start(self))
        self.button1.grid(row=4, column=0, pady=7)
        self.button2 = tk.Button(self, text='Назад',
                                 command=lambda: controller.show_frame(StartPage))
        self.button2.grid(row=4, column=1, pady=7)

        # canvas = FigureCanvasTkAgg(fig, self)
        # canvas.draw()
        # canvas.get_tk_widget().grid(row=1, column=2, rowspan=4)

    def start(self):
        self.N = 5
        self.u = np.array([0] * self.N)
        self.u_max = np.array([1000, 2000, 3000, 4000, 5000])
        self.time = np.array([300, 200, 200, 300, 400])
        self.X = np.array([[1, 0, 0, 0, 0],
                           [0, 1, 0, 0, 0],
                           [0, 0, 1, 0, 0],
                           [0, 1, 1, 1, 0],
                           [1, 1, 0, 1, 1]])

        LB = lb.LoadBalance(self.u, self.u_max, self.X, self.time, self.N)
        LB.distribution(LB.u, LB.u_max, LB.X, LB.time, LB.N)


def check_files():
    try:
        file = codecs.open("buf.txt", "w", "utf-8")
        file.close()
        file = codecs.open("N1.txt", "w", "utf-8")
        file.close()
        file = codecs.open("N2.txt", "w", "utf-8")
        file.close()
        file = codecs.open("N3.txt", "w", "utf-8")
        file.close()
        file = codecs.open("N4.txt", "w", "utf-8")
        file.close()
        file = codecs.open("N5.txt", "w", "utf-8")
        file.close()
    except IOError:
        print("An IOError has occurred!")

def main():
    check_files()

    app = LoadBalance()
    app.geometry("1000x500")
    # ani = animation.FuncAnimation(fig, animate, interval=25)
    app.mainloop()


if __name__ == '__main__':
    main()
