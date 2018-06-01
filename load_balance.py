#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import numpy as np

N = 5
M = 5


class LoadBalance:
    def __init__(self, u, u_max, X, time):
        self.u = u
        self.u_max = u.max
        self.X = X
        self.time = time

        global N
        global M

    def lam(self, k, d):
        return k / d

    def flaw(self, g, n, present_lam, past_lam):
        return (g / n) * (1 + (present_lam - past_lam) / past_lam)

    def dist(self, d, b, past_b):
        return past_b * d / b

    def distribution(self, u, u_max, X, time):
        k = 1  # k - шаг
        d = 300
        n = 3
        past_request = 0
        Arr = np.array([0] * n)
        arr = 0
        past_b = 0
        # X = np.zeros((N, M))

        while k < 1000:
            print("d", d)
            g = 0
            requests = random.randint(100, 1000)
            array_of_types = np.array([0] * M)

            for i in range(requests):
                request_type = random.randint(0, 4)
                array_of_types[request_type] += 1

            max_n = np.argmax(array_of_types)
            # max = np.max(array_of_types)

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
            # Ограничение пачечности (0, 1]
            if b == 0:
                b = 0.1
            if b > 1:
                b = 1

            print('b', b, '\npast_b', past_b, '\n')

            d = LoadBalance.dist(self, d, b, past_b)

            if b > past_b:
                # Уменьшаем d(k)
                d -= 1
            else:
                if b < past_b:
                    # Увеличиваем d(k)
                    d += 1
                else:
                    d = d

            past_b = b
            past_request = requests

            # Распределение по типам
            # for i in range(N):
            #     for j in range(M):
            #         if max_n == j:
            #             if X[i][j] == 1:
            #                 u[i] += d
            #                 print('Загруженность серверов', u)

            u[np.argmin(u)] += requests

            # Обработка запросов
            for i in range(N):
                u[i] -= random.randint(0, time[i])
                if u[i] < 0:
                    u[i] = 0

            # Сделать очередь и переменную для потерянных запросов

            print('Загруженность серверов', u)

            k += 1
