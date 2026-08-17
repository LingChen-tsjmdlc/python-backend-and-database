"""条件判断 if / elif / else、match-case，对应笔记 3.1。"""

# if：条件成立才执行
score = 85
if score >= 60:
    print("及格了")

# if-else：二选一
score = 45
if score >= 60:
    print("及格了")
else:
    print("不及格，要补考")

# if-elif-else：多分支，从上到下第一个成立就执行
score = 85
if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("不及格")

# if 嵌套：外层成立再判内层（别超过两三层）
age = 20
has_ticket = True
if age >= 18:
    if has_ticket:
        print("可以入场")
    else:
        print("请先买票")
else:
    print("未满 18 岁，不能入场")

# match-case（Python 3.10+）：按具体值匹配的多分支
choice = "2"
match choice:
    case "1":
        print("添加")
    case "2":
        print("查看")
    case "3":
        print("删除")
    case _:                  # 兜底：以上都不匹配时执行
        print("输入无效")
