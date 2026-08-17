"""for 循环与 range()，对应笔记 3.2。"""

# for：把序列里的东西一个个取出来
for ch in "abc":
    print(ch)

# range(5)：0 到 4
for i in range(5):
    print(i)

# range(1, 6)：1 到 5；range(0, 10, 2)：步长 2
print(list(range(1, 6)))       # [1, 2, 3, 4, 5]
print(list(range(0, 10, 2)))   # [0, 2, 4, 6, 8]

# 循环累加：求 1 到 100 的和
total = 0
for i in range(1, 101):
    total += i
print(total)                   # 5050

# 嵌套循环：外层每转一圈，内层完整转完一轮
for i in range(3):
    for j in range(2):
        print(f"i={i}, j={j}")
