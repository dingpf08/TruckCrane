import sys
import uuid

from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QRadioButton, QPushButton, QGraphicsView, QGraphicsScene, QLabel, QFormLayout, QComboBox, QSplitter, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen, QPainter, QPixmap
#from DrawGraphinsScene.DrawSharp import DrawingWidget as DrawArea  # 自己绘制绘图区域
from DrawGraphinsScene.DrawSharpPic import MultipleViewports as DrawArea  # 自己绘制绘图区域
class EarthSlopeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.m_name="土方边坡计算对话框"
        self.uuid = uuid.uuid4()  # 生成一个唯一的UUID
        self.initUI()

    def initUI(self):
        self.setWindowTitle('土方边坡计算')
        self.setGeometry(100, 100, 800, 600)  # 设置对话框的初始大小

        main_splitter = QSplitter(Qt.Horizontal)  # 创建一个水平分割器

        # 左边部件
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 演算项目选择区域
        calculation_group = QGroupBox("验算项目选择")
        calculation_layout = QVBoxLayout()
        radio1 = QRadioButton("土方直立壁开挖深度计算")
        radio2 = QRadioButton("基坑安全边坡计算")
        calculation_layout.addWidget(radio1)
        calculation_layout.addWidget(radio2)
        calculation_group.setLayout(calculation_layout)

        # 坡顶作用荷载区域
        load_group = QGroupBox("坡顶作用荷载")
        load_layout = QVBoxLayout()
        load_hbox1 = QHBoxLayout()
        load_label1 = QLabel("坑顶护道上均布荷载 q(kN/m²):")
        load_input1 = QLineEdit("2")
        load_hbox1.addWidget(load_label1)
        load_hbox1.addWidget(load_input1)
        load_layout.addLayout(load_hbox1)
        load_group.setLayout(load_layout)
        load_group.setFixedHeight(100)

        # 基本参数区域
        parameter_group = QGroupBox("基本参数")
        parameter_layout = QFormLayout()
        soil_types = ["粘性土", "红粘土", "粉土", "粉砂", "细砂", "中砂", "粗砂", "砾砂"]
        soil_type_combobox = QComboBox()
        soil_type_combobox.addItems(soil_types)
        parameter_layout.addRow("坑壁土类型:", soil_type_combobox)
        parameter_layout.addRow("土的重度γ(kN/m³):", QLineEdit("20"))
        parameter_layout.addRow("土的内摩擦角ϕ(°):", QLineEdit("15"))
        parameter_layout.addRow("土粘聚力c(kN/㎡):", QLineEdit("12"))
        parameter_layout.addRow("边坡的坡度角θ(°):", QLineEdit("45"))
        parameter_group.setLayout(parameter_layout)

        # 将各个区域的布局添加到左侧布局
        left_layout.addWidget(calculation_group)
        left_layout.addWidget(load_group)
        left_layout.addWidget(parameter_group)

        # 右边绘图区
        right_layout = DrawArea()

        # 将左边和右边的部件添加到分割器
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_layout)

        # 创建一个主布局并添加分割器
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)

        # 设置对话框的主布局
        self.setLayout(main_layout)
    def Getuuid(self):
        return self.uuid
if __name__ == '__main__':
    app = QApplication(sys.argv)
    earth_slope_dialog = EarthSlopeDialog()
    earth_slope_dialog.show()
    sys.exit(app.exec_())
