"""字典的创建、操作、get、遍历、推导式，对应笔记 4.3。"""

student = {"name": "小明", "age": 18, "city": "深圳"}
print(student["name"])     # 小明

# 增 / 改
student["city"] = "广州"     # 键存在 → 修改
student["phone"] = "138"     # 键不存在 → 新增

# 删
del student["city"]

# 查：get 在键不存在时返回默认值，不报错
print(student.get("name"))           # 小明
print(student.get("email"))          # None
print(student.get("email", "未知"))  # 未知
print("name" in student)             # True

# items() 交出所有键值对；for 写两个名字分别接住键和值
for key, value in student.items():
    print(f"{key}: {value}")

# 字典推导式
scores = {"小明": 85, "小红": 92, "小刚": 78}
passed = {n: s for n, s in scores.items() if s >= 80}
print(passed)                # {'小明': 85, '小红': 92}
