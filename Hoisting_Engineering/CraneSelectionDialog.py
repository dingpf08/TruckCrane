from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QComboBox, QGridLayout, QGroupBox,
                             QPushButton, QTableWidget, QTableWidgetItem, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal

class CraneSelectionDialog(QWidget):
    """起重机选型子对话框"""
    data_changed = pyqtSignal()  # 数据改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
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
        self.manufacturer_combo = QComboBox()
        self.manufacturer_combo.addItems(["三一", "中联重科", "徐工"])
        selection_layout.addWidget(self.manufacturer_combo, 1, 1, 1, 2)
        
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
        
        # 创建推荐参数（吊装工况）组
        condition_group = QGroupBox("推荐参数（吊装工况）")
        condition_layout = QGridLayout()
        
        # 起重臂
        condition_layout.addWidget(QLabel("起重臂:"), 0, 0)
        self.boom_combo = QComboBox()
        self.boom_combo.addItem("主臂")
        condition_layout.addWidget(self.boom_combo, 0, 1)
        
        # 具体吊装工况
        condition_layout.addWidget(QLabel("具体吊装工况:"), 1, 0)
        self.condition_detail_combo = QComboBox()
        self.condition_detail_combo.addItems([
            "固定配重30t，支腿全伸，需要二节臂时满伸",
            "固定配重30t，支腿全伸，需要二节臂时不满伸",
            "固定配重30t+活动配重20t，支腿全伸，需要二节臂时满伸",
            "固定配重30t+活动配重20t，支腿全伸，需要二节臂时不满伸"
        ])
        condition_layout.addWidget(self.condition_detail_combo, 1, 1)
        
        # 添加吊装工况表格按钮
        self.condition_table_button = QPushButton("显示工况表格")
        condition_layout.addWidget(self.condition_table_button, 2, 0, 1, 2)
        
        condition_group.setLayout(condition_layout)
        selection_layout.addWidget(condition_group, 5, 0, 3, 3)
        
        # 创建推荐参数（幅度、臂长、额定起重量）组
        parameters_group = QGroupBox("推荐参数（幅度、臂长、额定起重量）")
        parameters_layout = QGridLayout()
        
        # 添加表格
        self.table = QTableWidget()
        self.init_table()
        parameters_layout.addWidget(self.table, 0, 0)
        
        parameters_group.setLayout(parameters_layout)
        selection_layout.addWidget(parameters_group, 8, 0, 4, 3)
        
        # 添加所有控件到主布局
        main_group = QGroupBox()
        main_group.setLayout(selection_layout)
        layout.addWidget(main_group)
        
        self.setLayout(layout)
        
        # 连接信号
        self.recommendation_button.clicked.connect(self.on_data_changed)
        self.recommendation_type_combo.currentTextChanged.connect(self.on_data_changed)
        self.manufacturer_combo.currentTextChanged.connect(self.on_data_changed)
        self.crane_model_combo.currentTextChanged.connect(self.on_data_changed)
        self.capacity_check.stateChanged.connect(self.on_data_changed)
        self.condition_table_button.clicked.connect(self.on_condition_table_clicked)
        self.boom_combo.currentTextChanged.connect(self.on_data_changed)
        self.condition_detail_combo.currentTextChanged.connect(self.on_data_changed)
        
    def init_table(self):
        """初始化表格"""
        self.table.setColumnCount(7)
        self.table.setRowCount(15)
        
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
    
    def on_condition_table_clicked(self):
        """吊装工况表格按钮点击事件"""
        self.data_changed.emit()
        # TODO: 显示吊装工况表格
        
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
            'boom_type': self.boom_combo.currentText(),
            'condition_detail': self.condition_detail_combo.currentText()
        }
        
    def set_data(self, data):
        """设置对话框数据"""
        self.recommendation_type_combo.setCurrentText(data.get('recommendation_type', '指定起重机厂家推荐'))
        self.manufacturer_combo.setCurrentText(data.get('manufacturer', '三一'))
        self.crane_model_combo.setCurrentText(data.get('Str_crane_modelName', 'STC500'))
        self.capacity_check.setChecked(data.get('capacity_check', True))
        self.boom_combo.setCurrentText(data.get('boom_type', '主臂'))
        self.condition_detail_combo.setCurrentText(data.get('condition_detail', '固定配重30t，支腿全伸，需要二节臂时满伸')) 