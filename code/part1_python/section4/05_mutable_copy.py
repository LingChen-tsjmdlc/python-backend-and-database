"""可变 vs 不可变、引用机制、浅拷贝 / 深拷贝，对应笔记 4.5。"""

import copy

# 现象：改 b，a 跟着变
a = [1, 2, 3]
b = a                      # 不复制，b 也指向同一个列表
b.append(4)
print(a)                   # [1, 2, 3, 4]
print(id(a) == id(b))      # True：同一个对象
print(a is b)              # True

# 对照：数字（不可变）没这个问题
a = 100
b = a
b = b + 1                  # 新建对象 101，b 改指向它
print(a)                   # 100：不受影响

# 浅拷贝：只复制最外层
a = [1, 2, 3]
b = a.copy()
b.append(4)
print(a)                   # [1, 2, 3]：外层独立了
print(id(a) == id(b))      # False：两个不同对象

# 浅拷贝的陷阱：内层列表仍共享
a = [[1, 2], [3, 4]]
b = a.copy()
b[0].append(99)
print(a)                   # [[1, 2, 99], [3, 4]]：内层被一起改了

# 深拷贝：连内层一起复制，完全独立
a = [[1, 2], [3, 4]]
b = copy.deepcopy(a)
b[0].append(99)
print(a)                   # [[1, 2], [3, 4]]：不受影响
print(b)                   # [[1, 2, 99], [3, 4]]
