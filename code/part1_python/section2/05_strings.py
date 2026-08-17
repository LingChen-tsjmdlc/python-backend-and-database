"""字符串操作，对应笔记 2.6。"""

# 拼接
first = "小"
last = "明"
print(first + last)

# 数字要先转成字符串才能拼接
age = 18
print("年龄：" + str(age))

# 索引与切片（索引从 0 开始）
s = "Python"
print(s[0])      # P
print(s[-1])     # n
print(s[0:3])    # Pyt
print(s[2:])     # thon

# 常用方法
print("abc".upper())            # ABC
print(" hi ".strip())           # hi
print("a-b".replace("-", "_"))  # a_b
print(len("abc"))               # 3

# f-string：推荐的格式化方式
name = "小明"
print(f"我叫{name}，今年{age}岁")
print(f"总价是 {5 * 3} 元")

# 转义字符
print("第一行\n第二行")
print("姓名\t年龄")
