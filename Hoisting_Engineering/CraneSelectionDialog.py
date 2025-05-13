"""起重机选型子对话框"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QGridLayout, QGroupBox,
                             QPushButton, QTableWidget, QTableWidgetItem, QCheckBox,
                             QTabWidget, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from CommonDialogs.CraneSettingsDialog import CraneSettingsDialog

class CraneSelectionDialog(QWidget):
    """起重机选型子对话框"""
    data_changed = pyqtSignal()  # 数据改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # 连接厂家按钮点击事件
        self.manufacturer_button.clicked.connect(self.show_crane_settings_dialog)
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 起重机选择区域
        selection_layout = QGridLayout()
        
        # 起重机推荐方式
        selection_layout.addWidget(QLabel("起重机推荐方式:"), 0, 0)
        self.recommendation_button = QPushButton("推荐")
        selection_layout.addWidget(self.recommendation_button, 0, 1)
        
        # 添加推荐类型下拉框
        self.recommendation_type_combo = QComboBox()
        self.recommendation_type_combo.addItems([
            "指定起重机厂家推荐",
            "指定起重机型号推荐",
            "指定起重机工况推荐"
        ])
        selection_layout.addWidget(self.recommendation_type_combo, 0, 2)
        
        # 汽车起重机厂家
        selection_layout.addWidget(QLabel("汽车起重机厂家:"), 1, 0)
        self.manufacturer_button = QPushButton("...")
        self.manufacturer_button.setStyleSheet("font-weight: bold; color: white; background-color: #0078d7; border-radius: 4px; min-width: 28px; max-width: 28px; min-height: 24px;")
        selection_layout.addWidget(self.manufacturer_button, 1, 1)
        self.manufacturer_combo = QComboBox()
        self.manufacturer_combo.addItems(["三一", "中联重科", "徐工"])
        selection_layout.addWidget(self.manufacturer_combo, 1, 2)
        
        # 创建推荐参数（起重机型号）组
        model_group = QGroupBox("推荐参数（起重机型号）")
        model_layout = QGridLayout()
        
        # 起重机型号
        model_layout.addWidget(QLabel("起重机型号:"), 0, 0)
        self.crane_model_combo = QComboBox()
        self.crane_model_combo.addItem("STC500")
        model_layout.addWidget(self.crane_model_combo, 0, 1)
        
        model_group.setLayout(model_layout)
        selection_layout.addWidget(model_group, 2, 0, 2, 3)
        
        # 起重能力及吊装工况验算复选框
        self.capacity_check = QCheckBox("起重能力及吊装工况验算")
        self.capacity_check.setChecked(True)
        selection_layout.addWidget(self.capacity_check, 4, 0, 1, 3)
        
        # 创建推荐参数TabWidget
        self.recommend_tab = QTabWidget()
        # 推荐参数（吊装工况）Tab
        self.tab_condition = QWidget()
        self.tab_condition.setToolTip("推荐参数（吊装工况）")
        tab_condition_layout = QVBoxLayout(self.tab_condition)
        # 新增：上方控件区（两排，左对齐，纵向对齐）
        condition_top_layout = QFormLayout()
        self.boom_combo = QComboBox()
        self.boom_combo.addItem("主臂")
        condition_top_layout.addRow(QLabel("起重臂:"), self.boom_combo)
        self.condition_detail_combo = QComboBox()
        self.condition_detail_combo.addItems(["配重1.2t，支腿全"])
        condition_top_layout.addRow(QLabel("具体吊装工况:"), self.condition_detail_combo)
        tab_condition_layout.addLayout(condition_top_layout)
        # 创建表格
        self.condition_table = QTableWidget()
        self.condition_table.setColumnCount(6)
        self.condition_table.setRowCount(17)
        headers = ["幅度/主臂长(m)", "9.6", "15.08", "20.56", "26.04", "31.52"]
        self.condition_table.setHorizontalHeaderLabels(headers)
        radius_values = [str(x) for x in [3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 8, 9, 10, 11, 12, 16, 18, 20, 22, 24, 26]]
        for i, value in enumerate([str(x) for x in [3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 8, 9, 10, 11, 12, 16, 18, 20, 22, 24, 26]][:17]):
            self.condition_table.setItem(i, 0, QTableWidgetItem(value))
        table_data = [
            ["12", "10.8", "", "", ""],
            ["12", "10.8", "8.7", "", ""],
            ["12", "10.6", "8.7", "", ""],
            ["11.8", "10.4", "8.7", "6.8", ""],
            ["11", "9.7", "8.2", "6.8", ""],
            ["9.9", "9", "7.9", "6.7", ""],
            ["9.1", "8.5", "7.6", "6.2", "4.8"],
            ["8.4", "7.7", "7.35", "5.9", "4.8"],
            ["7.8", "7.1", "6.95", "5.4", "4.1"],
            ["6.2", "5.95", "4.8", "4.1", ""],
            ["5.2", "5.3", "4.35", "3.8", ""],
            ["3.6", "3.9", "3.6", "3.2", ""],
            ["3", "3.3", "2.9", "2.95", ""],
            ["2.2", "2.2", "2.1", "2", ""],
            ["1.8", "1.7", "1.6", "", ""],
            ["1.4", "1.2", "1.3", "", ""],
            ["0.8", "0.85", "", "", ""],
            ["0.65", "", "", "", ""],
            ["", "", "", "", ""]
        ]
        for i, row in enumerate(table_data):
            for j, value in enumerate(row):
                if value:
                    self.condition_table.setItem(i, j + 1, QTableWidgetItem(value))
        tab_condition_layout.addWidget(self.condition_table)
        self.recommend_tab.addTab(self.tab_condition, "推荐参数（吊装工况）")
        # 推荐参数（幅度、臂长、额定起重量）Tab
        self.tab_parameters = QWidget()
        self.tab_parameters.setToolTip("推荐参数（幅度、臂长、额定起重量）")
        tab_parameters_layout = QVBoxLayout(self.tab_parameters)
        # 主臂铰链中心至地面距离
        self.edit_hinge_to_ground = QLineEdit("3.05")
        row_hinge_to_ground = QHBoxLayout()
        row_hinge_to_ground.addWidget(QLabel("主臂铰链中心至地面距离h1(m):"))
        row_hinge_to_ground.addWidget(self.edit_hinge_to_ground)
        tab_parameters_layout.addLayout(row_hinge_to_ground)
        # 主臂铰链中心至回转中心距离
        self.edit_hinge_to_rotation = QLineEdit("1.973")
        row_hinge_to_rotation = QHBoxLayout()
        row_hinge_to_rotation.addWidget(QLabel("主臂铰链中心至回转中心a1(m):"))
        row_hinge_to_rotation.addWidget(self.edit_hinge_to_rotation)
        tab_parameters_layout.addLayout(row_hinge_to_rotation)
        # 推荐参数分组
        recommend_group = QGroupBox("推荐参数")
        recommend_form = QFormLayout(recommend_group)
        # 设计主臂长
        self.edit_boom_length = QLineEdit("15.44")
        recommend_form.addRow(QLabel("设计主臂长L1(m):[范围6~37]"), self.edit_boom_length)
        # 幅度
        self.edit_radius = QLineEdit("3")
        recommend_form.addRow(QLabel("设计幅度R(m):[范围3~26]"), self.edit_radius)
        # 主臂仰角
        self.edit_boom_angle = QLineEdit("71.21")
        recommend_form.addRow(QLabel("主臂仰角(°):[范围7~76]"), self.edit_boom_angle)
        # 额定起重量
        self.edit_rated_weight = QLineEdit("40")
        recommend_form.addRow(QLabel("额定起重量(qt):"), self.edit_rated_weight)
        tab_parameters_layout.addWidget(recommend_group)
        self.recommend_tab.addTab(self.tab_parameters, "推荐参数（幅度、臂长、额定起重量）")
        # 添加所有控件到主布局
        main_group = QGroupBox()
        main_layout = QVBoxLayout(main_group)
        main_layout.addLayout(selection_layout)
        main_layout.addWidget(self.recommend_tab)
        layout.addWidget(main_group)
        self.setLayout(layout)
        
        # 连接信号
        self.recommendation_button.clicked.connect(self.on_data_changed)
        self.recommendation_type_combo.currentTextChanged.connect(self.on_data_changed)
        self.manufacturer_combo.currentTextChanged.connect(self.on_data_changed)
        self.crane_model_combo.currentTextChanged.connect(self.on_data_changed)
        self.capacity_check.stateChanged.connect(self.on_data_changed)
        self.condition_table.cellChanged.connect(self.on_data_changed)
        
        # self.smart_radio.setToolTip('注：选择"智能推荐起重机"，点击下方"推荐"按钮，可对起吊高度、"起重能力"、"吊物安全距离"进行推荐择优！')
        
        self.condition_table.setToolTip("推荐参数（吊装工况）表格")
        
    def init_table(self):
        """初始化表格"""
        self.table.setColumnCount(7)
        self.table.setRowCount(15)
        self.table.setToolTip("推荐参数（幅度、臂长、额定起重量）表格")
        
        # 设置表头
        headers = ["幅度\\主臂长", "11.5", "15.44", "19.38", "27.25", "35.15", "39"]
        self.table.setHorizontalHeaderLabels(headers)
        
        # 设置第一列（幅度值）
        radius_values = ["6.5", "7", "7.5", "8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24", "26"]
        for i, value in enumerate(radius_values):
            self.table.setItem(i, 0, QTableWidgetItem(value))
            
        # 设置示例数据
        example_data = [
            ["25.8", "25.5", "23.9", "19.5", "14", ""],
            ["23.5", "23.2", "21.5", "18", "14", "11.5"],
            ["21.4", "21.2", "18.6", "16.8", "13.5", "11.5"],
            ["19.5", "19.3", "17", "15.8", "12.7", "11"],
            ["15.3", "15", "13.7", "14", "11.7", "10.5"],
            ["", "11.7", "10.9", "12", "10.7", "10"],
            ["", "9.6", "9", "9.9", "9.4", "9"],
            ["", "8", "8", "9", "8.5", "8"],
            ["", "", "5.3", "6.3", "6.6", "6.3"],
            ["", "", "3.5", "4.7", "5", "5"],
            ["", "", "", "3.5", "4", "4"],
            ["", "", "", "2.5", "3.1", "3.2"],
            ["", "", "", "1.9", "2.2", "2.4"],
            ["", "", "", "1.3", "1.7", "1.8"],
            ["", "", "", "", "1.2", "1.3"]
        ]
        
        # 填充数据
        for i, row in enumerate(example_data):
            for j, value in enumerate(row):
                if value:
                    self.table.setItem(i, j + 1, QTableWidgetItem(value))
    
    def on_data_changed(self):
        """数据改变时发出信号"""
        self.data_changed.emit()
        
    def get_data(self):
        """获取对话框数据"""
        return {
            'recommendation_clicked': False,  # 用于标记推荐按钮是否被点击
            'recommendation_type': self.recommendation_type_combo.currentText(),
            'manufacturer': self.manufacturer_combo.currentText(),
            'Str_crane_modelName': self.crane_model_combo.currentText(),
            'capacity_check': self.capacity_check.isChecked(),
            # 'boom_type': self.boom_combo.currentText(),  # 已移除
            # 'condition_detail': self.condition_detail_combo.currentText()  # 已移除
        }
        
    def set_data(self, data):
        """设置对话框数据"""
        self.recommendation_type_combo.setCurrentText(data.get('recommendation_type', '指定起重机厂家推荐'))
        self.manufacturer_combo.setCurrentText(data.get('manufacturer', '三一'))
        self.crane_model_combo.setCurrentText(data.get('Str_crane_modelName', 'STC500'))
        self.capacity_check.setChecked(data.get('capacity_check', True))
        # self.boom_combo.setCurrentText(data.get('boom_type', '主臂'))  # 已移除
        # self.condition_detail_combo.setCurrentText(data.get('condition_detail', '固定配重30t，支腿全伸，需要二节臂时满伸'))  # 已移除

    def show_crane_settings_dialog(self):
        """弹出起重机械设置对话框（模态）"""
        dialog = CraneSettingsDialog(self)
        dialog.exec_() 