"""实例属性 vs 类属性、实例方法，对应笔记 6.3。"""


class Student:
    school = "深圳大学"        # 类属性：全类共用一份

    def __init__(self, name, score):
        self.name = name       # 实例属性：每个对象各带各的
        self.score = score

    def is_pass(self):         # 实例方法：用自己的数据判断
        return self.score >= 60


s1 = Student("小明", 85)
s2 = Student("小红", 45)

# 类属性：两个对象、类本身，访问的是同一份
print(s1.school, s2.school, Student.school)

# 实例属性：各自独立
print(s1.name, s2.name)

# 实例方法
print(s1.is_pass(), s2.is_pass())     # True False
