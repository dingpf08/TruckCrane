import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsTextItem
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QPainter, QFont


class DrawingWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(self.windowFlags())
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setSceneRect(0, 0, 300, 300)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)#水平滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)#垂直滚动条
        self.setRenderHint(QPainter.Antialiasing)

        # 设置场景背景颜色为黑色
        self.scene.setBackgroundBrush(QColor(0, 0, 0))

        # 绘制的线条颜色为绿色
        pen = QPen(QColor(0, 255, 0))
        # 在图形中绘制正方形
        #self.drawSquare(pen)
        # 在图形中绘制文字 雄关漫道真如铁
        #self.drawText()
        self.drawFirstShape(self.scene)
        self.drawSecondShape(self.scene)
        self.last_pos = QPointF()
        self.panning = False

    def drawSquare(self,pen):
        self.scene.clear()
        self.square = self.scene.addRect(50, 50, 200, 200, pen=pen, brush=QColor(0, 0, 0))
    #绘制边坡的轮廓线
    def drawFirstShape(self,scene):
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
    #绘制标注线
    def drawSecondShape(self,scene):
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
        text_item = QGraphicsTextItem("h")
        text_item.setFont(QFont("Arial", 12))
        text_item.setRotation(-90)  # 逆时针旋转90°
        text_item.setPos(50, -50)  # 设置文本位置
        # 设置文本颜色为绿色
        text_item.setDefaultTextColor(QColor(0, 255, 0))
        scene.addItem(text_item)
        #绘制文本：雄关漫道真如铁
    def drawText(self):
        # 设置文字的颜色和字体
        textFont = QFont("宋体", 12)
        textColor = QColor(255, 255, 255)  # 白色文字
        textItem = self.scene.addText("雄关漫道真如铁", textFont)
        textItem.setDefaultTextColor(textColor)
        # 调整文字位置
        textItem.setPos(50, 20)
        # 将字体向右旋转30°
        textItem.setRotation(30)
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

            # 获取当前场景的矩形并调整其位置
            new_scene_rect = self.sceneRect().translated(-delta)
            self.setSceneRect(new_scene_rect)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('图形界面')
        self.setGeometry(100, 100, 400, 400)
        self.setStyleSheet("background-color: black;")

        self.central_widget = DrawingWidget()
        self.setCentralWidget(self.central_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
