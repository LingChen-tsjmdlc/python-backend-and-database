"""break 与 continue，对应笔记 3.4。"""

# break：立刻结束整个循环
for i in range(1, 10):
    if i == 5:
        break
    print(i)             # 1 2 3 4

# continue：跳过本次，进入下一次
for i in range(1, 10):
    if i % 2 == 0:
        continue         # 偶数跳过
    print(i)             # 1 3 5 7 9

# while True + break：一直循环，满足条件主动退出
count = 0
while True:
    count += 1
    if count >= 3:
        break
print(f"循环了 {count} 次后退出")
