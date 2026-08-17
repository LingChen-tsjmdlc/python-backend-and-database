"""列表遍历与列表推导式，对应笔记 4.2.3 / 4.2.4 / 4.2.5。"""

scores = [85, 92, 78, 90]

# 遍历
for s in scores:
    print(s)

# 带序号遍历
for i, s in enumerate(scores):
    print(f"第 {i + 1} 个：{s}")

# zip：两串数据配成对，成对遍历（长度不一致时多余的被忽略）
names = ["小明", "小红", "小刚", "小丽"]
for name, s in zip(names, scores):
    print(f"{name}：{s} 分")

# 列表推导式：对每个元素加工，生成新列表
doubled = [s * 2 for s in scores]
print(doubled)                  # [170, 184, 156, 180]

# 带条件筛选
high = [s for s in scores if s >= 90]
print(high)                     # [92, 90]

# map / filter：传内置函数，不用自己写函数
print(list(map(str, [1, 2, 3])))        # ['1', '2', '3']：每个元素过一遍 str()

texts = ["85", "92", "78"]
print(list(map(int, texts)))            # [85, 92, 78]：批量把字符串转成数字

items = ["85", "abc", "92", ""]
print(list(filter(None, items)))        # ['85', 'abc', '92']：滤掉空字符串

# map/filter 返回的是迭代器，要 list() 才能看到结果
result = map(str, [1, 2, 3])
print(result)                           # <map object ...>
print(list(result))                     # ['1', '2', '3']
