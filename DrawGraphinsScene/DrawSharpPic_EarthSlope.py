import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QTabWidget, \
    QTextEdit, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QPainter, QPixmap
#视口区域
class DrawingWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-1000000, -1000000, 2000000, 2000000)  # 根据需要调整
        self.setScene(self.scene)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭水平滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 关闭垂直滚动条
        self.setRenderHint(QPainter.Antialiasing)
        self.scene.setBackgroundBrush(QColor(0, 0, 0))
        self.loadAndFitImage()
        self.last_pos = QPointF()
        self.panning = False

    def loadAndFitImage(self):
        current_directory = os.path.dirname(__file__)
        image_path = os.path.join(current_directory, 'slope.png')
        pixmap = QPixmap(image_path)
        pixmapItem = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmapItem)
        self.fitInView(pixmapItem, Qt.KeepAspectRatio)

    def loadImage(self, image_name):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_directory, image_name)
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Unable to load image: {image_path}")
            return
        pixmapItem = QGraphicsPixmapItem(pixmap)
        self.scene.clear()
        self.scene.addItem(pixmapItem)
        self.fitInView(pixmapItem, Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.scene.items():
            return
        self.fitInView(self.scene.items()[0], Qt.KeepAspectRatio)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MiddleButton:
            if self.scene.items():
                self.fitInView(self.scene.items()[0], Qt.KeepAspectRatio)
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

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
        try:
            if self.panning and self.last_pos:  # 确保已经开始拖动并记录了最后的位置
                current_pos = event.pos()
                # 计算从上次位置到当前位置的位移
                delta = self.mapToScene(current_pos) - self.mapToScene(self.last_pos)
                self.last_pos = current_pos

                # 获取当前的滚动条位置并调整
                hbar = self.horizontalScrollBar()
                vbar = self.verticalScrollBar()
                # 将浮点数位移值转换为整数
                hbar.setValue(int(hbar.value() - delta.x()))
                vbar.setValue(int(vbar.value() - delta.y()))
        except Exception as e:
            print(f"Error during mouseMoveEvent: {e}")

        super().mouseMoveEvent(event)  # 调用父类处理，确保其他事件也能得到处理


class MultipleViewports(QMainWindow):
    def __init__(self):
        super().__init__()
        # 定义控件的布局比例
        self.layoutRatios = {
            'tabs': 80,
            'buttonsWidget': 5,
            'textEdit': 15
        }
        self.initUI()
    def ChangeLoadImage(self,radioname):
        if radioname=="土方直立壁开挖深度计算":
            self.tab1.loadImage('slope.png')
        elif radioname=="基坑安全边坡计算":
            self.tab1.loadImage('slope_2.png')
    def initUI(self):
        self.setWindowTitle('多标签图形界面')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: white;")
        mainWidget = QWidget()
        mainLayout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tab1 = DrawingWidget()
        self.tab2 = DrawingWidget()
        self.tab3 = DrawingWidget()

        self.tab1.loadImage('slope.png')

        self.tabs.addTab(self.tab1, "示意图")

        mainLayout.addWidget(self.tabs, self.layoutRatios['tabs'])  # 绘图区布局比例设置为6

        self.buttonsWidget = QWidget()
        buttonsLayout = QHBoxLayout()

        button1 = QPushButton("快速计算")
        button1.clicked.connect(lambda: self.buttonClicked("快速计算"))

        buttonsLayout.addWidget(button1)

        # 添加一个弹性空间，使按钮只占据1/5的宽度
        buttonsLayout.addStretch(4)  # 参数4意味着弹性空间的伸缩性是按钮的4倍,按钮占据控件的比例为1/5
        self.buttonsWidget.setLayout(buttonsLayout)

        mainLayout.addWidget(self.buttonsWidget, self.layoutRatios['buttonsWidget'])  # 按钮区布局比例设置为1

        self.textEdit = QTextEdit()#输出框
        self.textEdit.setReadOnly(True)

        mainLayout.addWidget(self.textEdit, self.layoutRatios['textEdit'])  # 文字显示区布局比例设置为3

        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

    #快速计算
    def buttonClicked(self, buttonText):
        #1、获取本次计算的参数，进行试算，给出试算结果，输出到self.textEdit
        parent_dialog=self.parent();#QSplitter
        # 检查是否真的有父窗口
        if parent_dialog:#
            print(parent_dialog.objectName())
            grand_parent_dialog=parent_dialog.parent() # EarthSlopeDialog等子对话框
            if grand_parent_dialog:
                grand_grand_parent_dialog=grand_parent_dialog.parent()#QWidget
                if grand_grand_parent_dialog:
                    parents_3grand_parent_dialog=grand_grand_parent_dialog.parent()#stackedWidget
                    if parents_3grand_parent_dialog:
                        parents_4grand_parent_dialog=parents_3grand_parent_dialog.parent()#QWidget 标签管理页面class ECSTabWidget(QTabWidget)
                        currentdata = parents_4grand_parent_dialog.GetCurrentDialogData()#获取到了当前选择的tab的数据
                        print(f"{currentdata}")
        #输出试算结果
        self.textEdit.clear()
        self.textEdit.append(f"{buttonText} 被点击了")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    multipleViewports = MultipleViewports()
    multipleViewports.show()
    sys.exit(app.exec_())
