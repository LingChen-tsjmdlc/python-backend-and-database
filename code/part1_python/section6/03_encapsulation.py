"""封装：_x / __x / @property，对应笔记 6.5。"""


class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance    # 双下划线：被改名藏深，外面访问不到

    def deposit(self, amount):
        self.__balance += amount    # 类内部自己可以用

    def get_balance(self):
        return self.__balance       # 想看？走这个入口


acc = Account("小明", 1000)
acc.deposit(500)
print(acc.get_balance())     # 1500
# print(acc.__balance)       # 取消注释会报错：AttributeError

print("----")


class Account2:
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance

    @property
    def balance(self):
        return self.__balance        # 读 acc.balance 时实际执行这里


acc2 = Account2("小红", 500)
print(acc2.balance)          # 500：像属性一样读，没括号
# acc2.balance = -1          # 取消注释会报错：没有写入口，改不了
