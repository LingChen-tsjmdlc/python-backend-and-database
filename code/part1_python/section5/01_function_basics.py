"""函数的定义与调用、为什么要用函数，对应笔记 5.1。"""

# 不用函数：同一个动作抄三遍
scores1 = [85, 92, 78]
scores2 = [60, 75, 88]
scores3 = [90, 91, 95]

avg1 = sum(scores1) / len(scores1)
print(f"一班的平均分是 {avg1:.1f}")
avg2 = sum(scores2) / len(scores2)
print(f"二班的平均分是 {avg2:.1f}")
avg3 = sum(scores3) / len(scores3)
print(f"三班的平均分是 {avg3:.1f}")

print("----")


# 用函数：写一遍，喊名字用无数次
def report(class_name, scores):
    avg = sum(scores) / len(scores)
    print(f"{class_name}的平均分是 {avg:.1f}")


report("一班", [85, 92, 78])
report("二班", [60, 75, 88])
report("三班", [90, 91, 95])
