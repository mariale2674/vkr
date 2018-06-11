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
import random

LARGE_FONT = ("Verdana, 12")
NORMAL_FONT = ("TimesNewRoman, 10")
SMALL_FONT = ("TimesNewRoman, 8")

style.use("ggplot")

# N = 3
M = 5

fig = Figure()
a = fig.add_subplot(111)


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

def animate(i):
    try:
        pullData = open("data.txt", "r").read()
        dataList = pullData.split('\n')
        xList = []
        yList = []

        for eachLine in dataList:
            if len(eachLine) > 1:
                x, y = eachLine.split(',')
                xList.append(int(x))
                yList.append(int(y))

        a.clear()

        a.plot(xList, yList, "black", label='CPU')
        a.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3, ncol=2, borderaxespad=0)

        title = "Сервер N1"
        a.set_title(title)
    except IOError:
        print("An IOError has occurred!")


class LoadBalance(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, 'Система мониторинга загруженности серверов')

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menu = tk.Menu(container)
        filemenu = tk.Menu(menu, tearoff=0)
        filemenu.add_command(label="Новый")
        filemenu.add_command(label="Открыть")
        filemenu.add_command(label="Сохранить")
        filemenu.add_command(label="Сохранить как...")
        filemenu.add_command(label="Выход", command=lambda: container.quit())

        editmenu = tk.Menu(menu, tearoff=0)
        editmenu.add_command(label="Вырезать")
        editmenu.add_command(label="Копировать")
        editmenu.add_command(label="Вставить")
        editmenu.add_command(label="Удалить")
        editmenu.add_command(label="Выбрать все")

        helpmenu = tk.Menu(menu, tearoff=0)
        helpmenu.add_command(label='Помощь',
                             command = lambda: popupmsg('Никто вам не поможет.\n'))
        helpmenu.add_command(label="О программе")

        menu.add_cascade(label="Файл", menu=filemenu)
        menu.add_cascade(label="Действия", menu=editmenu)
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
        self.label.grid(row=0, column=0)

        # self.entry = tk.Entry(self)
        # self.N = int(self.entry.get())
        # self.entry.grid(row=1, column=0)

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
        self.label = tk.Label(self, text='Загруженность сети', font=LARGE_FONT)
        self.label.grid(row=0, column=0, columnspan=3)

        self.img = ImageTk.PhotoImage(Image.open("img/N3.jpg"))
        self.topology = tk.Label(self, image=self.img)
        self.topology.grid(row=1, column=0, columnspan=2)

        self.info = tk.Label(self, text='Информация:\n', width=50, height=5)
        self.info.grid(row=2, column=0, columnspan=2)

        self.button1 = tk.Button(self, text='Старт',
                                 command=lambda: ThreeServerWindow.start(self))
        self.button1.grid(row=3, column=0, pady=7)
        self.button2 = tk.Button(self, text='Назад',
                                 command=lambda: controller.show_frame(StartPage))
        self.button2.grid(row=3, column=1, pady=7)

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=2, rowspan=3)

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


class FourServerWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text='Загруженность сети', font=LARGE_FONT)
        self.label.grid(row=0, column=0, columnspan=2)

        self.button1 = tk.Button(self, text='Назад',
                                 command=lambda: controller.show_frame(StartPage))
        self.button1.grid()

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
        self.label.grid(row=0, column=0, columnspan=2)

        self.button1 = tk.Button(self, text='Назад',
                                 command=lambda: controller.show_frame(StartPage))
        self.button1.grid()

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


def main():
    app = LoadBalance()
    app.geometry("1000x500")
    ani = animation.FuncAnimation(fig, animate, interval=10)
    app.mainloop()


if __name__ == '__main__':
    main()
