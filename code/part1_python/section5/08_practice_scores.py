"""实战：成绩统计工具箱，对应笔记 5.8。"""


def input_scores():
    texts = input("请输入成绩，用空格分隔：").split()
    return list(map(int, texts))


def average(scores):
    return sum(scores) / len(scores)


def pass_rate(scores):
    passed = list(filter(lambda s: s >= 60, scores))
    return len(passed) / len(scores) * 100


def report(scores):
    print(f"人数：{len(scores)}")
    print(f"平均分：{average(scores):.1f}")
    print(f"最高分：{max(scores)}，最低分：{min(scores)}")
    print(f"及格率：{pass_rate(scores):.0f}%")


def main():
    scores = []
    while True:
        print("\n===== 成绩统计工具箱 =====")
        print("1. 录入成绩")
        print("2. 查看统计")
        print("3. 退出")
        choice = input("请选择操作（1-3）：")

        if choice == "1":
            scores = input_scores()
            print(f"已录入 {len(scores)} 条成绩")
        elif choice == "2":
            if len(scores) == 0:
                print("请先录入成绩")
            else:
                report(scores)
        elif choice == "3":
            print("再见！")
            break
        else:
            print("输入无效，请输入 1-3")


main()
