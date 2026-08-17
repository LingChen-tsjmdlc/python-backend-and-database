"""元组与集合：分别什么时候用，对应笔记 4.4。"""

# 元组：不能改的列表，装固定数据
point = (3, 5)
print(point[0])              # 3
# point[0] = 9               # 报错：元组不能改

# 单元素元组要带逗号
single = (3,)
print(type(single))          # <class 'tuple'>
print(type((3)))             # <class 'int'>（没带逗号只是数字）

# 集合：无序、自动去重
tags = {"python", "sql", "python"}
print(tags)                  # {'python', 'sql'}
print("sql" in tags)         # True

# 常用技巧：给列表去重
nums = [1, 2, 2, 3, 3, 3]
unique = list(set(nums))
print(unique)                # [1, 2, 3]

# 空集合要写 set()，{} 是空字典
print(type(set()))           # <class 'set'>
print(type({}))              # <class 'dict'>
