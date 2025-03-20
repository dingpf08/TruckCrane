#液压汽车起重机吊装计算界面
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QRadioButton, QGroupBox, QComboBox, QGridLayout, QFormLayout, QSplitter, QWidget, QMessageBox
)
import sys
import uuid
from PyQt5.QtCore import Qt
from DataStruDef.EarthSlopeCalculation import VerificationProject
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
    def __init__(self, para_uuid=None, para_craneData=None):
        super().__init__()
        self.m_name = "液压汽车起重机吊装计算对话框"

        self.uuid = None  # 能够唯一定位对话框的符号
        self.crane_data = None  # 吊装数据
        self.IsSave = True  # 是否保存
        # Add verification project initialization
        self.verification_project = VerificationProject("液压汽车起重机吊装计算")

        if para_uuid is None:
            self.uuid = uuid.uuid4()  # 生成一个唯一的UUID
            print(f"自动生成的uuid为：汽车吊界面的uuid为：{str(self.uuid)}")
        else:
            self.uuid = para_uuid
            print(f"传入的uuid为：汽车吊界面的uuid为：{str(self.uuid)}")
        if para_craneData is None:
            # 初始化默认的吊装数据
            self.crane_data = {
                "load_capacity": 30.0,  # 吊装能力
                "boom_length": 50.0,  # 吊臂长度
                "working_radius": 20.0  # 工作半径
            }
            print(f"自己初始化参数：初始化的吊装数据: 吊装能力: {self.crane_data['load_capacity']}吨, 吊臂长度: {self.crane_data['boom_length']}米, 工作半径: {self.crane_data['working_radius']}米")
        else:
            self.crane_data = para_craneData#汽车吊的参数
            print(f"外面传入的参数：自己初始化参数：初始化的吊装数据: 吊装能力: {self.crane_data['load_capacity']}吨, 吊臂长度: {self.crane_data['boom_length']}米, 工作半径: {self.crane_data['working_radius']}米")

        print(f"初始化的吊装数据: 吊装能力: {self.crane_data['load_capacity']}吨, 吊臂长度: {self.crane_data['boom_length']}米, 工作半径: {self.crane_data['working_radius']}米")

        self.initUI()

    #这个函数每个对话框都要相同，否则程序会崩溃，因为是被设计到流程中的
    def updateCalculationData(self):
        """根据当前的对话框内容更新吊装数据。"""
        self.crane_data["load_capacity"] = float(self.load_capacity_input.text())
        self.crane_data["boom_length"] = float(self.boom_length_input.text())
        self.crane_data["working_radius"] = float(self.working_radius_input.text())
        return self.crane_data

    def updateCraneData(self):
        """根据当前的对话框内容更新吊装数据。"""
        self.crane_data["load_capacity"] = float(self.load_capacity_input.text())
        self.crane_data["boom_length"] = float(self.boom_length_input.text())
        self.crane_data["working_radius"] = float(self.working_radius_input.text())
        return self.crane_data

    def initUI(self):
        self.setWindowTitle('液压汽车起重机吊装计算')
        self.setGeometry(100, 100, 800, 600)  # 设置对话框的初始大小

        main_layout = QVBoxLayout()

        # 吊装参数区域
        crane_group = QGroupBox("吊装参数")
        crane_layout = QFormLayout()

        self.load_capacity_input = QLineEdit()
        self.load_capacity_input.setText(str(self.crane_data["load_capacity"]))
        self.load_capacity_input.textChanged.connect(self.markUnsavedChanges)
        crane_layout.addRow(QLabel("吊装能力 (吨):"), self.load_capacity_input)

        self.boom_length_input = QLineEdit()
        self.boom_length_input.setText(str(self.crane_data["boom_length"]))
        self.boom_length_input.textChanged.connect(self.markUnsavedChanges)
        crane_layout.addRow(QLabel("吊臂长度 (米):"), self.boom_length_input)

        self.working_radius_input = QLineEdit()
        self.working_radius_input.setText(str(self.crane_data["working_radius"]))
        self.working_radius_input.textChanged.connect(self.markUnsavedChanges)
        crane_layout.addRow(QLabel("工作半径 (米):"), self.working_radius_input)

        crane_group.setLayout(crane_layout)
        main_layout.addWidget(crane_group)

        self.setLayout(main_layout)

    def markUnsavedChanges(self):
        """标记对话框内容已修改，未保存。"""
        self.IsSave = False

    def Getuuid(self):
        """返回对话框的UUID。"""
        return self.uuid

if __name__ == '__main__':
    app = QApplication(sys.argv)
    crane_dialog = HydraulicCraneDialog()
    crane_dialog.show()
    sys.exit(app.exec_()) 