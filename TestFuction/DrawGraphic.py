import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PyQt5.QtGui import QColor, QPen, QFont, QPainter


def drawFirstShape(scene):
    # 绘制第一个图形
    pen = QPen(QColor(255, 255, 255))  # 白色粗线
    pen.setWidth(3)  # 设置线宽
    # 定义四个坐标点
    points = [(0, 0), (100, 0), (100, -100), (200, -100)]
    # 绘制直线连接四个坐标点
    for i in range(len(points) - 1):
        start_point = points[i]
        end_point = points[i + 1]
        scene.addLine(start_point[0], start_point[1], end_point[0], end_point[1], pen)


def drawSecondShape(scene):
    # 绘制第二个图形
    pen = QPen(QColor(0, 255, 0))  # 绿色线段
    # 定义三条线段
    lines = [((75, -5), (85, 5)),
             ((80, 0), (80, -100)),
             ((75, -105), (85, -95)),
             ((78, -100), (90, -100)),
             ]
    # 绘制线段
    for line in lines:
        start_point, end_point = line
        scene.addLine(start_point[0], start_point[1], end_point[0], end_point[1], pen)
    # 在线段二上添加逆时针旋转90°的文字 "H"
    text_item = QGraphicsTextItem("H")
    text_item.setFont(QFont("Arial", 12))
    text_item.setRotation(-90)  # 逆时针旋转90°
    text_item.setPos(50, -50)  # 设置文本位置
    # 设置文本颜色为绿色
    text_item.setDefaultTextColor(QColor(0, 255, 0))
    scene.addItem(text_item)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('绘制两个图形示例')
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QGraphicsView()
        self.setCentralWidget(self.central_widget)

        scene = QGraphicsScene()
        self.central_widget.setScene(scene)

        # 设置场景背景色为黑色
        scene.setBackgroundBrush(QColor(0, 0, 0))

        # 调用绘制函数绘制两个图形
        drawFirstShape(scene)
        drawSecondShape(scene)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
