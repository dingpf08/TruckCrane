import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsRectItem, \
    QGraphicsEllipseItem, QGraphicsPolygonItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPen, QBrush, QPolygonF, QPainter


class GraphicsView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)

        # 禁用滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setDragMode(QGraphicsView.NoDrag)
        self.panning = False

    def wheelEvent(self, event):
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.panning = True
            self.last_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value())
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.panning = False
            self.setCursor(Qt.ArrowCursor)
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning:
            # 计算移动距离
            delta = event.pos() - self.last_pos
            # 更新滚动条的位置
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_pos = event.pos()
        else:
            super().mouseMoveEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('图形缩放和平移示例')
        self.setGeometry(300, 300, 600, 400)

        scene = QGraphicsScene()
        self.view = GraphicsView(scene)
        self.setCentralWidget(self.view)

        # 绘制矩形
        rect = QGraphicsRectItem(0, 0, 100, 70)
        rect.setPen(QPen(Qt.blue, 2))
        scene.addItem(rect)

        # 绘制椭圆
        ellipse = QGraphicsEllipseItem(150, 0, 100, 70)
        ellipse.setPen(QPen(Qt.green, 2))
        ellipse.setBrush(QBrush(Qt.yellow))
        scene.addItem(ellipse)

        # 绘制多边形
        polygon = QPolygonF([QPointF(300, 0), QPointF(350, 50), QPointF(300, 100), QPointF(250, 50)])
        polygonItem = QGraphicsPolygonItem(polygon)
        scene.addItem(polygonItem)

        # 设置场景大小
        scene.setSceneRect(-300, -300, 600, 600)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
