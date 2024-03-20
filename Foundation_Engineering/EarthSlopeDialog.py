#土方边坡计算对话框
import sys
import uuid
import pickle
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QRadioButton, \
    QPushButton, QGraphicsView, QGraphicsScene, QLabel, QFormLayout, QComboBox, QSplitter, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen, QPainter, QPixmap
from DrawGraphinsScene.DrawSharpPic_EarthSlope import MultipleViewports as DrawArea  # 自己绘制绘图区域
from DataStruDef.EarthSlopeCalculation import SlopeCalculationData as Scdata, VerificationProject, \
    SlopeTopLoad, BasicParameters, SlopeCalculationData  # 边坡计算数据
from DataStruDef.CalculateType import ConstructionCalculationType as Caltype
#存储的类型 对话框的1-uuid,2-验算项目类型 3-坡顶作用荷载， 基本参数：4-坑壁土类型、5-土的重度、6-土的内摩擦角、7-土粘聚力、8-边坡的坡度角
class EarthSlopeDialog(QDialog):
    def __init__(self,para_uuid=None,para_slopeCalculationData=None):#默认的参数给init初始化函数
        super().__init__()
        self.m_name="土方边坡计算对话框"

        self.uuid =None#能够唯一定位对话框的符号
        self.verification_project =None#工程名称
        self.slope_top_load =None#均布荷载
        self.basic_parameters=None#基本参数
        self.slope_calculation_data=None#所有参数的集合
        self.IsSave = True#
        if para_uuid==None:
            self.uuid =uuid.uuid4()  # 生成一个唯一的UUID
        else:
            self.uuid=para_uuid

        if para_slopeCalculationData==None:
            self.verification_project = VerificationProject("基坑安全边坡计算")
            # 创建坡顶作用荷载实例
            self.slope_top_load = SlopeTopLoad(20.0)  # 假设均布荷载为20kN/m²
            # 创建基本参数实例 # 坑壁土类型 土的重度γ(kN/m³) # 土的内摩擦角ϕ(°) # 土粘聚力c(kN/㎡) # 边坡的坡度角θ(°)
            self. basic_parameters = BasicParameters("粘性土", 18.5, 30, 10, 45)
            self.IsSave=True#是否保存,初始化为真，可以保存
            # 创建土方边坡计算数据  实例
            self.slope_calculation_data = SlopeCalculationData(self.verification_project, self.slope_top_load, self.basic_parameters)#土方边坡的数据
        else:
            self.slope_calculation_data =para_slopeCalculationData
        self.initUI()
    #获取界面参数并更新界面参数
    def updateCalculationData(self):
        """根据当前的对话框内容更新计算数据。"""
        # 更新验算项目类型
        if self.radio1.isChecked():
            self.slope_calculation_data.verification_project.project_type = "土方直立壁开挖深度计算"
        elif self.radio2.isChecked():
            self.slope_calculation_data.verification_project.project_type = "基坑安全边坡计算"
        # 更新坡顶作用荷载
        self.slope_calculation_data.slope_top_load.uniform_load = float(self.load_input1.text())
        # 更新基本参数
        self.slope_calculation_data.basic_parameters.soil_type = self.soil_type_combobox.currentText()#坑壁土的类型
        self.slope_calculation_data.basic_parameters.unit_weight = float(self.Basic_soilweight.text())#土的重度
        self.slope_calculation_data.basic_parameters.internal_friction_angle = float(self.basic_InternalFrictionAngle.text())#土的内摩擦角
        self.slope_calculation_data.basic_parameters.cohesion = float(self.basic_soilCohesion.text())#土粘聚力
        self.slope_calculation_data.basic_parameters.slope_angle = float(self.basic_slopeAngle.text())#边坡的坡度角
        return self.slope_calculation_data
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
        self.radio2 = QRadioButton("基坑安全边坡计算")
        if self.slope_calculation_data.verification_project.project_type == "土方直立壁开挖深度计算":
            self.radio1.setChecked(True)
        else:
            self.radio2.setChecked(True)

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
        self.load_input1 = QLineEdit()#坑顶护道上均布荷载
        self.load_input1.setText(str(self.slope_calculation_data.slope_top_load.uniform_load))
        # 连接文本框、组合框等的信号到markUnsavedChanges方法
        self.load_input1.textChanged.connect(self.markUnsavedChanges)
        self.load_input1.editingFinished.connect(self.checkTopLoad)
        load_hbox1.addWidget(self.load_label1)
        load_hbox1.addWidget(self.load_input1)
        load_layout.addLayout(load_hbox1)
        load_group.setLayout(load_layout)
        load_group.setFixedHeight(100)

        # 基本参数区域
        parameter_group = QGroupBox("基本参数")
        parameter_layout = QFormLayout()

        self.soil_types = ["填土", "淤泥", "淤泥质二", "粘性土", "红粘土", "粉土", "粉砂", "细砂", "中砂", "粗砂", "砾砂", "角砾", "圆砾", "碎石", "卵石", "风化岩", "中风化岩", "微风化岩", "新鲜岩"]
        self.soil_type_combobox = QComboBox()#土的类型
        self.soil_type_combobox.addItems(self.soil_types)
        soil_type_index = self.soil_types.index(self.slope_calculation_data.basic_parameters.soil_type)
        self.soil_type_combobox.setCurrentIndex(soil_type_index)
        self.soil_type_combobox.currentIndexChanged.connect(self.markUnsavedChanges)  # 连接信号，告诉系统对话框修改了
        self.soil_type_combobox.currentIndexChanged.connect(self.checkSoilType)  # 新增检查土类型的方法
        self.soil_types_lable=QLabel("坑壁土类型:")
        parameter_layout.addRow(self.soil_types_lable, self.soil_type_combobox)


        self.Basic_soilweight = QLineEdit()#土的重度γ(kN/m³)"20"
        self.Basic_soilweight.setText(str(self.slope_calculation_data.basic_parameters.unit_weight))
        self.Basic_soilweight_lable=QLabel("土的重度γ(kN/m³):")
        self.Basic_soilweight.editingFinished.connect(self.checkSoilWeight)#结束编辑
        self.Basic_soilweight.textChanged.connect(self.markUnsavedChanges)
        parameter_layout.addRow(self.Basic_soilweight_lable, self.Basic_soilweight)


        self.basic_InternalFrictionAngle= QLineEdit()#土的内摩擦角ϕ(°)"15"
        self.basic_InternalFrictionAngle.editingFinished.connect(self.checkInternalFrictionAngle)#用户输入完成
        self.basic_InternalFrictionAngle_lable = QLabel("土的内摩擦角ϕ(°):")
        self.basic_InternalFrictionAngle.setText(
            str(self.slope_calculation_data.basic_parameters.internal_friction_angle))
        self.basic_InternalFrictionAngle.textChanged.connect(self.markUnsavedChanges)
        parameter_layout.addRow(self.basic_InternalFrictionAngle_lable,self.basic_InternalFrictionAngle)


        self.basic_soilCohesion = QLineEdit()  # 土粘聚力c(kN/㎡)"12"
        self.basic_soilCohesion.setText(str(self.slope_calculation_data.basic_parameters.cohesion))  # 使用数据填充
        self.basic_soilCohesion_lable = QLabel("土粘聚力c(kN/㎡):")
        self.basic_soilCohesion.textChanged.connect(self.markUnsavedChanges)
        self.basic_soilCohesion.editingFinished.connect(self.checkSoilCohesion)#检查数据是否在范围内
        parameter_layout.addRow(self.basic_soilCohesion_lable, self.basic_soilCohesion)


        self.basic_slopeAngle  = QLineEdit()  # 边坡的坡度角θ"45"
        self.basic_slopeAngle.setText(str(self.slope_calculation_data.basic_parameters.slope_angle))  # 使用数据填充
        self.basic_slopeAngle_lable = QLabel("边坡的坡度角θ(°):")
        self.basic_slopeAngle.textChanged.connect(self.markUnsavedChanges)
        self.basic_slopeAngle.editingFinished.connect(self.checkSlopeAngle)#检查数据是否在范围内
        parameter_layout.addRow(self.basic_slopeAngle_lable, self.basic_slopeAngle)

        parameter_group.setLayout(parameter_layout)
        # 将各个区域的布局添加到左侧布局
        left_layout.addWidget(calculation_group)
        left_layout.addWidget(load_group)
        left_layout.addWidget(parameter_group)

        # 右边绘图区
        self.right_layout = DrawArea()#土方边坡对话框

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

    #检查土的重度
    def checkSoilWeight(self):
        try:
            weight = float(self.Basic_soilweight.text())
            if weight < 0.1 or weight > 40:
                QMessageBox.warning(self, "土重度输入错误", "请输入0.1（包含）到40（包含）之间的实数")
                self.Basic_soilweight.setFocus()  # 将焦点重新设置到输入框
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的实数")
            self.Basic_soilweight.setFocus()  # 将焦点重新设置到输入框
        # 将焦点设置回土的重度输入框，并选中文本以便于修改
        self.Basic_soilweight.setFocus()
        self.Basic_soilweight.selectAll()

    #切换“土方直立壁开挖深度计算”和“基坑安全边坡计算”
    def on_radio_clicked(self):
        radio_button = self.sender()#在Qt框架（和PyQt）中，
        # sender()方法用于确定哪个QWidget（例如按钮、单选按钮、复选框等）发出了当前正在处理的信号。当
        # 在事件处理方法（例如槽函数）中调用self.sender()时，它会返回触发当前事件的对象的引用。
        # 这允许您在一个事件处理方法中处理来自多个对象的信号，而不需要为每个对象创建单独的方法。
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
                # 检查各个输入框的数据是否合理
                self.checkTopLoad()#坡顶作用荷载参数合理性检查
                self.checkSoilWeight()#检查土的重度
                self.checkSoilCohesion()#土的粘聚力数值的检查
                self.checkInternalFrictionAngle()#检查土的内摩擦角是否在范围内
                self.checkSlopeAngle()#边坡的坡度角检查
            self.right_layout.ChangeLoadImage(radio_text)#根据选择的类型不同切换图片
    #一旦控件修改，调用这个函数，使得对话框处于未保存状态
    def markUnsavedChanges(self):#不能保存，需要弹出对话框
        # 当控件的参数被修改时，将IsSave设置为False
        self.IsSave = False
    #坡顶作用荷载参数合理性检查
    def checkTopLoad(self):
        try:
            top_load = float(self.load_input1.text())
            if not 0 <= top_load <= 100:
                QMessageBox.warning(self, "坡顶作用荷载输入错误", "请输入0（包含）到100（包含）之间的实数！")
                self.load_input1.selectAll()
                self.load_input1.setFocus()
        except ValueError:
            QMessageBox.warning(self, "坡顶作用荷载输入错误", "请输入有效的实数！")
            self.load_input1.selectAll()
            self.load_input1.setFocus()
    #选择不同土类型，数值部队的时候，弹出提示对话框
    def checkSoilType(self):
        if self.radio1.isChecked():# 首先检查当前的计算类型是否为"土方直立壁开挖深度计算"
            selected_soil_type = self.soil_type_combobox.currentText()
            # 定义触发警告的土类型列表
            warning_soil_types = ["细砂", "中砂", "粗砂", "砾砂", "角砾", "圆砾", "碎石", "卵石"]
            if selected_soil_type in warning_soil_types:
                # 弹出警告对话框
                ret =QMessageBox.warning(self, "提示信息", "土方直立壁开挖不能选择土粘聚力为0的砂土等类型", QMessageBox.Ok)
                # 如果用户点击了确认按钮
                if ret == QMessageBox.Ok:
                    # 将选择的内容改为列表的第一个选项
                    self.soil_type_combobox.setCurrentIndex(0)
    #检查土的内摩擦角是否在范围内
    def checkInternalFrictionAngle(self):
        try:
            angle = float(self.basic_InternalFrictionAngle.text())
            if not 0 <= angle < 90:
                QMessageBox.warning(self, "土的内摩擦角", "请输入0（包含）到90（不包含）之间的实数！")
                self.basic_InternalFrictionAngle.selectAll()
                self.basic_InternalFrictionAngle.setFocus()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的实数！")
            self.basic_InternalFrictionAngle.selectAll()
            self.basic_InternalFrictionAngle.setFocus()
    #土的粘聚力数值的检查
    def checkSoilCohesion(self):
        try:
            cohesion = float(self.basic_soilCohesion.text())
            if not 0 <= cohesion <= 50:
                QMessageBox.warning(self, "输入错误", "请输入0（包含）到50（包含）之间的实数！")
                self.basic_soilCohesion.selectAll()
                self.basic_soilCohesion.setFocus()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的实数！")
            self.basic_soilCohesion.selectAll()
            self.basic_soilCohesion.setFocus()
    #边坡的坡度角检查
    def checkSlopeAngle(self):
        try:
            angle = float(self.basic_slopeAngle.text())
            if not 0 < angle <= 90:
                QMessageBox.warning(self, "坡度角输入错误", "请输入0（不包含）到90（包含）之间的实数！")
                self.basic_slopeAngle.selectAll()
                self.basic_slopeAngle.setFocus()
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的实数！")
            self.basic_slopeAngle.selectAll()
            self.basic_slopeAngle.setFocus()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    earth_slope_dialog = EarthSlopeDialog()
    earth_slope_dialog.show()
    sys.exit(app.exec_())
