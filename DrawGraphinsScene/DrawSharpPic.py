import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QTabWidget
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

    def loadImage(self, image_name):
        # 构建图片的绝对路径
        current_directory = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_directory, image_name)

        # 加载一张图片
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Unable to load image: {image_path}")
            return

        # 创建一个 QGraphicsPixmapItem 对象
        pixmapItem = QGraphicsPixmapItem(pixmap)

        # 清空之前的场景并添加新的图片项
        self.scene.clear()
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

class MultipleViewports(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('多标签图形界面')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: black;")

        # 创建 QTabWidget 对象
        self.tabs = QTabWidget()

        # 创建三个标签页，每个标签页都是 DrawingWidget 的一个实例
        self.tab1 = DrawingWidget()
        self.tab2 = DrawingWidget()
        self.tab3 = DrawingWidget()

        # 加载每个 DrawingWidget 的不同图片
        # 假设您有 tab1.png, tab2.png 和 tab3.png
        self.tab1.loadImage('slope.png')
        self.tab2.loadImage('slope1.png')
        self.tab3.loadImage('slope2.png')

        # 将 DrawingWidget 添加到每个标签页
        self.tabs.addTab(self.tab1, "正立面")
        self.tabs.addTab(self.tab2, "侧立面")
        self.tabs.addTab(self.tab3, "纵横向水平杆布置")

        # 设置 QTabWidget 为中心部件
        self.setCentralWidget(self.tabs)

    # 定义一个加载图片的方法
    def loadImage(self, image_name):
        current_directory = os.path.dirname(__file__)
        image_path = os.path.join(current_directory, image_name)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.scene.clear()
            pixmapItem = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(pixmapItem)
            self.fitInView(pixmapItem, Qt.KeepAspectRatio)

# 下面是创建和运行应用程序的标准方法
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())