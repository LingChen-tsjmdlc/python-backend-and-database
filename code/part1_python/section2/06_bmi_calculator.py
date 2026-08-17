"""实战：BMI 计算器，对应笔记 2.8。

BMI = 体重(kg) / 身高(m) 的平方。
综合用到：input 输入、float 类型转换、幂运算、除法、round 取近似、f-string 输出。
"""

height = float(input("请输入身高（米），例如 1.75："))
weight = float(input("请输入体重（公斤），例如 65："))

bmi = weight / (height ** 2)
bmi = round(bmi, 1)

print(f"你的 BMI 是 {bmi}")
