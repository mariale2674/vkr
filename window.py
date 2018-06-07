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

import load_balance as lb

# import random

# import pandas as pd
import numpy as np

LARGE_FONT = ("Verdana, 12")
NORMAL_FONT = ("TimesNewRoman, 10")
SMALL_FONT = ("TimesNewRoman, 8")
style.use("ggplot")

N = 5
M = 5

fig = Figure()
a = fig.add_subplot(111)

# Всплывающие сообщения
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
    # finally:
    #     pullData.close()  # Узнать, почему не работает и надо ли вообще


class LoadBalance(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, 'Система мониторинга загруженности серверов')

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Меню
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

        # exchangeChoice = tk.Menu(menu, tearoff=1)
        # exchangeChoice.add_command(label="3 сервера",
        #                            command = lambda: changeExchange())

        helpmenu = tk.Menu(menu, tearoff=0)
        helpmenu.add_command(label='Помощь',
                             command = lambda: popupmsg('Никто Вам не поможет.\n'
                                                                       'Запуск программы осуществляется под Вашу ответственность.\n'
                                                                       'Студентка группы ИКПИ-42 Лебедева Мария\n'
                                                                       'Не несет ответственности за любые неполадки.\n'
                                                                       'Спасибо за внимание.'))
        helpmenu.add_command(label="О программе")

        menu.add_cascade(label="Файл", menu=filemenu)
        menu.add_cascade(label="Действия", menu=editmenu)
        menu.add_cascade(label="Справка", menu=helpmenu)

        tk.Tk.config(self, menu=menu)

        self.frames = {}

        for F in (StartPage, ThreeServerWindow):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.label = tk.Label(self, text='Выберите количество серверов:', width=50, height=5, font=LARGE_FONT)
        self.label.grid(row=0)

        self.button1 = tk.Button(self, text='3 сервера',
                                  command=lambda: controller.show_frame(ThreeServerWindow))
        self.button1.grid(row=0, column=1)

        self.button2 = tk.Button(self, text='4 сервера',
                                 command=lambda: controller.show_frame(ThreeServerWindow))
        self.button2.grid(row=0, column=2)

        self.button3 = tk.Button(self, text='5 серверов',
                                 command=lambda: controller.show_frame(ThreeServerWindow))
        self.button3.grid(row=0, column=3)


class ThreeServerWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.label = tk.Label(self, text='Загруженность сети', font=LARGE_FONT)
        self.label.grid(row=0, column=0, columnspan=2)

        self.img = ImageTk.PhotoImage(Image.open("img/N3.jpg"))
        self.topology = tk.Label(self, image=self.img)
        self.topology.grid(row=1, column=0)

        self.info = tk.Label(self, text='Какая-нибудь информация', width=50, height=5)
        self.info.grid(row=2, column=0)

        # self.graph = tk.Label(self, text=g.show())
        # self.graph.pack()

        self.button1 = tk.Button(self, text='Назад',
                                 command=lambda: controller.show_frame(StartPage))
        self.button1.grid(row=3, column=0, pady=7)

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, rowspan=3)

        # Панель навигации больше не работает, исправить, если будет время
        # toolbar = NavigationToolbar2TkAgg(canvas, self)
        # toolbar.update()
        # canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


def main():
    app = LoadBalance()
    app.geometry("1000x500")
    # load_balance() # Запускаем функцию балансировки
    # Создать алгоритм балансировки и подсчитать оптимальный интервал считывания.
    # Записывать все данные в файл.
    # Раз в этот интервал запускать функцию ani и считывать данные из файла.
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    app.mainloop()


if __name__ == '__main__':
    main()
    # N = 5
    # M = 5
    u = np.array([0] * N)
    u_max = np.array([0] * N)
    time = np.array([0] * N)
    X = np.array([N, M])

    if N == 3:

        time = np.array([100, 200, 300])
        X = np.array([[1, 0, 0, 0, 0],
                      [0, 1, 0, 0, 1],
                      [1, 0, 1, 1, 0]])
    else:
        if N == 4:

            time = np.array([100, 150, 200, 300])
            X = np.array([[1, 0, 0, 0, 1],
                 [0, 1, 0, 0, 0],
                 [0, 0, 1, 0, 0],
                 [0, 0, 0, 1, 0]])
        else:
            if N == 5:
                u_max = np.array([1000, 2000, 3000, 4000, 5000])
                time = np.array([300, 200, 200, 300, 400])
                X = np.array([[1, 0, 0, 0, 0],
                              [0, 1, 0, 0, 0],
                              [0, 0, 1, 0, 0],
                              [0, 1, 1, 1, 0],
                              [1, 1, 0, 1, 1]])
            else:
                print('Некорректное число серверов.')

    LB = lb.LoadBalance(u, u_max, X, time)
    LB.distribution(LB.u, LB.u_max, LB.X, LB.time)
