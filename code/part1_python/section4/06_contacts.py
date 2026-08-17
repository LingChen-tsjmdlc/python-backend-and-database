"""实战：带菜单的简易通讯录，对应笔记 4.6。

通讯录 = 列表，里面每个元素是一个联系人的字典。
while True 循环显示菜单，直到选择退出。
"""

contacts = []

while True:
    print("\n===== 通讯录 =====")
    print("1. 添加联系人")
    print("2. 查看全部")
    print("3. 按姓名查找")
    print("4. 退出")
    choice = input("请选择操作（1-4）：")

    if choice == "1":
        name = input("请输入姓名：")
        phone = input("请输入电话：")
        contacts.append({"name": name, "phone": phone})
        print(f"已添加：{name}")

    elif choice == "2":
        if len(contacts) == 0:
            print("通讯录是空的")
        else:
            for c in contacts:
                print(f"{c['name']}：{c['phone']}")

    elif choice == "3":
        target = input("请输入要查找的姓名：")
        found = False
        for c in contacts:
            if c["name"] == target:
                print(f"找到了：{c['name']} 的电话是 {c['phone']}")
                found = True
        if not found:
            print(f"通讯录里没有 {target}")

    elif choice == "4":
        print("再见！")
        break

    else:
        print("输入无效，请输入 1-4")
