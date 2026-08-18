"""常用内置函数与递归入门，对应笔记 5.5。"""

# 常用内置函数
print(abs(-3))                    # 3
print(round(3.14159, 2))          # 3.14
print(max([3, 1, 4]), min([3, 1, 4]))
print(sum([1, 2, 3]))
print(sorted([3, 1, 2]))          # 返回新列表
print(type(3.5))
print(list(range(3)))

# sorted(列表) vs 列表.sort()：一个返回新列表，一个原地改并返回 None
nums = [3, 1, 2]
a = sorted(nums)
print(a, nums)        # [1, 2, 3] [3, 1, 2]
b = nums.sort()
print(b, nums)        # None [1, 2, 3]

print("----")


# 递归：函数调用自己
def countdown(n):
    if n <= 0:              # 基例：结束条件
        print("点火！")
        return
    print(n)
    countdown(n - 1)        # 向基例靠近


countdown(3)
