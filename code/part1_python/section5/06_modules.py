"""模块与 import：random / time / math / os，对应笔记 5.6。"""

import random
from math import sqrt
import time
import os

# random：随机数
print(random.randint(1, 100))
print(random.choice(["苹果", "香蕉", "橙子"]))
cards = [1, 2, 3, 4, 5]
random.shuffle(cards)
print(cards)

# math：数学（from ... import ... 的写法，直接用名字）
print(sqrt(16))

# time：时间
print(time.time())
time.sleep(1)
print("1 秒过去了")

# os：和操作系统打交道
print(os.getcwd())
print(os.listdir("."))
