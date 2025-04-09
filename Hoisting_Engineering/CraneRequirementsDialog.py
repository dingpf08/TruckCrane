from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QGridLayout, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal

class CraneRequirementsDialog(QWidget):
    """吊装要求子对话框"""
    data_changed = pyqtSignal()  # 数据改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 创建吊装要求组
        requirements_group = QGroupBox("吊装要求")
        grid_layout = QGridLayout()
        
        # 吊装高度
        grid_layout.addWidget(QLabel("吊物顶面距地面最大吊装高度h1(m):"), 0, 0)
        self.max_height_edit = QLineEdit("10")
        grid_layout.addWidget(self.max_height_edit, 0, 1)
        
        # 最小距离
        grid_layout.addWidget(QLabel("吊物顶面距起重臂端部的最小距离h2(m):"), 1, 0)
        self.min_distance_edit = QLineEdit("3")
        grid_layout.addWidget(self.min_distance_edit, 1, 1)
        
        # 工作幅度确定方法
        grid_layout.addWidget(QLabel("工作幅度确定方法:"), 2, 0)
        self.radius_method_combo = QComboBox()
        self.radius_method_combo.addItem("智能确定")
        grid_layout.addWidget(self.radius_method_combo, 2, 1)
        
        # 最小工作幅度
        grid_layout.addWidget(QLabel("场地要求的最小工作幅度(m):"), 3, 0)
        self.min_radius_edit = QLineEdit("4")
        grid_layout.addWidget(self.min_radius_edit, 3, 1)
        
        requirements_group.setLayout(grid_layout)
        layout.addWidget(requirements_group)
        
        # 创建吊物与起重臂安全距离复核组
        safety_group = QGroupBox("吊物与起重臂安全距离复核")
        safety_layout = QGridLayout()
        
        # 构件边缘距起重臂距离
        safety_layout.addWidget(QLabel("构件边缘距起重臂距离(m):"), 0, 0)
        self.edge_distance_edit = QLineEdit("1")
        safety_layout.addWidget(self.edge_distance_edit, 0, 1)
        
        # 安装构件边缘距起重臂中心的最小安全距离
        safety_layout.addWidget(QLabel("安装构件边缘距起重臂中心的最小安全距离ε(m):"), 1, 0)
        self.safety_distance_edit = QLineEdit("1")
        safety_layout.addWidget(self.safety_distance_edit, 1, 1)
        
        safety_group.setLayout(safety_layout)
        layout.addWidget(safety_group)
        
        # 连接信号
        self.max_height_edit.textChanged.connect(self.on_data_changed)
        self.min_distance_edit.textChanged.connect(self.on_data_changed)
        self.radius_method_combo.currentTextChanged.connect(self.on_data_changed)
        self.min_radius_edit.textChanged.connect(self.on_data_changed)
        self.edge_distance_edit.textChanged.connect(self.on_data_changed)
        self.safety_distance_edit.textChanged.connect(self.on_data_changed)
        
        self.setLayout(layout)
        
    def on_data_changed(self):
        """数据改变时发出信号"""
        self.data_changed.emit()
        
    def get_data(self):
        """获取对话框数据"""
        return {
            'max_lifting_height': float(self.max_height_edit.text()),
            'min_boom_distance': float(self.min_distance_edit.text()),
            'working_radius_method': self.radius_method_combo.currentText(),
            'min_working_radius': float(self.min_radius_edit.text()),
            'edge_distance': float(self.edge_distance_edit.text()),
            'safety_distance': float(self.safety_distance_edit.text())
        }
        
    def set_data(self, data):
        """设置对话框数据"""
        self.max_height_edit.setText(str(data.get('max_lifting_height', 10)))
        self.min_distance_edit.setText(str(data.get('min_boom_distance', 3)))
        self.radius_method_combo.setCurrentText(data.get('working_radius_method', '智能确定'))
        self.min_radius_edit.setText(str(data.get('min_working_radius', 4)))
        self.edge_distance_edit.setText(str(data.get('edge_distance', 1)))
        self.safety_distance_edit.setText(str(data.get('safety_distance', 1))) 