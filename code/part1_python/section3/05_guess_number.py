"""实战：猜数字，对应笔记 3.5.1。

程序随机想一个 1-100 的数字，用户一直猜，每次提示大了/小了，猜对为止。
"""

import random

secret = random.randint(1, 100)

while True:
    guess = int(input("猜一个 1-100 的数字："))
    if guess > secret:
        print("大了，再猜")
    elif guess < secret:
        print("小了，再猜")
    else:
        print("恭喜你，猜对了！")
        break
