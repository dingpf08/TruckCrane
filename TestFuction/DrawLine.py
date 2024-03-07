import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PyQt5.QtGui import QColor, QPen, QPainter


class DrawingWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        scene = QGraphicsScene()
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)

        # 设置场景背景颜色为白色
        self.scene().setBackgroundBrush(QColor(255, 255, 255))

        # 定义四个坐标点
        points = [(0, 0), (100, 0), (100, -100), (200, -100)]

        # 绘制直线连接四个坐标点
        pen = QPen(QColor(0, 0, 0))
        self.drawLine(scene, pen, points)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 设置场景大小
        self.setSceneRect(0, 0, 250, 150)

    def drawLine(self, scene, pen, points):
        # 依次连接四个坐标点绘制直线
        for i in range(len(points) - 1):
            start_point = points[i]
            end_point = points[i + 1]
            scene.addLine(start_point[0], start_point[1], end_point[0], end_point[1], pen)




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('绘制直线示例')
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = DrawingWidget()
        self.setCentralWidget(self.central_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
