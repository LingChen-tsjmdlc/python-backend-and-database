"""多态：同一句话，各自理解，对应笔记 6.6。"""

# 你早就在用多态：len 对各种容器各有各的算法，调用方不关心
print(len([1, 2, 3]))     # 3
print(len("hello"))       # 5
print(len({"a": 1}))      # 1

print("----")


# len() 的秘密：len(x) 实际调用 x.__len__()。自己实现 __len__，len 就认识我们的类
class Basket:
    def __init__(self):
        self.items = []

    def put(self, item):
        self.items.append(item)

    def __len__(self):               # 告诉 len()：我的"长度"这么算
        return len(self.items)


class Team:
    def __init__(self, members):
        self.members = members

    def __len__(self):               # 同名方法，各自的算法
        return len(self.members)


b = Basket()
b.put("苹果")
b.put("香蕉")
t = Team(["小明", "小红", "小刚"])

print(len(b))     # 2：len(b) 实际调的是 b.__len__()
print(len(t))     # 3：len(t) 实际调的是 t.__len__()

print("----")


class Dog:
    def speak(self):
        print("汪汪")


class Cat:
    def speak(self):
        print("喵喵")


class Duck:
    def speak(self):
        print("嘎嘎")


animals = [Dog(), Cat(), Duck(), Dog()]
for a in animals:
    a.speak()     # 同一句代码，各叫各的；新增 Duck 时这行循环没动过
