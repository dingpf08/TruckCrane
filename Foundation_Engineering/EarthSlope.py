import sys
import uuid

from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QRadioButton, QPushButton, QGraphicsView, QGraphicsScene, QLabel, QFormLayout, QComboBox, QSplitter, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen, QPainter, QPixmap
from DrawGraphinsScene.DrawSharpPic import MultipleViewports as DrawArea  # 自己绘制绘图区域
from DataStruDef.EarthSlopeCalculation import SlopeCalculationData as Scdata, VerificationProject, \
    SlopeTopLoad, BasicParameters, SlopeCalculationData  # 边坡计算数据
#存储的类型 对话框的1-uuid,2-验算项目类型 3-坡顶作用荷载， 基本参数：4-坑壁土类型、5-土的重度、6-土的内摩擦角、7-土粘聚力、8-边坡的坡度角
class EarthSlopeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.m_name="土方边坡计算对话框"
        self.uuid = uuid.uuid4()  # 生成一个唯一的UUID
        self.verification_project = VerificationProject("基坑安全边坡计算")
        # 创建坡顶作用荷载实例
        self.slope_top_load = SlopeTopLoad(20.0)  # 假设均布荷载为20kN/m²
        # 创建基本参数实例 # 坑壁土类型 土的重度γ(kN/m³) # 土的内摩擦角ϕ(°) # 土粘聚力c(kN/㎡) # 边坡的坡度角θ(°)
        self. basic_parameters = BasicParameters("粘性土", 18.5, 30, 10, 45)
        self.IsSave=True#是否保存,初始化为真，可以保存
        # 创建土方边坡计算数据实例
        slope_calculation_data = SlopeCalculationData(self.verification_project, self.slope_top_load, self.basic_parameters)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('土方边坡计算')
        self.setGeometry(100, 100, 800, 600)  # 设置对话框的初始大小

        main_splitter = QSplitter(Qt.Horizontal)  # 创建一个水平分割器

        # 左边部件
        self.left_widget = QWidget()
        left_layout = QVBoxLayout(self.left_widget)

        # 演算项目选择区域
        calculation_group = QGroupBox("验算项目选择")
        calculation_layout = QVBoxLayout()
        self.radio1 = QRadioButton("土方直立壁开挖深度计算")
        self.radio1.setChecked(True)#默认第一个按钮被选中
        self.radio2 = QRadioButton("基坑安全边坡计算")
        # 对于QRadioButton，你需要为每一个按钮的toggled信号连接到markUnsavedChanges方法
        self.radio1.toggled.connect(self.markUnsavedChanges)
        self.radio2.toggled.connect(self.markUnsavedChanges)
        calculation_layout.addWidget(self.radio1)
        calculation_layout.addWidget(self.radio2)
        self.radio1.clicked.connect(self.on_radio_clicked)
        self. radio2.clicked.connect(self.on_radio_clicked)
        calculation_group.setLayout(calculation_layout)

        # 坡顶作用荷载区域
        load_group = QGroupBox("坡顶作用荷载")
        load_layout = QVBoxLayout()
        load_hbox1 = QHBoxLayout()
        self.load_label1 = QLabel("坑顶护道上均布荷载 q(kN/m²):")
        self.load_input1 = QLineEdit("2")
        # 连接文本框、组合框等的信号到markUnsavedChanges方法
        self.load_input1.textChanged.connect(self.markUnsavedChanges)
        load_hbox1.addWidget(self.load_label1)
        load_hbox1.addWidget(self.load_input1)
        load_layout.addLayout(load_hbox1)
        load_group.setLayout(load_layout)
        load_group.setFixedHeight(100)

        # 基本参数区域
        parameter_group = QGroupBox("基本参数")
        parameter_layout = QFormLayout()

        self.soil_types = ["粘性土", "红粘土", "粉土", "粉砂", "细砂", "中砂", "粗砂", "砾砂"]
        self.soil_type_combobox = QComboBox()#土的类型
        self.soil_type_combobox.addItems(self.soil_types)
        self.soil_type_combobox.currentIndexChanged.connect(self.markUnsavedChanges)  # 连接信号
        self.soil_types_lable=QLabel("坑壁土类型:")
        parameter_layout.addRow(self.soil_types_lable, self.soil_type_combobox)

        self.Basic_soilweight = QLineEdit("20")#土的重度γ(kN/m³)
        self.Basic_soilweight_lable=QLabel("土的重度γ(kN/m³):")
        self.Basic_soilweight.textChanged.connect(self.markUnsavedChanges)
        parameter_layout.addRow(self.Basic_soilweight_lable, self.Basic_soilweight)


        self.basic_InternalFrictionAngle= QLineEdit("15")#土的内摩擦角ϕ(°)
        self.basic_InternalFrictionAngle_lable = QLabel("土的内摩擦角ϕ(°):")
        self.basic_InternalFrictionAngle.textChanged.connect(self.markUnsavedChanges)
        parameter_layout.addRow(self.basic_InternalFrictionAngle_lable,self.basic_InternalFrictionAngle)


        self.basic_soilCohesion = QLineEdit("12")  # 土粘聚力c(kN/㎡)
        self.basic_soilCohesion_lable = QLabel("土粘聚力c(kN/㎡):")
        self.basic_soilCohesion.textChanged.connect(self.markUnsavedChanges)
        parameter_layout.addRow(self.basic_soilCohesion_lable, QLineEdit("12"))


        self.basic_slopeAngle  = QLineEdit("45")  # 边坡的坡度角θ
        self.basic_slopeAngle_lable = QLabel("边坡的坡度角θ(°):")
        self.basic_slopeAngle.textChanged.connect(self.markUnsavedChanges)
        parameter_layout.addRow(self.basic_slopeAngle_lable, self.basic_slopeAngle)

        parameter_group.setLayout(parameter_layout)
        # 将各个区域的布局添加到左侧布局
        left_layout.addWidget(calculation_group)
        left_layout.addWidget(load_group)
        left_layout.addWidget(parameter_group)

        # 右边绘图区
        self.right_layout = DrawArea()

        # 将左边和右边的部件添加到分割器
        main_splitter.addWidget(self.left_widget)
        main_splitter.addWidget(self.right_layout)

        # 创建一个主布局并添加分割器
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_splitter)

        # 设置对话框的主布局
        self.setLayout(main_layout)
        #返回对话框的uuid
    def Getuuid(self):
        return self.uuid
    #切换“土方直立壁开挖深度计算”和“基坑安全边坡计算”
    def on_radio_clicked(self):
        radio_button = self.sender()
        if radio_button.isChecked():
            radio_text=radio_button.text()
            if radio_text == "土方直立壁开挖深度计算":
                print("选择了土方直立壁开挖深度计算")
                self.load_label1.setEnabled(True)#坡顶作用荷载标签
                self.load_input1.setEnabled(True)#坡顶作用荷载输入框
                self.basic_slopeAngle_lable.setEnabled(False)  # 边坡的坡度角
                self.basic_slopeAngle.setEnabled(False)#边坡的坡度角
                # 这里可以添加更多针对此选项的代码
            elif radio_text == "基坑安全边坡计算":
                print("选择了基坑安全边坡计算")
                self.load_label1.setEnabled(False)  # 坡顶作用荷载标签
                self.load_input1.setEnabled(False)  # 坡顶作用荷载输入框
                self.basic_slopeAngle_lable.setEnabled(True)  # 边坡的坡度角
                self.basic_slopeAngle.setEnabled(True)  # 边坡的坡度角
                # 这里可以添加更多针对此选项的代码
            self.right_layout.ChangeLoadImage(radio_text)

    def markUnsavedChanges(self):#不能保存，需要弹出对话框
        # 当控件的参数被修改时，将IsSave设置为False
        self.IsSave = False
if __name__ == '__main__':
    app = QApplication(sys.argv)
    earth_slope_dialog = EarthSlopeDialog()
    earth_slope_dialog.show()
    sys.exit(app.exec_())
