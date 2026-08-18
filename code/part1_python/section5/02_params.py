"""五种传参方式：位置 / 默认 / 关键字 / *args / **kwargs，对应笔记 5.2。"""


def introduce(name, city="深圳"):
    print(f"我是{name}，来自{city}")


# 位置参数：按顺序对号入座
introduce("小明", "广州")

# 默认参数：不传就用缺省值
introduce("小明")
introduce("小红", "珠海")

# 关键字参数：指名道姓，不管顺序
introduce(city="汕头", name="小刚")

print("----")


# *args：任意多个位置值，打包成元组
def average(*scores):
    print(f"scores 其实是元组：{scores}")
    return sum(scores) / len(scores)


print(average(85, 92, 78))
print(average(60, 75))

print("----")


# **kwargs：任意多个关键字值，打包成字典
def show_info(**info):
    print(f"info 其实是字典：{info}")
    for key, value in info.items():
        print(f"{key}: {value}")


show_info(name="小明", age=18, city="深圳")
