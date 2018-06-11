#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
np.set_printoptions(threshold=np.nan)
import codecs

import window as w

M = 5


class LoadBalance:
    def __init__(self, u, u_max, X, time, N):
        self.N = N
        self.u = u
        self.u_max = u_max
        self.X = X
        self.time = time

        global M

    def lam(self, k, d):
        return k / d

    def flaw(self, g, n, present_lam, past_lam):
        b = (g / n) * (1 + (present_lam - past_lam) / past_lam)

        if b == 0:
            b = 0.1
        if b > 1:
            b = 1

        return b

    def dist(self, d, b, past_b):
        return past_b * d / b

    def distribution(self, u, u_max, X, time, N):
        k = 1
        d = 300
        n = 3
        q = 0
        q_max = 1000
        q_types = []
        lost = 0
        past_request = 0
        past_b = 0
        past_u = np.array([0] * N)
        forecast = np.array([0] * N)

        while k < 100:
            g = 0
            arr = 0
            Arr = np.array([0] * n)
            requests = random.randint(100, 1000)

            # Распределение запросов (с учетом типа)
            for i in range(requests):
                array_of_types = random.randint(0, 4)
                buf = [row[array_of_types] for row in X]
                min_N = np.argmax(buf)
                min_u = u[min_N]

                for element in buf:
                    if (buf[element] == 1) and (u[element] < min_u):
                        min_u = u[element]
                        min_N = element

                if u_max[min_N] < u[min_N] + 1:
                    if q_max > q:
                        q += 1
                        q_types.append(array_of_types)
                    else:
                        lost += 1
                else:
                    u[min_N] += 1

            # Обработка запросов
            for i in range(N):
                u[i] -= random.randint(0, time[i])
                if u[i] < 0:
                    u[i] = 0

            # Обработка очереди
            if q > 1:
                for request in q_types:
                    type = q_types[request]
                    buf = [row[type] for row in X]
                    min_N = np.argmax(buf)
                    min_u = u[min_N]

                    for element in buf:
                        if (buf[element] == 1) and (u[element] < min_u):
                            min_u = u[element]
                            min_N = element

                    if u_max[min_N] > u[min_N] + 1:
                        u[min_N] += 1
                        q -= 1
                        q_types.remove(type)

            # Подсчет прогнозируемой величины
            forecast = u + past_u

            # Сбор статистики
            present_lam = LoadBalance.lam(self, requests, d)
            if k == 1:
                past_lam = LoadBalance.lam(self, random.randint(100, 1000), d)
                past_b = random.uniform(0.1, 1)
            else:
                past_lam = LoadBalance.lam(self, past_request, d)

            buf = requests
            for i in range(n):
                Arr[i] = random.randint(0, buf)
                buf -= Arr[i]

            for i in range(n):
                lam_h = LoadBalance.lam(self, Arr[i], d / n)
                if lam_h > present_lam:
                    arr += 1
                    g += 1

            b = LoadBalance.flaw(self, g, n, present_lam, past_lam)
            d = LoadBalance.dist(self, d, b, past_b)

            try:
                file = codecs.open("N1.txt", "a", "utf-8")
                file.write("%s" % k)
                file.write(",%s" % u[0])
                file.write("\n")
                file.close()
                file = codecs.open("N2.txt", "a", "utf-8")
                file.write("%s" % k)
                file.write(",%s" % u[1])
                file.write("\n")
                file.close()
                file = codecs.open("N3.txt", "a", "utf-8")
                file.write("%s" % k)
                file.write(",%s" % u[2])
                file.write("\n")
                file.close()

                if N == 4:
                    file = codecs.open("N4.txt", "a", "utf-8")
                    file.write(" %s" % k)
                    file.write(",%s" % u[3])
                    file.write("\n")
                    file.close()

                if N == 5:
                    file = codecs.open("N5.txt", "a", "utf-8")
                    file.write(" %s" % k)
                    file.write(",%s" % u[4])
                    file.write("\n")
                    file.close()

            except IOError:
                print("An IOError has occurred!")

            past_b = b
            past_request = requests
            past_u = u
            k += 1

        try:
            file = codecs.open("buf.txt", "w", "utf-8")

            for element in u:
                file.write("%s " % element)

            file.write("\n")

            for element in forecast:
                file.write("%s " % element)

            file.write("\n%s" % q)
            file.write("\n%s" % lost)

            file.close()
        except IOError:
            print("An IOError has occurred!")
