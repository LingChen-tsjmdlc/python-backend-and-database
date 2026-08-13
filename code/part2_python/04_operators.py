"""各类运算符，对应笔记 2.5。"""

# 算术运算符
print(7 / 2)     # 3.5  普通除法
print(7 // 2)    # 3    整除
print(7 % 2)     # 1    取余
print(2 ** 3)    # 8    幂

# 比较运算符，结果是布尔值
print(3 == 2)    # False
print(3 != 2)    # True

# 逻辑运算符
print(3 > 2 and 5 > 1)   # True
print(3 > 2 or 1 > 5)    # True
print(not 3 > 2)         # False

# 复合赋值
count = 10
count += 5
print(count)     # 15

# 成员与身份运算符
print("a" in "abc")      # True
x = None
print(x is None)         # True
