import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QPainter, QPixmap

class DrawingWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭水平滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭垂直滚动条
        self.setRenderHint(QPainter.Antialiasing)

        # 设置场景背景颜色为黑色
        self.scene.setBackgroundBrush(QColor(0, 0, 0))

        # 加载并显示图片
        self.loadAndFitImage()

        self.last_pos = QPointF()
        self.panning = False

    def loadAndFitImage(self):
        # 获取当前文件的目录
        current_directory = os.path.dirname(__file__)
        # 构建图片的绝对路径
        image_path = os.path.join(current_directory, 'slope.png')
        # 加载一张图片
        pixmap = QPixmap(image_path)
        # 创建一个QGraphicsPixmapItem对象
        pixmapItem = QGraphicsPixmapItem(pixmap)
        # 将图片项添加到场景中
        self.scene.addItem(pixmapItem)
        # 根据视图大小调整图片大小
        self.fitInView(pixmapItem, Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        # 视图大小发生变化时，重新调整图片以填充视图
        super().resizeEvent(event)
        if not self.scene.items():
            return
        self.fitInView(self.scene.items()[0], Qt.KeepAspectRatio)
    def mouseDoubleClickEvent(self, event):
        # 检测鼠标中键双击事件
        if event.button() == Qt.MiddleButton:
            # 如果场景中有项目（在这个场景中应该只有一个图片项目）
            if self.scene.items():
                # 使图片充满整个视口
                self.fitInView(self.scene.items()[0], Qt.KeepAspectRatio)
            event.accept()  # 表示事件已被处理
        else:
            super().mouseDoubleClickEvent(event)  # 其他情况，调用基类的方法
    def wheelEvent(self, event):
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.panning = True
            self.last_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.panning = False

    def mouseMoveEvent(self, event):
        if self.panning:
            current_pos = event.pos()
            delta = self.mapToScene(current_pos) - self.mapToScene(self.last_pos)
            self.last_pos = current_pos

            # 调整视图中的场景位置
            self.translate(delta.x(), delta.y())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('图形界面')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: black;")

        self.central_widget = DrawingWidget()
        self.setCentralWidget(self.central_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
