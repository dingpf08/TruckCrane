import matplotlib.pyplot as plt


def draw_arrows():
    # 起点Y坐标和终点Y坐标
    y_start = -120
    y_end = -100

    # 创建图形和轴
    fig, ax = plt.subplots()

    # 设置图形的显示范围
    ax.set_xlim(95, 155)
    ax.set_ylim(-125, -95)

    # 循环绘制箭头
    for x in range(100, 151, 5):
        # 绘制箭头，从(x, y_start)到(x, y_end)
        ax.arrow(x, y_start, 0, y_end - y_start, head_width=1, head_length=2, fc='k', ec='k', length_includes_head=True)

    # 显示图形
    plt.show()


if __name__ == '__main__':
    draw_arrows()
