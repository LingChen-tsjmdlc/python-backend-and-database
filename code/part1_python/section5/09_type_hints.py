"""类型提示：变量、容器、函数签名上的标注写法，对应笔记 5.9。"""

# 基本类型：变量后面写 : 类型（不影响运行，是提示不是检查）
count: int = 3
price: float = 9.9
name: str = "小明"
is_active: bool = True

# 容器可以写细"里面装什么"
scores: list[int] = [85, 92, 78]
prices: dict[str, float] = {"苹果": 3.5, "香蕉": 2.8}
point: tuple[int, int] = (3, 5)
tags: set[str] = {"python", "sql"}

# 嵌套结构一层层写下去
students: list[dict[str, int]] = [{"score": 85}, {"score": 92}]

# 允许几种类型用 | ；允许"没有值"加 None
user_input: str | None = None
score: int | float = 92


# 函数：参数后 : 类型，括号后 -> 返回值类型
def average(scores: list[int], passing: int = 60) -> float:
    passed = [s for s in scores if s >= passing]
    return sum(passed) / len(passed)


print(average([85, 92, 55, 78]))


# 不返回有用结果的函数标 -> None
def show_info(**info: str) -> None:
    for key, value in info.items():
        print(f"{key}: {value}")


show_info(name="小明", city="深圳")

# 验证"不影响运行"：上面 count 标了 int，这里却赋字符串，Python 照跑
# （但 PyCharm 会在这一行画波浪线，提示类型不匹配）
count = "not a number"
print(count)
