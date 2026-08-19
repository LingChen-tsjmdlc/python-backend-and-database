"""继承、super() 与方法重写，对应笔记 6.6。"""


class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            print("余额不足")
            return
        self.balance -= amount


# 继承：子类自动拥有父类的一切
class CreditAccount(Account):
    def withdraw(self, amount):
        # 重写：信用卡允许透支 5000
        if amount > self.balance + 5000:
            print("超出透支额度")
            return
        self.balance -= amount


acc = CreditAccount("小明", 1000)
acc.deposit(500)          # 没写 deposit，用父类的
acc.withdraw(3000)        # 用子类重写的版本：透支成功
print(acc.balance)        # -1500


# super()：在父类基础上加点东西，而不是完全盖掉
class VIPAccount(Account):
    def __init__(self, owner, balance, level):
        super().__init__(owner, balance)     # 父类的出厂设置先做完
        self.level = level                   # 再加 VIP 特有的


vip = VIPAccount("小红", 2000, "黄金")
print(vip.owner, vip.balance, vip.level)     # 小红 2000 黄金
