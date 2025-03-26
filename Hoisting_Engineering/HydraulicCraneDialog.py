#液压汽车起重机吊装计算界面
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QRadioButton, QButtonGroup, QGroupBox, QComboBox, QGridLayout, QFormLayout, QSplitter, QWidget, QMessageBox, QFrame
)
import sys
import uuid
from PyQt5.QtCore import Qt
from DataStruDef.EarthSlopeCalculation import VerificationProject
from DataStruDef.HydraulicCraneData import HydraulicCraneData
# para_uuid:
# 类型：UUID 或 None
# 作用：用于唯一标识对话框实例。如果没有提供，则在初始化时生成一个新的UUID。这在需要跟踪多个对话框实例时非常有用。
# para_craneData:
# 类型：字典或 None
# 作用：包含吊装计算所需的初始数据。如果没有提供，则使用默认值初始化。字典中的键值对包括：
# "load_capacity": 吊装能力，以吨为单位。
# "boom_length": 吊臂长度，以米为单位。
# "working_radius": 工作半径，以米为单位。#
class HydraulicCraneDialog(QDialog):
    def __init__(self, uuid=None, data=None):
        super().__init__()
        self.m_name = "液压汽车起重机吊装计算对话框"

        self.uuid = uuid
        self.data = data if data else HydraulicCraneData()
        if uuid:
            self.data.uuid = uuid
        
        self.IsSave = True  # 保存状态标志
        # Add verification project initialization
        self.verification_project = VerificationProject("液压汽车起重机吊装计算")#后续支持修改项目树节点的名称，目前还没有用到

        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("液压汽车起重机吊装计算")
        self.setGeometry(100, 100, 800, 600)  # 设置对话框的初始大小

        main_layout = QVBoxLayout()

        # 1. 基本参数组
        basic_group = QGroupBox("基本参数")
        basic_layout = QGridLayout()
        
        # 吊重输入
        basic_layout.addWidget(QLabel("吊重Gw(吨):"), 0, 0)
        self.crane_weight_edit = QLineEdit(str(self.data.crane_weight))
        self.crane_weight_edit.textChanged.connect(self.on_data_changed)
        basic_layout.addWidget(self.crane_weight_edit, 0, 1)
        
        # 起重动力系数
        basic_layout.addWidget(QLabel("起重动力系数k1:"), 1, 0)
        self.power_factor_edit = QLineEdit(str(self.data.power_factor))
        self.power_factor_edit.textChanged.connect(self.on_data_changed)
        basic_layout.addWidget(self.power_factor_edit, 1, 1)
        
        # 单选按钮组
        radio_group = QButtonGroup(self)
        self.smart_radio = QRadioButton("智能推荐起重机")
        self.custom_radio = QRadioButton("自定义起重机")
        radio_group.addButton(self.smart_radio)
        radio_group.addButton(self.custom_radio)
        self.smart_radio.setChecked(self.data.is_smart_recommendation)
        self.custom_radio.setChecked(not self.data.is_smart_recommendation)
        
        basic_layout.addWidget(self.smart_radio, 2, 0)
        basic_layout.addWidget(self.custom_radio, 2, 1)
        basic_group.setLayout(basic_layout)
        
        # 2. 吊装要求组
        requirements_group = QGroupBox("吊装要求")
        requirements_layout = QGridLayout()
        
        # 子标题
        requirements_layout.addWidget(QLabel("起重机选型"), 0, 0)
        requirements_layout.addWidget(QLabel("起重机相关计算参数"), 0, 1)
        
        # 吊装高度
        requirements_layout.addWidget(QLabel("吊物顶面距地面最大吊装高度h1(m):"), 1, 0)
        self.max_height_edit = QLineEdit(str(self.data.max_lifting_height))
        self.max_height_edit.textChanged.connect(self.on_data_changed)
        requirements_layout.addWidget(self.max_height_edit, 1, 1)
        
        # 最小距离
        requirements_layout.addWidget(QLabel("吊物顶面距起重臂端部的最小距离h2(m):"), 2, 0)
        self.min_distance_edit = QLineEdit(str(self.data.min_boom_distance))
        self.min_distance_edit.textChanged.connect(self.on_data_changed)
        requirements_layout.addWidget(self.min_distance_edit, 2, 1)
        
        # 工作幅度确定方法
        requirements_layout.addWidget(QLabel("工作幅度确定方法:"), 3, 0)
        self.radius_method_combo = QComboBox()
        self.radius_method_combo.addItem("智能确定")
        self.radius_method_combo.setCurrentText(self.data.working_radius_method)
        self.radius_method_combo.currentTextChanged.connect(self.on_data_changed)
        requirements_layout.addWidget(self.radius_method_combo, 3, 1)
        
        # 最小工作幅度
        requirements_layout.addWidget(QLabel("场地要求的最小工作幅度(m):"), 4, 0)
        self.min_radius_edit = QLineEdit(str(self.data.min_working_radius))
        self.min_radius_edit.textChanged.connect(self.on_data_changed)
        requirements_layout.addWidget(self.min_radius_edit, 4, 1)
        
        requirements_group.setLayout(requirements_layout)
        
        # 3. 安全距离复核组
        safety_group = QGroupBox("吊物与起重臂安全距离复核")
        safety_layout = QGridLayout()
        
        # 水平距离
        safety_layout.addWidget(QLabel("特性弧线最高吊钩（起重臂终端）中心的水平距离b(m):"), 0, 0)
        self.horizontal_distance_edit = QLineEdit(str(self.data.horizontal_distance))
        self.horizontal_distance_edit.textChanged.connect(self.on_data_changed)
        safety_layout.addWidget(self.horizontal_distance_edit, 0, 1)
        
        # 安全距离
        safety_layout.addWidget(QLabel("安装构件边缘距起重臂中心的最小安全距离L(m):"), 1, 0)
        self.safety_distance_edit = QLineEdit(str(self.data.min_safety_distance))
        self.safety_distance_edit.textChanged.connect(self.on_data_changed)
        safety_layout.addWidget(self.safety_distance_edit, 1, 1)
        
        safety_group.setLayout(safety_layout)
        
        # 添加所有组到主布局
        main_layout.addWidget(basic_group)
        main_layout.addWidget(requirements_group)
        main_layout.addWidget(safety_group)
        
        self.setLayout(main_layout)

    def on_data_changed(self):
        """当数据改变时的处理函数"""
        self.IsSave = False
        
    def updateCalculationData(self):
        """更新计算数据"""
        try:
            self.data.crane_weight = float(self.crane_weight_edit.text())
            self.data.power_factor = float(self.power_factor_edit.text())
            self.data.is_smart_recommendation = self.smart_radio.isChecked()
            self.data.max_lifting_height = float(self.max_height_edit.text())
            self.data.min_boom_distance = float(self.min_distance_edit.text())
            self.data.working_radius_method = self.radius_method_combo.currentText()
            self.data.min_working_radius = float(self.min_radius_edit.text())
            self.data.horizontal_distance = float(self.horizontal_distance_edit.text())
            self.data.min_safety_distance = float(self.safety_distance_edit.text())
            
            self.IsSave = True
            return self.data
            
        except ValueError as e:
            print(f"数据转换错误: {str(e)}")
            return None
            
    def Getuuid(self):
        """获取对话框的UUID"""
        return self.uuid

if __name__ == '__main__':
    app = QApplication(sys.argv)
    crane_dialog = HydraulicCraneDialog()
    crane_dialog.show()
    sys.exit(app.exec_()) 