import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QTabWidget, \
    QTextEdit, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QPen, QPainter, QPixmap
import math
from DataStruDef.CalculateType import ConstructionCalculationType as CCType#计算类型
#视口区域
class DrawingWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
            初始化用户界面。
            该方法配置了图形场景(scene)的属性，包括场景的大小、背景颜色等，并设置了渲染提示以提高画质。
            同时，关闭了滚动条，并加载并适应了图像。
            """
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
        """
           加载并适配图像到场景中。

           该函数从当前目录加载名为'slope.png'的图像，将其添加到图形场景中，并确保图像在场景中保持原始的宽高比进行适配显示。

           参数:
           无

           返回值:
           无
           """
        current_directory = os.path.dirname(__file__)
        image_path = os.path.join(current_directory, 'slope.png')
        pixmap = QPixmap(image_path)
        pixmapItem = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmapItem)
        self.fitInView(pixmapItem, Qt.KeepAspectRatio)

    def loadImage(self, image_name):
        """
            加载指定图像到图形场景中。

            :param image_name: 图像文件的名称，相对于当前文件所在的路径。
            :return: 无返回值。
            """
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
        """
           处理窗口大小改变事件。

           当窗口被调整大小时，此函数将被调用。它首先调用超类的resizeEvent方法，然后检查场景中是否有项目。
           如果有项目存在，它会调整视图以适应场景中的第一个项目，保持宽高比。

           参数:
           - event: QResizeEvent 对象，包含了窗口被调整的新尺寸信息。

           返回值:
           - 无
           """
        super().resizeEvent(event)
        if not self.scene.items():
            return
        self.fitInView(self.scene.items()[0], Qt.KeepAspectRatio)

    def mouseDoubleClickEvent(self, event):
        """
            处理鼠标双击事件。

            :param event: 鼠标双击事件对象，包含事件的详细信息。
            :return: 无返回值。
            """
        if event.button() == Qt.MiddleButton:
            if self.scene.items():
                self.fitInView(self.scene.items()[0], Qt.KeepAspectRatio)
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        """
            处理鼠标滚轮事件的函数。

            参数:
            - self: 表示实例自身。
            - event: 鼠标滚轮事件的对象，包含了事件的详细信息。

            返回值:
            - 无。
            """
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        """
            处理鼠标按下事件的函数。

            参数:
            - self: 表示实例自身。
            - event: 鼠标事件对象，包含了事件的详细信息。

            返回值:
            无
            """
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
        button1.clicked.connect(lambda: self.QuickCal_ButtonClicked("快速计算"))

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
    def QuickCal_ButtonClicked(self, buttonText):
        print("DrawSharpPic_EarthSlope.py:开始快速计算")
        #1、获取本次计算的参数，进行试算，给出试算结果，输出到self.textEdit
        parent_dialog=self.parent();#MultipleViewports添加到了QSplitter控件
        # 检查是否真的有父窗口
        if parent_dialog:#
            print(parent_dialog.objectName())
            grand_parent_dialog=parent_dialog.parent() # QSplitter控件添加到了EarthSlopeDialog等子对话框
            if grand_parent_dialog:
                grand_grand_parent_dialog=grand_parent_dialog.parent()#EarthSlopeDialog等子对话框添加到了QWidget
                if grand_grand_parent_dialog:
                    parents_3grand_parent_dialog=grand_grand_parent_dialog.parent()#QWidget添加到了stackedWidget
                    if parents_3grand_parent_dialog:
                        parents_4grand_parent_dialog=parents_3grand_parent_dialog.parent()#stackedWidget添加到了class ECSTabWidget(QTabWidget)
                        currentdata = parents_4grand_parent_dialog.GetCurrentDialogData()#获取到了当前选择的tab对话框的数据
                        conCalType = None
                        if currentdata:
                            conCalType=currentdata.conCalType
                        if conCalType==CCType.SOIL_EMBANKMENT_CALCULATION:# 土方边坡计算
                            print("开始土方边坡计算")
                            if currentdata.verification_project.project_type=="土方直立壁开挖深度计算":
                                print("土方直立壁开挖深度计算")
                                # hmax = 2×c/(K×γ×tan(45°-φ/2))-q/γ
                                #其中，hmax - -土方最大直壁开挖高度
                                #q - -坡顶护到均布荷载
                                #γ - -坑壁土的重度(kN/m3)
                                #φ - -坑壁土的内摩擦角(°)
                                #c - -坑壁土粘聚力(kN/m2)
                                #K - -安全系数（一般用1.25 ）
                                #hmax = 2×12.0/(1.25×20.00×tan(45°-15.0°/2))-2.0/20.00=1.15m；
                                # 将角度转换为弧度
                                c=currentdata.basic_parameters.cohesion#坑壁土粘聚力
                                k = 1.25  # K - -安全系数（一般用1.25 ）
                                γ=currentdata.basic_parameters.unit_weight#坑壁土的重度
                                q=currentdata.slope_top_load.uniform_load#坡顶护道均布荷载
                                slope_angle_in_degrees = currentdata.basic_parameters.slope_angle
                                slope_angle_in_radians = math.radians(45-slope_angle_in_degrees/2)
                                Hmax=2*c/(k*γ*math.tan(slope_angle_in_radians))-q/γ
                                Hmax_rounded = round(Hmax, 2)#保留两位小数
                                # 输出试算结果
                                self.textEdit.clear()
                                self.textEdit.append(f"1.坑壁土方立直壁最大开挖高度为{Hmax_rounded}m。")
                                pass
                            elif currentdata.verification_project.project_type=="基坑安全边坡计算":
                                print("基坑安全边坡计算")
                                c=currentdata.basic_parameters.cohesion#坑壁土粘聚力
                                θ=currentdata.basic_parameters.slope_angle#边坡的坡度角
                                θ_Radians=math.radians(θ)#边坡的坡度角弧度
                                φ=currentdata.basic_parameters.internal_friction_angle#坑壁土的内摩擦角φ(°)
                                φ_Radians=math.radians(φ)#坑壁土的内摩擦角φ(°)
                                γ = currentdata.basic_parameters.unit_weight  # 坑壁土的重度
                                θγ_Radians=(θ-φ)/2
                                Hight= 2 * c * math.sin(θ_Radians)*math.cos(φ_Radians) / (γ * math.sin(θγ_Radians) ** 2)
                                Hight_rounded = round(Hight, 2)  # 保留两位小数
                                # 输出试算结果
                                self.textEdit.clear()
                                self.textEdit.append(f"1.土坡允许最大高度为为{Hight_rounded}m。")
                                pass
        print("DrawSharpPic_EarthSlope.py:结束快速计算")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    multipleViewports = MultipleViewports()
    multipleViewports.show()
    sys.exit(app.exec_())
