#!/usr/bin/python
# -*- coding: utf-8 -*-

import matplotlib
import matplotlib.ticker
matplotlib.use('Qt4Agg')
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style
import tkinter as tk
from PIL import ImageTk, Image
import numpy as np
import load_balance as lb
import codecs

LARGE_FONT = ("Verdana, 12")
NORMAL_FONT = ("TimesNewRoman, 10")
SMALL_FONT = ("TimesNewRoman, 8")

style.use("ggplot")
matplotlib.rc('lines', linewidth=1)

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
        helpmenu.add_command(label="О программе",
                             command=lambda: popupmsg('ВКР студентки группы ИКПИ-42\n'
                                                      'Лебедевой Марии Сергеевны\n'
                                                      '2018 г.'))

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
        self.label = tk.Label(self, text='Выберите количество серверов:', width=110, pady=40, font=LARGE_FONT)
        self.label.grid(row=0, column=0)

        self.buttons = tk.Frame(self)
        self.buttons.grid(row=1, column=0)

        self.img1 = ImageTk.PhotoImage(Image.open("img/N3.JPG"))
        self.topology = tk.Label(self.buttons, image=self.img1)
        self.topology.grid(row=0, column=0, sticky=tk.N, padx=7)
        self.button1 = tk.Button(self.buttons, text='3 сервера',
                                  command=lambda: controller.show_frame(ThreeServerWindow))
        self.button1.grid(row=1, column=0, padx=10, pady=10)

        self.img2 = ImageTk.PhotoImage(Image.open("img/N4.JPG"))
        self.topology = tk.Label(self.buttons, image=self.img2)
        self.topology.grid(row=0, column=1, sticky=tk.N, padx=7)
        self.button2 = tk.Button(self.buttons, text='4 сервера',
                                 command=lambda: controller.show_frame(FourServerWindow))
        self.button2.grid(row=1, column=1, padx=10, pady=10)

        self.img3 = ImageTk.PhotoImage(Image.open("img/N5.JPG"))
        self.topology = tk.Label(self.buttons, image=self.img3)
        self.topology.grid(row=0, column=2, sticky=tk.N, padx=7)
        self.button3 = tk.Button(self.buttons, text='5 серверов',
                                 command=lambda: controller.show_frame(FiveServerWindow))
        self.button3.grid(row=1, column=2, padx=10, pady=10)


class ThreeServerWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.img = ImageTk.PhotoImage(Image.open("img/N3.JPG"))
        self.topology = tk.Label(self, image=self.img)
        self.topology.grid(row=0, column=0, sticky=tk.N, padx=7)

        self.label = tk.Label(self, text='Количество серверов: 3',
                              font=LARGE_FONT)
        self.label.grid(row=1, column=0)

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

        self.buttons = tk.Frame(self)
        self.buttons.grid(row=3, column=0)
        self.button1 = tk.Button(self.buttons, text='Старт',
                                 command=lambda: ThreeServerWindow.start(self))
        self.button1.grid(row=0, column=0, pady=7)
        self.button2 = tk.Button(self.buttons, text='Назад',
                                 command=lambda: controller.show_frame(StartPage))
        self.button2.grid(row=0, column=1, pady=7)

        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)

        formatter = matplotlib.ticker.NullFormatter()
        self.ax1.xaxis.set_major_formatter(formatter)
        self.ax2.xaxis.set_major_formatter(formatter)
        self.ax3.xaxis.set_major_formatter(formatter)

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=5,sticky=tk.N+tk.E)

    def start(self):
        self.N = 3
        self.u = np.array([0] * self.N)
        self.u_max = np.array([7000, 5000, 3000])
        self.time = np.array([400, 350, 200])
        self.X = np.array([[1, 0, 0, 0, 1],
                           [0, 1, 1, 0, 1],
                           [1, 0, 1, 1, 0]])

        LB = lb.LoadBalance(self.u, self.u_max, self.X, self.time, self.N)
        LB.distribution(LB.u, LB.u_max, LB.X, LB.time, LB.N)

        ThreeServerWindow.build_graph(self, self.fig, self.ax1, self.ax2, self.ax3, self.canvas, self.u_max)

        try:
            pullData = open("txt/buf.txt", "r").read()
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

    def build_graph(self, fig, ax1, ax2, ax3, canvas, u_max):
        try:
            file = open("txt/N1.txt", "r").read()
            ThreeServerWindow.draw_graph(self, ax1, u_max[0], file)
            ax1.set_ylabel('N1', fontsize=12)
            file = open("txt/N2.txt", "r").read()
            ThreeServerWindow.draw_graph(self, ax2, u_max[1], file)
            ax2.set_ylabel('N2', fontsize=12)
            file = open("txt/N3.txt", "r").read()
            ThreeServerWindow.draw_graph(self, ax3, u_max[2], file)
            ax3.set_ylabel('N3', fontsize=12)

            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=1, rowspan=5, sticky=tk.N+tk.E)

        except IOError:
            print("An IOError has occurred!")

    def draw_graph(self, ax, u_max, file):
        xList = []
        yList = []

        ax_list = file.split('\n')

        for eachLine in ax_list:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                xList.append(int(x))
                yList.append(int(y))

        ax.plot(xList, yList, "#00A3E0", u_max, "r-", label="max_CPU")


class FourServerWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.img = ImageTk.PhotoImage(Image.open("img/N4.JPG"))
        self.topology = tk.Label(self, image=self.img)
        self.topology.grid(row=0, column=0, sticky=tk.N, padx=7)

        self.label = tk.Label(self, text='Количество серверов: 4',
                              font=LARGE_FONT)
        self.label.grid(row=1, column=0)

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

        self.buttons = tk.Frame(self)
        self.buttons.grid(row=3, column=0)
        self.button1 = tk.Button(self.buttons, text='Старт',
                                 command=lambda: FourServerWindow.start(self))
        self.button1.grid(row=0, column=0, pady=7)
        self.button2 = tk.Button(self.buttons, text='Назад',
                                 command=lambda: controller.show_frame(StartPage))
        self.button2.grid(row=0, column=1, pady=7)

        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(411)
        self.ax2 = self.fig.add_subplot(412)
        self.ax3 = self.fig.add_subplot(413)
        self.ax4 = self.fig.add_subplot(414)

        formatter = matplotlib.ticker.NullFormatter()
        self.ax1.xaxis.set_major_formatter(formatter)
        self.ax2.xaxis.set_major_formatter(formatter)
        self.ax3.xaxis.set_major_formatter(formatter)
        self.ax4.xaxis.set_major_formatter(formatter)

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=5, sticky=tk.N+tk.E)

    def start(self):
        self.N = 4
        self.u = np.array([0] * self.N)
        self.u_max = np.array([4000, 4000, 4000, 4000])
        self.time = np.array([200, 200, 200, 200])
        self.X = np.array([[1, 0, 0, 0, 1],
                           [0, 1, 0, 0, 1],
                           [0, 0, 1, 0, 1],
                           [0, 0, 0, 1, 1]])

        LB = lb.LoadBalance(self.u, self.u_max, self.X, self.time, self.N)
        LB.distribution(LB.u, LB.u_max, LB.X, LB.time, LB.N)

        FourServerWindow.build_graph(self, self.fig, self.ax1, self.ax2, self.ax3, self.ax4, self.canvas, self.u_max)

        try:
            pullData = open("txt/buf.txt", "r").read()
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

    def build_graph(self, fig, ax1, ax2, ax3, ax4, canvas, u_max):
        try:
            file = open("txt/N1.txt", "r").read()
            FourServerWindow.draw_graph(self, ax1, u_max[0], file)
            ax1.set_ylabel('N1', fontsize=12)
            file = open("txt/N2.txt", "r").read()
            FourServerWindow.draw_graph(self, ax2, u_max[1], file)
            ax2.set_ylabel('N2', fontsize=12)
            file = open("txt/N3.txt", "r").read()
            FourServerWindow.draw_graph(self, ax3, u_max[2], file)
            ax3.set_ylabel('N3', fontsize=12)
            file = open("txt/N4.txt", "r").read()
            FourServerWindow.draw_graph(self, ax4, u_max[3], file)
            ax4.set_ylabel('N4', fontsize=12)

            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=1, rowspan=5, sticky=tk.N+tk.E)

        except IOError:
            print("An IOError has occurred!")

    def draw_graph(self, ax, u_max, file):
        xList = []
        yList = []

        ax_list = file.split('\n')

        for eachLine in ax_list:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                xList.append(int(x))
                yList.append(int(y))

        ax.plot(xList, yList, "#00A3E0", u_max, "r-", label="max_CPU")


class FiveServerWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.img = ImageTk.PhotoImage(Image.open("img/N5.JPG"))
        self.topology = tk.Label(self, image=self.img)
        self.topology.grid(row=0, column=0, sticky=tk.N, padx=7)

        self.label = tk.Label(self, text='Количество серверов: 5',
                              font=LARGE_FONT)
        self.label.grid(row=1, column=0)

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

        self.buttons = tk.Frame(self)
        self.buttons.grid(row=3, column=0)
        self.button1 = tk.Button(self.buttons, text='Старт',
                                 command=lambda: FiveServerWindow.start(self))
        self.button1.grid(row=0, column=0, pady=7)
        self.button2 = tk.Button(self.buttons, text='Назад',
                                 command=lambda: controller.show_frame(StartPage))
        self.button2.grid(row=0, column=1, pady=7)

        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(511)
        self.ax2 = self.fig.add_subplot(512)
        self.ax3 = self.fig.add_subplot(513)
        self.ax4 = self.fig.add_subplot(514)
        self.ax5 = self.fig.add_subplot(515)

        formatter = matplotlib.ticker.NullFormatter()
        self.ax1.xaxis.set_major_formatter(formatter)
        self.ax2.xaxis.set_major_formatter(formatter)
        self.ax3.xaxis.set_major_formatter(formatter)
        self.ax4.xaxis.set_major_formatter(formatter)
        self.ax5.xaxis.set_major_formatter(formatter)

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=5, sticky=tk.N+tk.E)

    def start(self):
        self.N = 5
        self.u = np.array([0] * self.N)
        self.u_max = np.array([4000, 4000, 4000, 4000, 4000])
        self.time = np.array([200, 200, 200, 200, 200])
        self.X = np.array([[1, 0, 0, 0, 0],
                           [0, 1, 0, 0, 0],
                           [0, 0, 1, 0, 0],
                           [0, 0, 0, 1, 0],
                           [0, 0, 0, 0, 1]])

        LB = lb.LoadBalance(self.u, self.u_max, self.X, self.time, self.N)
        LB.distribution(LB.u, LB.u_max, LB.X, LB.time, LB.N)

        FiveServerWindow.build_graph(self, self.fig, self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.canvas, self.u_max)

        try:
            pullData = open("txt/buf.txt", "r").read()
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

    def build_graph(self, fig, ax1, ax2, ax3, ax4, ax5, canvas, u_max):
        try:
            file = open("txt/N1.txt", "r").read()
            FiveServerWindow.draw_graph(self, ax1, u_max[0], file)
            ax1.set_ylabel('N1', fontsize=12)
            file = open("txt/N2.txt", "r").read()
            FiveServerWindow.draw_graph(self, ax2, u_max[1], file)
            ax2.set_ylabel('N2', fontsize=12)
            file = open("txt/N3.txt", "r").read()
            FiveServerWindow.draw_graph(self, ax3, u_max[2], file)
            ax3.set_ylabel('N3', fontsize=12)
            file = open("txt/N4.txt", "r").read()
            FiveServerWindow.draw_graph(self, ax4, u_max[3], file)
            ax4.set_ylabel('N4', fontsize=12)
            file = open("txt/N5.txt", "r").read()
            FiveServerWindow.draw_graph(self, ax5, u_max[4], file)
            ax5.set_ylabel('N5', fontsize=12)

            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=1, rowspan=5, sticky=tk.N+tk.E)

        except IOError:
            print("An IOError has occurred!")

    def draw_graph(self, ax, u_max, file):
        xList = []
        yList = []

        ax_list = file.split('\n')

        for eachLine in ax_list:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                xList.append(int(x))
                yList.append(int(y))

        ax.plot(xList, yList, "#00A3E0", u_max, "r-", label="max_CPU")


def check_files():
    try:
        file = codecs.open("txt/buf.txt", "w", "utf-8")
        file.close()
        file = codecs.open("txt/N1.txt", "w", "utf-8")
        file.close()
        file = codecs.open("txt/N2.txt", "w", "utf-8")
        file.close()
        file = codecs.open("txt/N3.txt", "w", "utf-8")
        file.close()
        file = codecs.open("txt/N4.txt", "w", "utf-8")
        file.close()
        file = codecs.open("txt/N5.txt", "w", "utf-8")
        file.close()
    except IOError:
        print("An IOError has occurred!")

def main():
    check_files()

    app = LoadBalance()
    app.mainloop()


if __name__ == '__main__':
    main()
