#液压汽车起重机吊装计算界面
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QRadioButton, QButtonGroup, QGroupBox, QComboBox, QGridLayout, QFormLayout, QSplitter, QWidget, QMessageBox, QFrame, QTabWidget
)
import sys
import uuid
from PyQt5.QtCore import Qt
from DataStruDef.EarthSlopeCalculation import VerificationProject
from DataStruDef.HydraulicCraneData import HydraulicCraneData
from .CraneRequirementsDialog import CraneRequirementsDialog
from .CraneSelectionDialog import CraneSelectionDialog
from .CraneParametersDialog import CraneParametersDialog
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
        
        # 2. 创建标签页组件
        tab_widget = QTabWidget()
        
        # 创建三个子对话框
        self.requirements_dialog = CraneRequirementsDialog(self)
        self.selection_dialog = CraneSelectionDialog(self)
        self.parameters_dialog = CraneParametersDialog(self)
        
        # 添加标签页
        tab_widget.addTab(self.requirements_dialog, "吊装要求")
        tab_widget.addTab(self.selection_dialog, "起重机选型")
        tab_widget.addTab(self.parameters_dialog, "起重机相关计算参数")
        
        # 连接子对话框的数据改变信号
        self.requirements_dialog.data_changed.connect(self.on_data_changed)
        self.selection_dialog.data_changed.connect(self.on_data_changed)
        self.parameters_dialog.data_changed.connect(self.on_data_changed)
        
        # 添加所有组件到主布局
        main_layout.addWidget(basic_group)
        main_layout.addWidget(tab_widget)
        
        self.setLayout(main_layout)

    def on_data_changed(self):
        """当数据改变时的处理函数"""
        self.IsSave = False
        
    def updateCalculationData(self):
        """更新计算数据"""
        try:
            # 更新基本参数
            self.data.crane_weight = float(self.crane_weight_edit.text())
            self.data.power_factor = float(self.power_factor_edit.text())
            self.data.is_smart_recommendation = self.smart_radio.isChecked()
            
            # 获取子对话框数据
            requirements_data = self.requirements_dialog.get_data()
            selection_data = self.selection_dialog.get_data()
            parameters_data = self.parameters_dialog.get_data()
            
            # 更新吊装要求数据
            self.data.max_lifting_height = requirements_data['max_lifting_height']
            self.data.min_boom_distance = requirements_data['min_boom_distance']
            self.data.working_radius_method = requirements_data['working_radius_method']
            self.data.min_working_radius = requirements_data['min_working_radius']
            
            # 将选型和参数数据存储到计算结果字典中
            self.data.calculation_results.update({
                'crane_selection': selection_data,
                'crane_parameters': parameters_data
            })
            
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