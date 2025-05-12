from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QGridLayout, QGroupBox,
                             QTableWidget, QTableWidgetItem, QPushButton, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import os

class CraneParametersDialog(QWidget):
    """起重机相关计算参数子对话框"""
    data_changed = pyqtSignal()  # 数据改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 起重机自重荷载选择（不在group内）
        weight_layout = QHBoxLayout()
        weight_layout.addWidget(QLabel("起重机自重荷载:"))
        self.weight_combo = QComboBox()
        self.weight_combo.addItem("按说明书轴荷")
        weight_layout.addWidget(self.weight_combo)
        weight_layout.addStretch(1)
        layout.addLayout(weight_layout)
        # 起重机轴距及轴荷分组
        main_group = QGroupBox("起重机轴距及轴荷")
        main_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 10pt; }")
        main_layout = QVBoxLayout(main_group)
        # 轴数、第一排车轮荷载
        axle_layout = QGridLayout()
        axle_layout.addWidget(QLabel("汽车起重机轴数:"), 0, 0)
        self.axle_count_edit = QLineEdit("4")
        axle_layout.addWidget(self.axle_count_edit, 0, 1)
        axle_layout.addWidget(QLabel("第1排车轮荷载(吨):"), 1, 0)
        self.first_axle_load_edit = QLineEdit("8")
        axle_layout.addWidget(self.first_axle_load_edit, 1, 1)
        main_layout.addLayout(axle_layout)
        # 轴距表格
        self.axle_table = QTableWidget()
        self.init_axle_table()
        main_layout.addWidget(self.axle_table)
        # 后支腿距后后排车轮距离
        rear_leg_layout = QHBoxLayout()
        rear_leg_layout.addWidget(QLabel("后支腿距后后排车轮距离s1(m):"))
        self.rear_leg_distance_edit = QLineEdit("1.5")
        rear_leg_layout.addWidget(self.rear_leg_distance_edit)
        main_layout.addLayout(rear_leg_layout)
        layout.addWidget(main_group)
        
        # 其它参数
        params_group = QGroupBox("其它参数")
        params_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 10pt; }")
        params_layout = QGridLayout()
        
        # 汽车起重机自重
        params_layout.addWidget(QLabel("汽车起重机自重(吨):"), 0, 0)
        self.crane_weight_edit = QLineEdit("42")
        params_layout.addWidget(self.crane_weight_edit, 0, 1)
        
        # 是否有活动配重
        params_layout.addWidget(QLabel("是否有活动配重:"), 1, 0)
        self.has_active_weight_combo = QComboBox()
        self.has_active_weight_combo.addItem("是")
        params_layout.addWidget(self.has_active_weight_combo, 1, 1)
        
        # 活动配重重量
        params_layout.addWidget(QLabel("活动配重重量(吨):"), 2, 0)
        self.active_weight_edit = QLineEdit("30")
        params_layout.addWidget(self.active_weight_edit, 2, 1)
        
        # 活动配重距转中心距离
        params_layout.addWidget(QLabel("活动配重距转中心距离Ld(m):"), 3, 0)
        self.active_weight_distance_edit = QLineEdit("2.175")
        params_layout.addWidget(self.active_weight_distance_edit, 3, 1)
        
        # 支腿纵向距离
        params_layout.addWidget(QLabel("支腿纵向距离s2(m):"), 4, 0)
        self.leg_length_edit = QLineEdit("6")
        params_layout.addWidget(self.leg_length_edit, 4, 1)
        
        # 支腿横向距离
        params_layout.addWidget(QLabel("支腿横向距离s3(m):"), 5, 0)
        self.leg_width_edit = QLineEdit("7.2")
        params_layout.addWidget(self.leg_width_edit, 5, 1)
        
        # 后支腿距转中心距离
        params_layout.addWidget(QLabel("后支腿距转中心距离Lh(m):"), 6, 0)
        self.rear_leg_center_edit = QLineEdit("2.175")
        params_layout.addWidget(self.rear_leg_center_edit, 6, 1)
        
        # 抗倾覆安全系数
        params_layout.addWidget(QLabel("抗倾覆安全系数:"), 7, 0)
        self.safety_factor_edit = QLineEdit("1.2")
        params_layout.addWidget(self.safety_factor_edit, 7, 1)
        
        # 地基承载力计算
        params_layout.addWidget(QLabel("单根支腿基础面积Ad1(m2):"), 8, 0)
        self.foundation_area_edit = QLineEdit("10")
        params_layout.addWidget(self.foundation_area_edit, 8, 1)
        
        # 地基土类型
        params_layout.addWidget(QLabel("地基土类型:"), 9, 0)
        self.soil_type_combo = QComboBox()
        self.soil_type_combo.addItem("碎石土")
        params_layout.addWidget(self.soil_type_combo, 9, 1)
        
        # 地基承载力特征值
        fak_row = QHBoxLayout()
        fak_label = QLabel("地基承载力特征值fak(kPa):")
        fak_row.addWidget(fak_label)
        self.soil_strength_edit = QLineEdit("360")
        fak_row.addWidget(self.soil_strength_edit)
        # 新增：圆形红框按钮
        self.fak_btn = QPushButton("🐎")
        self.fak_btn.setFixedSize(24, 24)
        self.fak_btn.setStyleSheet("border: 2px solid red; border-radius: 12px; color: red; font-weight: bold; background: white;")
        fak_row.addWidget(self.fak_btn)
        fak_row.addStretch(1)
        params_layout.addLayout(fak_row, 10, 0, 1, 2)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        self.setLayout(layout)
        
        # 连接信号
        self.connect_signals()
        
    def init_axle_table(self):
        """初始化轴距表格"""
        self.axle_table.setColumnCount(3)
        self.axle_table.setRowCount(3)
        
        # 设置表头
        headers = ["第i排车轮", "依次轴距(mm)", "轴荷(吨)"]
        self.axle_table.setHorizontalHeaderLabels(headers)
        
        # 设置数据
        data = [
            ["2", "1450", "8.000"],
            ["3", "4000", "13.000"],
            ["4", "1350", "13.000"]
        ]
        
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                self.axle_table.setItem(i, j, QTableWidgetItem(value))
                
    def connect_signals(self):
        """连接所有信号"""
        # 编辑框信号
        self.axle_count_edit.textChanged.connect(self.on_data_changed)
        self.first_axle_load_edit.textChanged.connect(self.on_data_changed)
        self.rear_leg_distance_edit.textChanged.connect(self.on_data_changed)
        self.crane_weight_edit.textChanged.connect(self.on_data_changed)
        self.active_weight_edit.textChanged.connect(self.on_data_changed)
        self.active_weight_distance_edit.textChanged.connect(self.on_data_changed)
        self.leg_length_edit.textChanged.connect(self.on_data_changed)
        self.leg_width_edit.textChanged.connect(self.on_data_changed)
        self.rear_leg_center_edit.textChanged.connect(self.on_data_changed)
        self.safety_factor_edit.textChanged.connect(self.on_data_changed)
        self.foundation_area_edit.textChanged.connect(self.on_data_changed)
        self.soil_strength_edit.textChanged.connect(self.on_data_changed)
        
        # 下拉框信号
        self.weight_combo.currentTextChanged.connect(self.on_data_changed)
        self.has_active_weight_combo.currentTextChanged.connect(self.on_data_changed)
        self.soil_type_combo.currentTextChanged.connect(self.on_data_changed)
        
        # 新增：圆形红框按钮信号
        self.fak_btn.clicked.connect(self.show_fak_table_dialog)
        
    def on_data_changed(self):
        """数据改变时发出信号"""
        self.data_changed.emit()
        
    def get_data(self):
        """获取对话框数据"""
        # 获取轴距表格数据
        axle_data = []
        for row in range(self.axle_table.rowCount()):
            row_data = []
            for col in range(self.axle_table.columnCount()):
                item = self.axle_table.item(row, col)
                row_data.append(item.text() if item else "")
            axle_data.append(row_data)
            
        return {
            'weight_load_type': self.weight_combo.currentText(),
            'axle_count': int(self.axle_count_edit.text()),
            'first_axle_load': float(self.first_axle_load_edit.text()),
            'axle_data': axle_data,
            'rear_leg_distance': float(self.rear_leg_distance_edit.text()),
            'crane_weight': float(self.crane_weight_edit.text()),
            'has_active_weight': self.has_active_weight_combo.currentText(),
            'active_weight': float(self.active_weight_edit.text()),
            'active_weight_distance': float(self.active_weight_distance_edit.text()),
            'leg_length': float(self.leg_length_edit.text()),
            'leg_width': float(self.leg_width_edit.text()),
            'rear_leg_center': float(self.rear_leg_center_edit.text()),
            'safety_factor': float(self.safety_factor_edit.text()),
            'foundation_area': float(self.foundation_area_edit.text()),
            'soil_type': self.soil_type_combo.currentText(),
            'soil_strength': float(self.soil_strength_edit.text())
        }
        
    def set_data(self, data):
        """设置对话框数据"""
        self.weight_combo.setCurrentText(data.get('weight_load_type', '按说明书轴荷'))
        self.axle_count_edit.setText(str(data.get('axle_count', 4)))
        self.first_axle_load_edit.setText(str(data.get('first_axle_load', 8)))
        self.rear_leg_distance_edit.setText(str(data.get('rear_leg_distance', 1.5)))
        self.crane_weight_edit.setText(str(data.get('crane_weight', 42)))
        self.has_active_weight_combo.setCurrentText(data.get('has_active_weight', '是'))
        self.active_weight_edit.setText(str(data.get('active_weight', 30)))
        self.active_weight_distance_edit.setText(str(data.get('active_weight_distance', 2.175)))
        self.leg_length_edit.setText(str(data.get('leg_length', 6)))
        self.leg_width_edit.setText(str(data.get('leg_width', 7.2)))
        self.rear_leg_center_edit.setText(str(data.get('rear_leg_center', 2.175)))
        self.safety_factor_edit.setText(str(data.get('safety_factor', 1.2)))
        self.foundation_area_edit.setText(str(data.get('foundation_area', 10)))
        self.soil_type_combo.setCurrentText(data.get('soil_type', '碎石土'))
        self.soil_strength_edit.setText(str(data.get('soil_strength', 360)))
        
    def show_fak_table_dialog(self):
        """弹出地基承载力标准值图片对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("地基承载力标准值")
        vbox = QVBoxLayout(dialog)
        label = QLabel()
        # 假设图片名为soil_fak_table.png，放在当前py文件同目录
        img_path = os.path.join(os.path.dirname(__file__), "soil_fak_table.png")
        pix = QPixmap(img_path)
        label.setPixmap(pix)
        label.setScaledContents(True)
        vbox.addWidget(label)
        dialog.setLayout(vbox)
        dialog.setModal(True)
        dialog.exec_() 