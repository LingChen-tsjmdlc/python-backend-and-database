"""类与对象、__init__、self，对应笔记 6.2。"""


class Student:
    def __init__(self, name, score):
        self.name = name       # 把传进来的值装到这个对象身上
        self.score = score

    def introduce(self):
        print(f"我是{self.name}，考了{self.score}分")


# 类是图纸，类名() 造对象，每个对象独立
s1 = Student("小明", 85)
s2 = Student("小红", 92)

print(s1.name, s1.score)     # 小明 85
print(s2.name, s2.score)     # 小红 92

# self：调用时 Python 自动把对象自己填进去
s1.introduce()     # 我是小明，考了85分（这里 self 就是 s1）
s2.introduce()     # 我是小红，考了92分（这里 self 就是 s2）
