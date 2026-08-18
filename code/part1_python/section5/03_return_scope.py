"""返回值、作用域、闭包入门，对应笔记 5.3。"""


# return：把结果交还给调用处
def average(scores):
    return sum(scores) / len(scores)


avg = average([85, 92, 78])
print(avg + 5)     # 结果可以继续参与运算

# return 多个值（其实是打包成元组）
def min_max(scores):
    return min(scores), max(scores)


lo, hi = min_max([85, 92, 78])
print(lo, hi)

# 不写 return，默认返回 None
def just_print(x):
    print(x)


result = just_print("hello")
print(result)      # None

print("----")


# 作用域：函数内部的局部变量，出了门就不存在
def calc(scores):
    total = sum(scores)     # total 是局部变量
    return total / len(scores)


print(calc([85, 92, 78]))
# print(total)              # 取消注释会报错：NameError

# global：声明"我要改的是外面那个变量"（认识即可，初学不建议用）
count = 0                  # 全局变量


def add_one():
    global count           # 没有这行，下面的赋值只是在新建同名局部变量
    count = count + 1


add_one()
add_one()
print(count)               # 2：外面那个 count 真的被改了

print("----")


# 闭包：函数带走它出生时的环境

# 零件一：函数也是一种值，可以装进变量
def hello():
    print("你好")


f = hello      # 没加括号：不是调用，是把函数赋给 f
f()            # 你好


# 零件二：函数里可以定义函数，里层能读到外层的变量
def outer():
    n = 5

    def add(x):
        return x + n

    print(add(10))


outer()        # 15


# 零件三：把里层函数 return 出来，它"带走"当时的 n
def make_adder(n):
    def add(x):
        return x + n
    return add


add5 = make_adder(5)
add10 = make_adder(10)
print(add5(1))              # 6：这个包裹里 n 是 5
print(add10(1))             # 11：这个包裹里 n 是 10
