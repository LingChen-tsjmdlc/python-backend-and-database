"""实战：九九乘法表与打印图形，对应笔记 3.5.2 / 3.5.3。"""

# 九九乘法表：嵌套循环，外层管行、内层管列
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f"{j}×{i}={i * j}", end="\t")
    print()

print()

# 打印三角形
for i in range(1, 6):
    print("*" * i)
