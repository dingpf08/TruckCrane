import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PyQt5.QtGui import QColor, QPen, QFont, QPainter


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

        # 绘制三条线段
        lines = [((75, -5), (85, 5)),
                 ((80, 0), (80, -100)),
                 ((75, -105), (85, -95))]
        pen = QPen(QColor(0, 255, 0))  # 绿色线段
        self.drawLines(scene, pen, lines)

        # 在线段二上添加逆时针旋转90°的文字 "H"
        text_item = QGraphicsTextItem("H")
        text_item.setFont(QFont("Arial", 12))
        text_item.setRotation(-90)  # 逆时针旋转90°
        text_item.setPos(50, -35)  # 设置文本位置
        scene.addItem(text_item)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 设置场景大小
        self.setSceneRect(0, -110, 250, 250)

    def drawLines(self, scene, pen, lines):
        # 绘制线段
        for line in lines:
            start_point, end_point = line
            scene.addLine(start_point[0], start_point[1], end_point[0], end_point[1], pen)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('绘制线段并添加文字')
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = DrawingWidget()
        self.setCentralWidget(self.central_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
