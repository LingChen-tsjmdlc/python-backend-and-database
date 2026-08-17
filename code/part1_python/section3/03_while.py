"""while 循环，对应笔记 3.3。

只要条件成立就一直执行，适合"不知道循环几次"的场景。
"""

count = 1
while count <= 5:
    print(f"第 {count} 次")
    count += 1     # 更新条件变量，否则会死循环
