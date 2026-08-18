"""lambda 与高阶函数：sorted(key=...)、重新认识 map / filter，对应笔记 5.4。"""

# lambda：一句话定义的小函数
double = lambda x: x * 2
print(double(5))     # 10


# 等价于：
def double2(x):
    return x * 2


print(double2(5))

print("----")

# sorted 的 key：告诉排序"按什么比"
students = [
    {"name": "小明", "score": 85},
    {"name": "小红", "score": 92},
    {"name": "小刚", "score": 78},
]
ranked = sorted(students, key=lambda s: s["score"], reverse=True)
for s in ranked:
    print(s["name"], s["score"])

print("----")

# map / filter + lambda：规则自己写
scores = [85, 92, 78, 90]
print(list(map(lambda s: s / 10, scores)))       # 换算成 10 分制
print(list(filter(lambda s: s >= 80, scores)))   # 只留下 80 分以上的
