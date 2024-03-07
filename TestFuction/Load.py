import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QPainter, QPolygonF, QBrush


class DrawingWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        scene = QGraphicsScene()
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)

        # 设置场景背景颜色为白色
        self.scene().setBackgroundBrush(Qt.white)

        # 绘制均布荷载线
        pen = QPen(QColor(0, 0, 0))
        brush = QBrush(Qt.SolidPattern)
        self.drawLoad(scene, pen, brush)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setSceneRect(0, 0, 300, 200)

    def drawLoad(self, scene, pen, brush):
        # 绘制线段
        scene.addLine(50, 100, 250, 100, pen)

        # 绘制箭头
        arrow = QPolygonF()
        arrow.append(QPointF(250, 100))
        arrow.append(QPointF(240, 90))
        arrow.append(QPointF(240, 110))
        arrow.append(QPointF(250, 100))
        scene.addPolygon(arrow, pen, brush)

        # 绘制箭头底部横线
        scene.addLine(240, 90, 240, 110, pen)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('均布荷载示例')
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = DrawingWidget()
        self.setCentralWidget(self.central_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
