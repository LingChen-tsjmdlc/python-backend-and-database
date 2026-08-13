"""四种基本数据类型 + 特殊值 None / NaN，对应笔记 2.3。"""

import math

age = 18            # int 整数
height = 1.75       # float 浮点数
name = "小明"        # str 字符串
is_student = True   # bool 布尔值

# type() 查看数据类型
print(type(age))
print(type(height))
print(type(name))
print(type(is_student))

# 特殊值 None：表示"空 / 什么都没有"，类型是 NoneType
answer = None
print(answer)            # None
print(type(answer))      # <class 'NoneType'>
print(answer is None)    # True

# 特殊值 NaN：表示"非数字"，类型仍是 float
x = float("nan")
print(x)                 # nan
print(type(x))           # <class 'float'>
print(x == x)            # False：NaN 不等于任何值，连自己都不等
print(math.isnan(x))     # True：判断是不是 NaN 要用 math.isnan
