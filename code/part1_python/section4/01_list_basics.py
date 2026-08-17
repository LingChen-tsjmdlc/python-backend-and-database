"""列表的创建、索引切片、增删改查，对应笔记 4.2.1 / 4.2.2。"""

scores = [85, 92, 78, 90]
print(scores[0])     # 85
print(scores[-1])    # 90
print(scores[1:3])   # [92, 78]
print(len(scores))   # 4

fruits = ["苹果", "香蕉", "橙子"]

fruits.append("西瓜")        # 加到末尾
fruits.insert(1, "葡萄")     # 插到索引 1
fruits[0] = "梨"             # 改
fruits.remove("香蕉")        # 按内容删
last = fruits.pop()          # 删最后一个并取出

print(fruits)                # ['梨', '葡萄', '橙子']
print(last)                  # 西瓜
print("葡萄" in fruits)      # True
print(fruits.index("葡萄"))  # 1
