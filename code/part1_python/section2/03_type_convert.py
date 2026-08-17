"""类型转换，对应笔记 2.4。"""

# 字符串转整数，才能做数学运算
age_text = "18"
age = int(age_text)
print(age + 1)

# 字符串转浮点数
height = float("1.75")
print(height)

# 数字转字符串，才能和字符串拼接
score = 95
print("成绩：" + str(score))

# 转换失败的情况（取消注释会报错）
# int("abc")     # abc 不是数字
# int("3.14")    # 带小数点的字符串不能直接转 int
