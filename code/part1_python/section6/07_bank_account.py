"""实战：银行账户系统，对应笔记 6.9。"""


class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance        # 内部数据：约定外面别直接碰

    @property
    def balance(self):
        return self._balance           # 查余额走这里（只读，不给写入口）

    def deposit(self, amount):
        if amount <= 0:
            print("存款金额必须大于 0")
            return
        self._balance += amount
        print(f"存入 {amount} 元，余额 {self._balance} 元")

    def withdraw(self, amount):
        if amount > self._balance:
            print(f"余额不足：当前余额 {self._balance} 元")
            return
        self._balance -= amount
        print(f"取出 {amount} 元，余额 {self._balance} 元")

    def __str__(self):
        return f"账户({self.owner}，余额{self._balance}元)"


class CreditAccount(Account):
    def withdraw(self, amount):
        # 重写：信用卡允许透支 5000
        if amount > self.balance + 5000:
            print("超出透支额度")
            return
        self._balance -= amount        # 子类属于"内部"，按约定可以用 _balance
        print(f"取出 {amount} 元，余额 {self._balance} 元")


acc = Account("小明", 1000)
print(acc)                # 账户(小明，余额1000元)
acc.deposit(500)          # 存入 500 元，余额 1500 元
acc.withdraw(2000)        # 余额不足：当前余额 1500 元
acc.withdraw(300)         # 取出 300 元，余额 1200 元
print(acc.balance)        # 1200
# acc.balance = 0         # 取消注释会报错：只读属性没有写入口

credit = CreditAccount("小红", 1000)
credit.withdraw(3000)     # 取出 3000 元，余额 -2000 元（透支成功）
credit.withdraw(4000)     # 超出透支额度
