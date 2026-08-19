"""魔术方法：__str__ / __repr__ / __eq__，对应笔记 6.8。"""


class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

    def __str__(self):
        # print(对象) 时自动调用
        return f"账户({self.owner}，余额{self.balance}元)"

    def __repr__(self):
        # 列表里打印、交互式环境敲对象名时自动调用
        return f"Account({self.owner!r}, {self.balance})"

    def __eq__(self, other):
        # == 比较时自动调用：户主相同就算同一个账户
        return self.owner == other.owner


acc = Account("小明", 1000)
print(acc)                                  # 账户(小明，余额1000元)

accounts = [Account("小明", 1000), Account("小红", 500)]
print(accounts)                             # [Account('小明', 1000), Account('小红', 500)]

a = Account("小明", 1000)
b = Account("小明", 9999)
print(a == b)                               # True：规则是自己定的
