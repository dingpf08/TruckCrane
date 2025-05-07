"""
起重机械设置对话框模块

此模块实现了起重机械设置的主要功能，包括：
1. 起重机基本信息的配置和显示
2. 起重机性能参数的管理
3. 起重能力表的展示和编辑

主要类:
- CraneSettingsDialog: 主对话框类
- CraneCustomTab: 起重机自定义标签页
- CraneCapacityTab: 起重机额定起重能力表标签页
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget,
                           QComboBox, QLabel, QGridLayout, QGroupBox,
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QTabWidget, QLineEdit, QCheckBox,
                           QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import os
import sqlite3
# 起重机械设置对话框的数据流和逻辑
#
# 1. 初始化：
#    - 初始化 CraneSettingsDialog，设置 UI 并连接数据库。
#
# 2. 数据库连接：
#    - 使用从 ROOT_DIR 构建的路径连接到 SQLite 数据库。
#    - 使用 fetch_data_from_db 方法从 TruckCrane 表中获取数据。
#
# 3. 数据存储：
#    - 将获取的数据存储在 self.data 成员变量中。
#
# 4. UI 设置：
#    - 创建主布局和标签页控件。
#    - 初始化 CraneCustomTab 和 CraneCapacityTab，并将数据传递给 CraneCustomTab。
#
# 5. 表格初始化：
#    - CraneCustomTab 使用 init_table 方法用数据填充表格。
#
# 6. 信号连接：
#    - 连接用户交互的信号，例如选择起重机型号。
#
# 7. 用户交互：
#    - 当选择起重机型号时，更新 CraneSettingsDialog 中的标签页名称。
#
# 8. 错误处理：
#    - 如果数据库连接失败，显示错误消息。

#主臂起重性能表
# 获取当前文件所在目录的路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))#D:\Cache\ztzp-ConCaSys\Dialogs
# 获取项目根目录的路径
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))#D:\Cache\ztzp-ConCaSys

print(f"CURRENT_DIR: {CURRENT_DIR}")
print(f"ROOT_DIR: {ROOT_DIR}")

class CraneSettingsDialog(QDialog):
    """起重机械设置主对话框类
    
    负责管理整个对话框的布局和数据流转，包括：
    1. 数据库连接和基础数据获取
    2. 标签页管理
    3. 用户交互响应

    成员变量:
        data (list): 存储从数据库获取的起重机基础数据
        current_crane_model (str): 当前选中的起重机型号
        connection (sqlite3.Connection): 数据库连接对象
        cursor (sqlite3.Cursor): 数据库游标对象
        tab_widget (QTabWidget): 标签页控件
        custom_tab (CraneCustomTab): 起重机自定义标签页
        capacity_tab (CraneCapacityTab): 起重机额定起重能力表标签页
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.current_crane_model = None  # 添加当前选中的起重机型号属性
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面
        Initialize the user interface
        
        创建并设置起重机额定起重能力表标签页的所有UI元素
        Creates and sets up all UI elements for the crane capacity tab
        """
        self.setWindowTitle("起重机械设置")
        self.resize(800, 600)
        self.setup_database()
        self.create_layout()
        self.setup_connections()
        
    def setup_database(self):
        """设置数据库连接"""
        try:
            db_path = os.path.join(ROOT_DIR, 'CraneDataBase')
            self.connection = sqlite3.connect(db_path)
            self.cursor = self.connection.cursor()
            self.data = self.fetch_data_from_db()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "数据库错误", f"连接数据库失败: {e}")
            
    def create_layout(self):
        """创建主布局"""
        layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        # 创建标签页
        self.custom_tab = CraneCustomTab(self.data, self.cursor)
        self.capacity_tab = CraneCapacityTab(self.cursor)

        # 添加标签页
        self.tab_widget.addTab(self.custom_tab, "起重机自定义")
        self.tab_widget.addTab(self.capacity_tab, "起重机额定起重能力表")

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    def setup_connections(self):
        """设置信号连接"""
        self.custom_tab.crane_selected.connect(self.on_crane_selected)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
    def fetch_data_from_db(self):
        """从数据库获取起重机基础数据"""
        query = """
        SELECT TruckCraneID, CraneManufacturers, MaxLiftingWeight
        FROM TruckCrane
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
        
    def on_crane_selected(self, model):
        """处理起重机型号选择事件"""
        self.current_crane_model = model  # 更新当前选中的起重机型号
        self.capacity_tab.update_crane_model(model)
        self.tab_widget.setTabText(1, f"{model}起重机额定起重能力表")
        
    def on_tab_changed(self, index):
        """处理标签页切换事件"""
        try:
            print(f"切换到标签页 {index}")  # 添加日志
            print(f"当前起重机型号: {self.current_crane_model}")  # 添加日志

            if not self.cursor or not self.current_crane_model:
                print("数据库游标或起重机型号未设置")
                return

            if index == 0:  # 主臂起重性能表
                # 重新加载主臂工况数据 - 只检查SpeWorkCondition是否有值
                query = """
                SELECT DISTINCT SpeWorkCondition
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND SpeWorkCondition IS NOT NULL
                AND TRIM(SpeWorkCondition) != ''
                ORDER BY SpeWorkCondition
                """
                self.cursor.execute(query, (self.current_crane_model,))
                main_conditions = self.cursor.fetchall()
                
                if main_conditions:
                    self.capacity_tab.main_boom_conditions = [cond[0] for cond in main_conditions]
                    print(f"主臂标签页 - 获取到的主臂工况: {self.capacity_tab.main_boom_conditions}")
                else:
                    print("主臂标签页 - 未获取到主臂工况数据")
                    self.capacity_tab.main_boom_conditions = []

                # 更新主臂工况表格
                self.capacity_tab._populate_condition_table(self.capacity_tab.main_condition_table, self.capacity_tab.main_boom_conditions)
                
                # 重置主臂起重能力表
                if self.capacity_tab.main_capacity_table:
                    self.capacity_tab.main_capacity_table.setRowCount(0)
                    self.capacity_tab.main_capacity_table.setColumnCount(1)
                    self.capacity_tab.main_capacity_table.setHorizontalHeaderLabels(["幅度/主臂长(m)"])
                if self.capacity_tab.main_capacity_title:
                    self.capacity_tab.main_capacity_title.setText("额定起重量(吨)")

            elif index == 1:  # 主臂+副臂起重性能表
                # 重新加载主臂工况数据 - 只检查SpeWorkCondition是否有值
                query_main = """
                SELECT DISTINCT SpeWorkCondition
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND SpeWorkCondition IS NOT NULL
                AND TRIM(SpeWorkCondition) != ''
                ORDER BY SpeWorkCondition
                """
                self.cursor.execute(query_main, (self.current_crane_model,))
                main_conditions = self.cursor.fetchall()
                if main_conditions:
                    self.capacity_tab.main_boom_conditions = [cond[0] for cond in main_conditions]
                    print(f"副臂标签页 - 也获取到的主臂工况: {self.capacity_tab.main_boom_conditions}")
                else:
                    print("副臂标签页 - 未获取到主臂工况数据")
                    self.capacity_tab.main_boom_conditions = []
                # 更新主臂工况表格
                self.capacity_tab._populate_condition_table(self.capacity_tab.main_condition_table, self.capacity_tab.main_boom_conditions)

                # 重新加载主臂+副臂工况数据
                query = """
                SELECT DISTINCT SecondSpeWorkCondition
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND IsJibHosCon = '是'
                AND SecondSpeWorkCondition IS NOT NULL
                AND TRIM(SecondSpeWorkCondition) != ''
                ORDER BY SecondSpeWorkCondition
                """
                self.cursor.execute(query, (self.current_crane_model,))
                combined_conditions = self.cursor.fetchall()
                
                if combined_conditions:
                    self.capacity_tab.combined_boom_conditions = [cond[0] for cond in combined_conditions]
                    print(f"副臂标签页 - 获取到的主臂+副臂工况: {self.capacity_tab.combined_boom_conditions}")
                else:
                    print("副臂标签页 - 未获取到主臂+副臂工况数据")
                    self.capacity_tab.combined_boom_conditions = []

                # 更新主臂+副臂工况表格
                self.capacity_tab._populate_condition_table(self.capacity_tab.combined_condition_table, self.capacity_tab.combined_boom_conditions)
                
                # 重置主臂+副臂起重能力表
                if self.capacity_tab.combined_capacity_table:
                    self.capacity_tab.combined_capacity_table.setRowCount(0)
                    self.capacity_tab.combined_capacity_table.setColumnCount(1)
                    self.capacity_tab.combined_capacity_table.setHorizontalHeaderLabels(["幅度/主臂长(m)"])
                if self.capacity_tab.combined_capacity_title:
                    self.capacity_tab.combined_capacity_title.setText("额定起重量(吨)")

        except sqlite3.Error as e:
            error_msg = f"数据库错误: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "数据库错误", error_msg)
        except Exception as e:
            error_msg = f"切换标签页时发生错误: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

class CraneCustomTab(QWidget):
    """起重机自定义标签页

    成员变量:
        data (list): 存储起重机基础数据的列表
        cursor (sqlite3.Cursor): 数据库游标对象
        crane_type_combo (QComboBox): 起重机类型选择下拉框
        table (QTableWidget): 主数据表格
        manufacturer_edit (QLineEdit): 起重机厂家输入框
        model_edit (QLineEdit): 起重机型号输入框
        calc_checkbox (QCheckBox): 轴距及轴荷计算复选框
        axle_count_edit (QLineEdit): 轴数输入框
        first_axle_load_edit (QLineEdit): 第一排轴荷输入框
        axle_table (QTableWidget): 轴距表格
        total_weight_edit (QLineEdit): 总重输入框
        long_dis_edit (QLineEdit): 支腿纵向距离输入框
        horiz_dis_edit (QLineEdit): 支腿横向距离输入框
        enter_rated_combo (QComboBox): 额定起重量表录入选择框
        dis_to_ground_edit (QLineEdit): 主臂铰链中心至地面距离输入框
        dis_to_rotacen_edit (QLineEdit): 主臂铰链中心至回转中心距离输入框

    信号:
        crane_selected (str): 当选择起重机型号时发出的信号
    """
    crane_selected = pyqtSignal(str)

    def __init__(self, data, cursor):
        super().__init__()
        self.data = data  # Store data as a member variable
        self.cursor = cursor  # Store cursor as a member variable
        """# 示例数据结构
            data = [
             ("STC120T5-1", "三一重工", 120.0),
            ("XCT80L6", "徐工集团", 80.5),
            ("QY100K5C", "中联重科", 100.0)
                   ]
        """
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # 顶部区域 - 起重机类型选择
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("起重机种类:"))
        self.crane_type_combo = QComboBox()
        self.crane_type_combo.addItem("汽车起重机")
        self.crane_type_combo.addItem("履带式起重机")
        top_layout.addWidget(self.crane_type_combo)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # Connect the combo box signal to the slot
        self.crane_type_combo.currentIndexChanged.connect(self.on_crane_type_changed)

        # 中间区域 - 表格
        self.table = QTableWidget()
        self.init_table(self.data)  # Pass self.data to init_table
        main_layout.addWidget(self.table)

        # 底部区域 - 分为左右两部分
        bottom_layout = QHBoxLayout()

        # 左侧 - 图片区域
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        image_label = QLabel()

        # 使用相对于项目根目录的路径加载图片
        image_path = os.path.join(CURRENT_DIR, "PIC", "CranePic.png")
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # 设置图片大小为400x400，保持纵横比
            scaled_pixmap = pixmap.scaled(400, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignCenter)  # 居中显示图片
        else:
            # 如果图片加载失败，显示错误信息
            image_label.setText("图片加载失败")
            print(f"Failed to load image from: {image_path}")
            print(f"Current directory: {CURRENT_DIR}")
            print(f"Image path attempted: {image_path}")

        left_layout.addWidget(image_label)
        left_widget.setLayout(left_layout)
        left_widget.setMinimumWidth(400)
        bottom_layout.addWidget(left_widget)

        # 右侧 - 参数输入区域
        right_layout = QGridLayout()

        # 起重机信息输入
        right_layout.addWidget(QLabel("起重机厂家:"), 0, 0)
        self.manufacturer_edit = QLineEdit()
        right_layout.addWidget(self.manufacturer_edit, 0, 1)

        right_layout.addWidget(QLabel("起重机型号:"), 1, 0)
        self.model_edit = QLineEdit()
        right_layout.addWidget(self.model_edit, 1, 1)

        # 添加复选框
        self.calc_checkbox = QCheckBox("输入汽车起重机轴距及轴荷计算")
        right_layout.addWidget(self.calc_checkbox, 2, 0, 1, 2)

        # 轴距及轴荷组
        axle_group = QGroupBox("起重机轴距及轴荷")
        axle_layout = QGridLayout()

        axle_layout.addWidget(QLabel("汽车起重机轴数:"), 0, 0)
        self.axle_count_edit = QLineEdit()
        axle_layout.addWidget(self.axle_count_edit, 0, 1)

        axle_layout.addWidget(QLabel("第1排车轮荷载(吨):"), 1, 0)
        self.first_axle_load_edit = QLineEdit()
        axle_layout.addWidget(self.first_axle_load_edit, 1, 1)

        # 添加轴距表格
        self.axle_table = QTableWidget()
        self.axle_table.setColumnCount(3)
        self.axle_table.setHorizontalHeaderLabels(["第i排车轮", "依次轴距(mm)", "轴荷(吨)"])
        self.axle_table.setRowCount(2)

        # 设置示例数据
        self.axle_table.setItem(0, 0, QTableWidgetItem("2"))
        self.axle_table.setItem(0, 1, QTableWidgetItem("4760"))
        self.axle_table.setItem(0, 2, QTableWidgetItem("13.000"))
        self.axle_table.setItem(1, 0, QTableWidgetItem("3"))
        self.axle_table.setItem(1, 1, QTableWidgetItem("1360"))
        self.axle_table.setItem(1, 2, QTableWidgetItem("13.000"))

        axle_layout.addWidget(self.axle_table, 2, 0, 1, 2)

        # Initialize parameter input widgets as member variables
        self.total_weight_edit = QLineEdit("34.1")
        self.long_dis_edit = QLineEdit("5.4")
        self.horiz_dis_edit = QLineEdit("6.4")
        self.enter_rated_combo = QComboBox()
        self.enter_rated_combo.addItems(["是", "否"])
        self.dis_to_ground_edit = QLineEdit("3.05")
        self.dis_to_rotacen_edit = QLineEdit("1.6")

        # Add widgets to the layout
        axle_layout.addWidget(QLabel("起重机总重(吨):"), 3, 0)
        axle_layout.addWidget(self.total_weight_edit, 3, 1)

        axle_layout.addWidget(QLabel("支腿纵向距离L(m):"), 4, 0)
        axle_layout.addWidget(self.long_dis_edit, 4, 1)

        axle_layout.addWidget(QLabel("支腿横向距离B(m):"), 5, 0)
        axle_layout.addWidget(self.horiz_dis_edit, 5, 1)

        axle_layout.addWidget(QLabel("是否录入额定起重量表:"), 6, 0)
        axle_layout.addWidget(self.enter_rated_combo, 6, 1)

        axle_layout.addWidget(QLabel("主臂铰链中心至地面距离h(m):"), 7, 0)
        axle_layout.addWidget(self.dis_to_ground_edit, 7, 1)

        axle_layout.addWidget(QLabel("主臂铰链中心至回转中心距离a1(m):"), 8, 0)
        axle_layout.addWidget(self.dis_to_rotacen_edit, 8, 1)

        axle_group.setLayout(axle_layout)
        right_layout.addWidget(axle_group, 3, 0, 1, 2)

        # 将右侧布局添加到底部布局
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        bottom_layout.addWidget(right_widget)

        main_layout.addLayout(bottom_layout)

        # 注释说明
        note_label = QLabel("注：表中淡灰色文字为官方数据，官方数据不可修改！")
        main_layout.addWidget(note_label)

        self.setLayout(main_layout)

        # 设置表格选择模式为整行选择
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        # 连接信号
        self.table.itemClicked.connect(self.on_item_clicked)

    def on_crane_type_changed(self, index):
        """Handle changes in crane type selection."""
        crane_type = self.crane_type_combo.currentText()
        try:
            if crane_type == "汽车起重机":
                query = """
                SELECT TruckCraneID, CraneManufacturers, MaxLiftingWeight
                FROM TruckCrane
                """
            elif crane_type == "履带式起重机":
                query = """
                SELECT CrawlerCraneID, CraneManufacturers, MaxLiftingWeight
                FROM CrawlerCrane
                """
            
            # Fetch new data based on the selected crane type
            self.cursor.execute(query)
            self.data = self.cursor.fetchall()

            # Format data for display
            data_str = "\n".join([f"Model: {model}, Manufacturer: {manufacturer}, Capacity: {capacity}" for model, manufacturer, capacity in self.data])

            # Display data in a message box
            #QMessageBox.information(self, "Fetched Data", data_str)

            # Clear and update the table with new data
            self.init_table(self.data)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def init_table(self, data):
        """Initialize the table with data from the database."""
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["起重机厂家", "起重机型号", "最大额定起重量(吨)"])

        self.table.setRowCount(len(data))

        # 设置表格的最小高度，确保能显示8行
        row_height = 30  # 每行高度
        header_height = 30  # 表头高度
        min_visible_rows = 8  # 最少显示8行
        min_height = row_height * min_visible_rows + header_height
        self.table.setMinimumHeight(min_height)

        # 填充数据并设置为不可编辑
        for i, (model, manufacturer, capacity) in enumerate(data):
            for j, value in enumerate([manufacturer, model, capacity]):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # 设置为不可编辑
                self.table.setItem(i, j, item)

        # 设置表格整体为不可编辑
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 调整列宽
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 设置表格样式
        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)

    def on_item_clicked(self, item):
        """当点击表格项时，从数据库获取详细信息并填充到控件中"""
        row = item.row()
        selected_data = self.data[row]
        # selected_data中只包含三个值：[型号, 厂家, 最大额定起重量]
        crane_model = selected_data[0]  # 获取起重机型号
        
        try:
            # 根据起重机类型查询不同的表获取详细信息
            if self.crane_type_combo.currentText() == "汽车起重机":
                # 查询汽车起重机详细参数
                query = """
                SELECT 
                    AxesNums,               -- 轴数
                    CraneTotalWeight,       -- 起重机总重
                    OutriggerLongDis,       -- 支腿纵向距离L
                    OutriggersHorizDis,     -- 支腿横向距离B
                    IsEnterRatedWT,         -- 是否录入额定起重量表
                    DisMAHToGroud,          -- 主臂铰链中心至地面距离h
                    DisMAHToRotaCen         -- 主臂铰链中心至回转中心的距离
                FROM TruckCraneDetailInfo
                WHERE TruckCraneID = ?
                """
            else:
                # 查询履带式起重机详细参数
                query = """
                SELECT 
                    AxesNums,
                    CraneTotalWeight,
                    OutriggerLongDis,
                    OutriggersHorizDis,
                    IsEnterRatedWT,
                    DisMAHToGroud,
                    DisMAHToRotaCen
                FROM CrawlerCraneDetailInfo
                WHERE CrawlerCraneID = ?
                """
            
            # 执行查询
            self.cursor.execute(query, (crane_model,))
            detail = self.cursor.fetchone()
            
            if detail:
                # 先填充已知的数据
                self.manufacturer_edit.setText(str(selected_data[1]))  # 厂家
                self.model_edit.setText(str(selected_data[0]))        # 型号
                
                # 填充查询到的详细数据
                self.total_weight_edit.setText(str(detail[1]))       # 总重
                self.long_dis_edit.setText(str(detail[2]))           # 支腿纵向距离L
                self.horiz_dis_edit.setText(str(detail[3]))          # 支腿横向距离B
                self.enter_rated_combo.setCurrentText("是" if detail[4] == "是" else "否")  # 是否有额定起重量表
                self.dis_to_ground_edit.setText(str(detail[5]))      # 主臂铰链中心至地面距离h
                self.dis_to_rotacen_edit.setText(str(detail[6]))     # 主臂铰链中心至回转中心距离a1
                #测试
                # 发送型号选择信号
                self.crane_selected.emit(crane_model)
                
                # 查询并填充轴距和轴荷数据
                self.load_axle_data(crane_model)
                
            else:
                QMessageBox.warning(self, "查询结果", f"未找到型号为 {crane_model} 的起重机详细信息")
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "数据库错误", f"查询数据时发生错误: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生未知错误: {str(e)}")
            
    def load_axle_data(self, crane_model):
        """加载轴距和轴荷数据"""
        try:
            # 查询轴数和轴距轴荷数据
            query = """
            SELECT 
                AxesNums,    -- 轴数
                D1, L1,      -- 第1排轴距和轴荷
                D2, L2,      -- 第2排轴距和轴荷
                D3, L3,      -- 第3排轴距和轴荷
                D4, L4,      -- 第4排轴距和轴荷
                D5, L5,      -- 第5排轴距和轴荷
                D6, L6       -- 第6排轴距和轴荷
            FROM TruckCraneAxesNumLoad
            WHERE TruckCraneID = ?
            """
            
            self.cursor.execute(query, (crane_model,))
            axle_data = self.cursor.fetchone()
            
            if axle_data:
                axle_count = int(axle_data[0])  # 获取轴数
                self.axle_count_edit.setText(str(axle_count))  # 设置轴数
                
                # 设置第一排轴荷
                self.first_axle_load_edit.setText(str(axle_data[2]))  # L1值
                
                # 设置轴距表格的行数（轴数-1，因为第一排已经单独显示）
                self.axle_table.setRowCount(axle_count - 1)
                
                # 从第2排开始填充轴距和轴荷数据
                for i in range(axle_count - 1):
                    # 计算在axle_data中的索引位置
                    # 每对D,L占用2个位置，从D2,L2开始，所以基础偏移是3
                    base_idx = 3 + i * 2
                    
                    # 设置排数（从2开始）
                    self.axle_table.setItem(i, 0, QTableWidgetItem(str(i + 2)))
                    # 设置轴距
                    self.axle_table.setItem(i, 1, QTableWidgetItem(str(axle_data[base_idx])))
                    # 设置轴荷
                    self.axle_table.setItem(i, 2, QTableWidgetItem(str(axle_data[base_idx + 1])))
                    
        except sqlite3.Error as e:
            QMessageBox.warning(self, "数据库错误", f"加载轴距和轴荷数据时发生错误: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载轴距和轴荷数据时发生未知错误: {str(e)}")

class CraneCapacityTab(QWidget):
    """起重机额定起重能力表标签页

    成员变量:
        Str_crane_modelName (str): 当前选中的起重机型号
        cursor (sqlite3.Cursor): 数据库游标对象
        main_content (QWidget): 主要内容区域控件
        main_condition_table (QTableWidget): 主臂工况表格
        combined_condition_table (QTableWidget): 主臂+副臂工况表格
        main_capacity_table (QTableWidget): 主臂起重能力表格
        combined_capacity_table (QTableWidget): 主臂+副臂起重能力表格
        main_capacity_title (QLabel): 主臂起重能力表标题
        combined_capacity_title (QLabel): 主臂+副臂起重能力表标题
        main_boom_conditions (list): 存储主臂工况数据
        combined_boom_conditions (list): 存储主臂+副臂工况数据
        condition_combo (QComboBox): 副臂装置工况选择下拉框
        tab_widget (QTabWidget): 标签页控件
        main_boom_tab (QWidget): 主臂标签页
        combined_boom_tab (QWidget): 主臂+副臂标签页
    """
    def __init__(self, cursor):
        super().__init__()
        self.Str_crane_modelName = None
        self.cursor = cursor
        self.main_content = QWidget()
        self.main_condition_table = None
        self.combined_condition_table = None
        self.main_capacity_table = None
        self.combined_capacity_table = None
        self.main_capacity_title = None
        self.combined_capacity_title = None
        self.main_boom_conditions = []  # Store main boom conditions
        self.combined_boom_conditions = []  # Store combined boom conditions
        self.init_ui()

    def init_ui(self):
        """初始化用户界面
        Initialize the user interface
        
        创建并设置起重机额定起重能力表标签页的所有UI元素
        Creates and sets up all UI elements for the crane capacity tab
        """
        # 创建主垂直布局
        # Create main vertical layout
        main_layout = QVBoxLayout()
        
        # 创建顶部区域 - 副臂装置工况选择
        # Create top area - auxiliary boom condition selection
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("是否有副臂吊装工况:"))  # 添加标签 (Add label)
        self.condition_combo = QComboBox()  # 创建下拉框 (Create combo box)
        self.condition_combo.addItem("否")  # 添加选项"否" (Add "No" option)
        self.condition_combo.addItem("是")  # 添加选项"是" (Add "Yes" option)
        top_layout.addWidget(self.condition_combo)  # 将下拉框添加到布局 (Add combo box to layout)
        top_layout.addStretch()  # 添加弹性空间 (Add stretch space)
        main_layout.addLayout(top_layout)  # 将顶部布局添加到主布局 (Add top layout to main layout)
        
        # 创建标签页控件
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setVisible(False)  # 初始设置为不可见 (Initially set to invisible)
        
        # 创建主臂起重性能表标签页
        # Create main boom performance tab
        self.main_boom_tab = QWidget()
        self.init_main_boom_tab()  # 初始化主臂标签页 (Initialize main boom tab)
        self.tab_widget.addTab(self.main_boom_tab, "主臂起重性能表")
        
        # 创建主臂+副臂起重性能表标签页
        # Create main boom + auxiliary boom performance tab
        self.combined_boom_tab = QWidget()
        self.init_combined_boom_tab()  # 初始化主副臂组合标签页 (Initialize combined boom tab)
        self.tab_widget.addTab(self.combined_boom_tab, "主臂+副臂起重性能表")
        
        # 连接标签页切换信号
        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 初始化主要内容区域
        # Initialize main content area
        main_content_layout = QVBoxLayout()
        
        # 创建主臂起重性能表组
        # Create main boom performance group
        main_group = QGroupBox("主臂起重性能表")
        group_layout = QVBoxLayout()
        
        # 创建额定起重量确定方法选择区域
        # Create rated lifting capacity determination method selection area
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("额定起重量确定方法:"))
        self.method_combo = QComboBox()
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        group_layout.addLayout(method_layout)
        
        # 创建主要内容区域 - 左右分布
        # Create main content area - left and right distribution
        content_layout = QHBoxLayout()
        
        # 左侧 - 工况列表
        # Left side - condition list
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("主臂吊装工况:"))
        
        # 创建工况表格
        # Create condition table
        self.main_condition_table = QTableWidget()
        self.init_condition_table(self.main_condition_table)
        left_layout.addWidget(self.main_condition_table)
        left_layout.addStretch()
        
        # 右侧 - 起重能力表
        # Right side - lifting capacity table
        right_layout = QVBoxLayout()
        title_label = QLabel("工况1【配重1.2t，支腿全伸】额定起重量(吨)")
        right_layout.addWidget(title_label)
        
        # 创建起重能力表格
        # Create lifting capacity table
        self.main_capacity_table = QTableWidget()
        self.init_capacity_table(self.main_capacity_table)
        right_layout.addWidget(self.main_capacity_table)
        
        # 设置左右布局的比例为1:3
        # Set left and right layout ratio to 1:3
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 3)
        
        # 组装布局
        # Assemble layouts
        group_layout.addLayout(content_layout)
        main_group.setLayout(group_layout)
        main_content_layout.addWidget(main_group)
        
        # 设置主内容布局
        # Set main content layout
        self.main_content.setLayout(main_content_layout)
        
        # 将主要组件添加到主布局
        # Add main components to main layout
        main_layout.addWidget(self.main_content)
        main_layout.addWidget(self.tab_widget)
        
        # 添加底部说明文字
        # Add bottom description text
        note_text = ("注：本数据库操作方式：\n"
                    "（官方数据不可修改，自定义数据可修改）：\n"
                    "1、左侧保装工况装格输入具体装置工况（比如配重情况、支腿\n"
                    "外伸情况）等，根据右侧可增加删除工况。\n"
                    "2、选定工况，在右侧表格相录入当前工况下起重机额定起重量。\n"
                    "3、右侧额定起重量表格可通过鼠标右键：增加行、删除行、\n"
                    "增加列、删除列。\n"
                    "4、最后点击窗口下方'保存额定起重量'按钮。")
        note_label = QLabel(note_text)
        main_layout.addWidget(note_label)
        
        # 设置主布局
        # Set main layout
        self.setLayout(main_layout)
        
        # 连接信号
        # Connect signals
        self.condition_combo.currentTextChanged.connect(self.on_condition_changed)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 初始化界面状态
        self.main_content.setVisible(True)
        self.tab_widget.setVisible(False)

    def init_main_boom_tab(self):
        """初始化主臂起重性能表标签页
        
        此方法负责创建和配置主臂起重性能表的标签页界面，包括：
        1. 创建主要布局和分组
        2. 设置额定起重量确定方法选择器
        3. 配置左侧主臂工况列表
        4. 配置右侧起重能力表格
        5. 设置表格样式和行为
        
        布局结构：
        - 主布局（垂直）
            - 主臂起重性能表组
                - 额定起重量确定方法（下拉框）
                - 内容区域（水平分布）
                    - 左侧：主臂工况列表
                    - 右侧：起重能力表格
        """
        layout = QVBoxLayout()

        # 主臂起重性能表组
        main_group = QGroupBox("主臂起重性能表")
        group_layout = QVBoxLayout()

        # 额定起重量确定方法
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("额定起重量确定方法:"))
        method_combo = QComboBox()
        method_combo.addItem("根据幅度、主臂长确定")
        method_layout.addWidget(method_combo)
        method_layout.addStretch()
        group_layout.addLayout(method_layout)

        # 主要内容区域 - 左右分布
        content_layout = QHBoxLayout()

        # 左侧 - 工况列表
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("主臂吊装工况:"))

        # 创建主臂工况表格并设置属性
        self.main_condition_table = QTableWidget()
        self.main_condition_table.setColumnCount(2)
        self.main_condition_table.setHorizontalHeaderLabels(["主臂工况编号", "主臂具体工况"])
        self.main_condition_table.horizontalHeader().setStretchLastSection(True)
        self.main_condition_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.main_condition_table.setColumnWidth(0, 100)
        self.main_condition_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.main_condition_table.setSelectionMode(QTableWidget.SingleSelection)

        # 设置表格的最小尺寸和策略
        self.main_condition_table.setMinimumWidth(300)
        self.main_condition_table.setMinimumHeight(200)
        self.main_condition_table.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        # 设置表格样式
        self.main_condition_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d3d3d3;
                gridline-color: #d3d3d3;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #d3d3d3;
            }
        """)

        left_layout.addWidget(self.main_condition_table)

        # 右侧 - 起重能力表
        right_layout = QVBoxLayout()
        self.main_capacity_title = QLabel("额定起重量(吨)")
        right_layout.addWidget(self.main_capacity_title)

        # 创建主臂起重能力表格
        self.main_capacity_table = QTableWidget()
        self.main_capacity_table.setColumnCount(2)
        self.main_capacity_table.setHorizontalHeaderLabels(["主臂幅度/主臂长(m)", ""])
        self.main_capacity_table.horizontalHeader().setStretchLastSection(True)
        self.main_capacity_table.verticalHeader().setVisible(False)
        self.main_capacity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.main_capacity_table.setMinimumHeight(200)
        right_layout.addWidget(self.main_capacity_table)

        # 设置左右布局的比例为1:2
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 2)

        # 组装所有布局
        group_layout.addLayout(content_layout)
        main_group.setLayout(group_layout)
        layout.addWidget(main_group)

        # 确保所有组件可见
        main_group.setVisible(True)
        self.main_condition_table.setVisible(True)
        self.main_capacity_table.setVisible(True)

        # 设置标签页布局
        self.main_boom_tab.setLayout(layout)

    def init_combined_boom_tab(self):
        """初始化主臂+副臂起重性能表标签页"""
        layout = QVBoxLayout()

        # 主臂+副臂起重性能表组
        combined_group = QGroupBox("主臂+副臂起重性能表")
        group_layout = QVBoxLayout()

        # 额定起重量确定方法
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("额定起重量确定方法:"))
        method_combo = QComboBox()
        method_combo.addItem("根据幅度、主臂长、副臂长度、副臂安装角度确定")
        method_layout.addWidget(method_combo)
        method_layout.addStretch()
        group_layout.addLayout(method_layout)

        # 主要内容区域 - 左右分布
        content_layout = QHBoxLayout()

        # 左侧 - 工况列表
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("主臂+副臂吊装工况:"))

        # 创建主臂+副臂工况表格
        self.combined_condition_table = QTableWidget()
        self.combined_condition_table.setColumnCount(2)
        self.combined_condition_table.setHorizontalHeaderLabels(["主副臂工况编号", "主副臂具体工况"])
        self.combined_condition_table.horizontalHeader().setStretchLastSection(True)
        self.combined_condition_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.combined_condition_table.setColumnWidth(0, 120)
        self.combined_condition_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.combined_condition_table.setSelectionMode(QTableWidget.SingleSelection)
        self.combined_condition_table.itemClicked.connect(self.on_condition_clicked)
        left_layout.addWidget(self.combined_condition_table)

        # 右侧 - 起重能力表
        right_layout = QVBoxLayout()
        self.combined_capacity_title = QLabel("额定起重量(吨)")
        right_layout.addWidget(self.combined_capacity_title)

        # 创建主臂+副臂起重能力表格
        self.combined_capacity_table = QTableWidget()
        self.combined_capacity_table.setColumnCount(2)
        self.combined_capacity_table.setHorizontalHeaderLabels(["主副臂幅度/主臂长(m)", ""])
        self.combined_capacity_table.horizontalHeader().setStretchLastSection(True)
        self.combined_capacity_table.verticalHeader().setVisible(False)
        self.combined_capacity_table.setEditTriggers(QTableWidget.NoEditTriggers)
        right_layout.addWidget(self.combined_capacity_table)

        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 2)

        group_layout.addLayout(content_layout)
        combined_group.setLayout(group_layout)
        layout.addWidget(combined_group)

        self.combined_boom_tab.setLayout(layout)

    def init_condition_table(self, table):
        """初始化工况表格"""
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["工况编号", "具体工况"])

        # 设置表格属性
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置为不可编辑
        table.setMinimumWidth(300)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.setColumnWidth(0, 80)  # 设置工况编号列的宽度

        # 设置表格样式
        table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)

        # 设置表格选择模式
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)

        # 连接点击信号
        table.itemClicked.connect(self.on_condition_clicked)

    def init_capacity_table(self, table, is_combined=False):
        """初始化起重能力表"""
        self.table = table
        if not is_combined:
            # 主臂起重能力表
            headers = ["幅度/主臂长(m)", "9.6", "15.08", "20.56", "26.04", "31.52", "37"]
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)

            data = [
                ["3", "12", "10.8", "", "", "", ""],
                ["3.5", "12", "10.8", "8.7", "", "", ""],
                ["4", "11.7", "10.6", "8.7", "", "", ""],
                ["4.5", "11.2", "10.4", "8.7", "6.8", "", ""],
                ["5", "9", "9.2", "8.2", "6.8", "", ""],
                ["5.5", "7.4", "7.6", "7.8", "6.7", "", ""],
                ["6", "6.2", "6.4", "6.6", "6.2", "4.8", ""],
                ["6.5", "5.2", "5.5", "5.7", "5.8", "4.8", ""],
                ["7", "4.5", "4.7", "4.9", "5", "4.5", "3.5"],
                ["8", "", "3.6", "3.8", "3.9", "3.9", "3.5"],
                ["9", "", "2.9", "3", "3.1", "3.1", "3.2"],
                ["10", "", "2.3", "2.4", "2.5", "2.6", "2.6"],
                ["11", "", "1.8", "2", "2", "2.1", "2.1"],
                ["12", "", "1.5", "1.6", "1.7", "1.7", "1.7"],
                ["14", "", "", "1.1", "1.1", "1.2", "1.2"],
                ["16", "", "", "0.7", "0.7", "0.8", "0.8"],
                ["18", "", "", "0.4", "0.4", "0.5", "0.5"],
                ["20", "", "", "", "", "", "0.3"]
            ]
        else:
            # 主臂+副臂起重能力表
            headers = ["幅度/主臂长(m)", "41"]
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)

            data = [
                ["78", "2.8"],
                ["75", "2.5"],
                ["72", "2.2"],
                ["70", "2"],
                ["65", "1.6"],
                ["60", "1"],
                ["55", "0.6"],
                ["50", "0.35"]
            ]

        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(value if value else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, j, item)

        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setWordWrap(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)

    def on_condition_changed(self, text):
        """当副臂装置工况选择改变时"""
        try:
            print(f"工况选择改变为: {text}")  # 添加日志
            print(f"当前主臂工况数据: {self.main_boom_conditions}")  # 添加日志
            print(f"当前主臂+副臂工况数据: {self.combined_boom_conditions}")  # 添加日志

            if text == "是":
                self.main_content.setVisible(False)
                self.tab_widget.setVisible(True)
                
                # 确保主臂工况数据在切换时正确显示
                print("更新主臂工况表格...")
                self._populate_condition_table(self.main_condition_table, self.main_boom_conditions)
                print("更新主臂+副臂工况表格...")
                self._populate_condition_table(self.combined_condition_table, self.combined_boom_conditions)
                
                # 默认显示主臂标签页
                self.tab_widget.setCurrentIndex(0)
            else:
                self.main_content.setVisible(True)
                self.tab_widget.setVisible(False)
                # 在主界面显示主臂工况
                print("更新主界面主臂工况表格...")
                self._populate_condition_table(self.main_condition_table, self.main_boom_conditions)

            # 重置起重能力表
            self._reset_capacity_tables()

        except Exception as e:
            print(f"切换工况显示时发生错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"切换工况显示时发生错误: {str(e)}")

    def _reset_capacity_tables(self):
        """重置起重能力表"""
        try:
            if self.main_capacity_table:
                self.main_capacity_table.setRowCount(0)
                self.main_capacity_table.setColumnCount(1)
                self.main_capacity_table.setHorizontalHeaderLabels(["主臂幅度/主臂长(m)"])
            if self.main_capacity_title:
                self.main_capacity_title.setText("额定起重量(吨)")

            if self.combined_capacity_table:
                self.combined_capacity_table.setRowCount(0)
                self.combined_capacity_table.setColumnCount(1)
                self.combined_capacity_table.setHorizontalHeaderLabels(["主副臂幅度/主臂长(m)"])
            if self.combined_capacity_title:
                self.combined_capacity_title.setText("额定起重量(吨)")
        except Exception as e:
            print(f"重置起重能力表时发生错误: {str(e)}")

    def _populate_condition_table(self, table, conditions):
        """填充工况表格的辅助方法"""
        try:
            if not table:
                print("错误：表格对象为空")
                return
                
            print(f"开始填充表格，条件数量: {len(conditions) if conditions else 0}")
            print(f"条件内容: {conditions}")
            
            # 设置表格的基本属性
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["工况编号", "具体工况"])
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.SingleSelection)
            
            # 清空现有行
            table.setRowCount(0)
            
            if conditions:
                # 设置表格行数为条件数量
                table.setRowCount(len(conditions))
                
                # 遍历所有条件并填充表格
                for i, condition in enumerate(conditions):
                    print(f"设置第 {i+1} 行数据: {condition}")
                    
                    # 创建并设置工况编号单元格
                    item_num = QTableWidgetItem(str(i + 1))
                    item_num.setTextAlignment(Qt.AlignCenter)
                    table.setItem(i, 0, item_num)
                    
                    # 创建并设置工况内容单元格
                    condition_item = QTableWidgetItem(str(condition))
                    table.setItem(i, 1, condition_item)
                
                # 调整表格列宽和样式
                table.resizeColumnsToContents()
                table.horizontalHeader().setStretchLastSection(True)
                table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
                table.setColumnWidth(0, 80)
                
                print("表格填充完成")
                
            else:
                print("没有条件数据，清空表格")
                table.setRowCount(0)
                
            # 确保表格可见并更新显示
            table.show()
            table.update()
            
        except Exception as e:
            print(f"填充表格时发生错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"填充表格时发生错误: {str(e)}")

    def on_tab_changed(self, index):
        """处理标签页切换事件"""
        try:
            print(f"切换到标签页 {index}")  # 添加日志
            print(f"当前起重机型号: {self.Str_crane_modelName}")  # 添加日志

            if not self.cursor or not self.Str_crane_modelName:
                print("数据库游标或起重机型号未设置")
                return

            if index == 0:  # 主臂起重性能表
                # 重新加载主臂工况数据 - 只检查SpeWorkCondition是否有值
                query = """
                SELECT DISTINCT SpeWorkCondition
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND SpeWorkCondition IS NOT NULL
                AND TRIM(SpeWorkCondition) != ''
                ORDER BY SpeWorkCondition
                """
                self.cursor.execute(query, (self.Str_crane_modelName,))
                main_conditions = self.cursor.fetchall()
                
                if main_conditions:
                    self.main_boom_conditions = [cond[0] for cond in main_conditions]
                    print(f"主臂标签页 - 获取到的主臂工况: {self.main_boom_conditions}")
                else:
                    print("主臂标签页 - 未获取到主臂工况数据")
                    self.main_boom_conditions = []

                # 更新主臂工况表格
                self._populate_condition_table(self.main_condition_table, self.main_boom_conditions)
                
                # 重置主臂起重能力表
                if self.main_capacity_table:
                    self.main_capacity_table.setRowCount(0)
                    self.main_capacity_table.setColumnCount(1)
                    self.main_capacity_table.setHorizontalHeaderLabels(["幅度/主臂长(m)"])
                if self.main_capacity_title:
                    self.main_capacity_title.setText("额定起重量(吨)")

            elif index == 1:  # 主臂+副臂起重性能表
                # 重新加载主臂工况数据 - 只检查SpeWorkCondition是否有值
                query_main = """
                SELECT DISTINCT SpeWorkCondition
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND SpeWorkCondition IS NOT NULL
                AND TRIM(SpeWorkCondition) != ''
                ORDER BY SpeWorkCondition
                """
                self.cursor.execute(query_main, (self.Str_crane_modelName,))
                main_conditions = self.cursor.fetchall()
                if main_conditions:
                    self.main_boom_conditions = [cond[0] for cond in main_conditions]
                    print(f"副臂标签页 - 也获取到的主臂工况: {self.main_boom_conditions}")
                else:
                    print("副臂标签页 - 未获取到主臂工况数据")
                    self.main_boom_conditions = []
                # 更新主臂工况表格
                self._populate_condition_table(self.main_condition_table, self.main_boom_conditions)

                # 重新加载主臂+副臂工况数据
                query = """
                SELECT DISTINCT SecondSpeWorkCondition
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND IsJibHosCon = '是'
                AND SecondSpeWorkCondition IS NOT NULL
                AND TRIM(SecondSpeWorkCondition) != ''
                ORDER BY SecondSpeWorkCondition
                """
                self.cursor.execute(query, (self.Str_crane_modelName,))
                combined_conditions = self.cursor.fetchall()
                
                if combined_conditions:
                    self.combined_boom_conditions = [cond[0] for cond in combined_conditions]
                    print(f"副臂标签页 - 获取到的主臂+副臂工况: {self.combined_boom_conditions}")
                else:
                    print("副臂标签页 - 未获取到主臂+副臂工况数据")
                    self.combined_boom_conditions = []

                # 更新主臂+副臂工况表格
                self._populate_condition_table(self.combined_condition_table, self.combined_boom_conditions)
                
                # 重置主臂+副臂起重能力表
                if self.combined_capacity_table:
                    self.combined_capacity_table.setRowCount(0)
                    self.combined_capacity_table.setColumnCount(1)
                    self.combined_capacity_table.setHorizontalHeaderLabels(["幅度/主臂长(m)"])
                if self.combined_capacity_title:
                    self.combined_capacity_title.setText("额定起重量(吨)")

        except sqlite3.Error as e:
            error_msg = f"数据库错误: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "数据库错误", error_msg)
        except Exception as e:
            error_msg = f"切换标签页时发生错误: {str(e)}"
            print(error_msg)
            QMessageBox.warning(self, "错误", error_msg)

    def on_condition_clicked(self, item):
        """处理工况点击事件"""
        if not self.cursor or not self.Str_crane_modelName:
            return
            
        try:
            current_tab = self.tab_widget.currentWidget()
            if current_tab == self.main_boom_tab:
                # 获取选中的主臂工况
                condition = self.main_condition_table.item(item.row(), 1).text()
                
                # 更新标题
                self.main_capacity_title.setText(f"工况{item.row() + 1}【{condition}】额定起重量(吨)")
                
                # 查询对应的起重能力数据
                query = """
                SELECT DISTINCT 
                    TruckCraneRange,           -- 汽车吊幅度
                    TruckCraneMainArmLen,      -- 主臂长度
                    TruckCraneRatedLiftingCap  -- 额定起重量
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND SpeWorkCondition = ?
                AND (SecondSpeWorkCondition IS NULL OR SecondSpeWorkCondition = '')
                AND TruckCraneRatedLiftingCap IS NOT NULL
                AND TruckCraneRatedLiftingCap != ''
                ORDER BY CAST(TruckCraneRange AS FLOAT)
                """
                
                self.cursor.execute(query, (self.Str_crane_modelName, condition))
                data = self.cursor.fetchall()
                
                if data:
                    # 获取所有不同的主臂长度和幅度值
                    arm_lengths = sorted(set(str(row[1]) for row in data), key=lambda x: float(x) if x else 0)
                    ranges = sorted(set(str(row[0]) for row in data), key=lambda x: float(x) if x else 0)
                    
                    # 设置主臂工况表格的列数和标题
                    self.main_capacity_table.setColumnCount(len(arm_lengths) + 1)
                    headers = ["幅度/主臂长(m)"] + arm_lengths
                    self.main_capacity_table.setHorizontalHeaderLabels(headers)
                    
                    # 设置行数
                    self.main_capacity_table.setRowCount(len(ranges))
                    
                    # 创建数据字典，用于快速查找
                    capacity_dict = {}
                    for row in data:
                        capacity_dict[(str(row[0]), str(row[1]))] = str(row[2])
                    
                    # 填充数据
                    for i, range_val in enumerate(ranges):
                        # 设置幅度值
                        self.main_capacity_table.setItem(i, 0, QTableWidgetItem(str(range_val)))
                        
                        # 填充每个主臂长度对应的起重量
                        for j, arm_len in enumerate(arm_lengths):
                            capacity = capacity_dict.get((range_val, arm_len), "")
                            if capacity:
                                formatted_capacity = self.format_number(capacity)
                                self.main_capacity_table.setItem(i, j + 1, QTableWidgetItem(formatted_capacity))
                            else:
                                self.main_capacity_table.setItem(i, j + 1, QTableWidgetItem(""))
                    
                    # 调整列宽
                    self.main_capacity_table.resizeColumnsToContents()
                else:
                    # 如果没有数据，清空表格
                    self.main_capacity_table.setRowCount(0)
                    self.main_capacity_table.setColumnCount(1)
                    self.main_capacity_table.setHorizontalHeaderLabels(["幅度/主臂长(m)"])
                    
            elif current_tab == self.combined_boom_tab:
                # 获取选中的主臂+副臂工况
                condition = self.combined_condition_table.item(item.row(), 1).text()
                
                # 更新标题
                self.combined_capacity_title.setText(f"工况{item.row() + 1}【{condition}】额定起重量(吨)")
                
                # 查询对应的起重能力数据
                query = """
                SELECT DISTINCT 
                    TruckCraneRange,           -- 汽车吊幅度
                    TruckCraneMainArmLen,      -- 主臂长度
                    TruckCraneRatedLiftingCap  -- 额定起重量
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND SecondSpeWorkCondition = ?
                AND TruckCraneRatedLiftingCap IS NOT NULL
                AND TruckCraneRatedLiftingCap != ''
                ORDER BY CAST(TruckCraneRange AS FLOAT)
                """
                
                self.cursor.execute(query, (self.Str_crane_modelName, condition))
                data = self.cursor.fetchall()
                
                if data:
                    # 获取所有不同的主臂长度和幅度值
                    arm_lengths = sorted(set(str(row[1]) for row in data), key=lambda x: float(x) if x else 0)
                    ranges = sorted(set(str(row[0]) for row in data), key=lambda x: float(x) if x else 0)
                    
                    # 设置主臂+副臂工况表格的列数和标题
                    self.combined_capacity_table.setColumnCount(len(arm_lengths) + 1)
                    headers = ["幅度/主臂长(m)"] + arm_lengths
                    self.combined_capacity_table.setHorizontalHeaderLabels(headers)
                    
                    # 设置行数
                    self.combined_capacity_table.setRowCount(len(ranges))
                    
                    # 创建数据字典，用于快速查找
                    capacity_dict = {}
                    for row in data:
                        capacity_dict[(str(row[0]), str(row[1]))] = str(row[2])
                    
                    # 填充数据
                    for i, range_val in enumerate(ranges):
                        # 设置幅度值
                        self.combined_capacity_table.setItem(i, 0, QTableWidgetItem(str(range_val)))
                        
                        # 填充每个主臂长度对应的起重量
                        for j, arm_len in enumerate(arm_lengths):
                            capacity = capacity_dict.get((range_val, arm_len), "")
                            if capacity:
                                formatted_capacity = self.format_number(capacity)
                                self.combined_capacity_table.setItem(i, j + 1, QTableWidgetItem(formatted_capacity))
                            else:
                                self.combined_capacity_table.setItem(i, j + 1, QTableWidgetItem(""))
                    
                    # 调整列宽
                    self.combined_capacity_table.resizeColumnsToContents()
                else:
                    # 如果没有数据，清空表格
                    self.combined_capacity_table.setRowCount(0)
                    self.combined_capacity_table.setColumnCount(1)
                    self.combined_capacity_table.setHorizontalHeaderLabels(["幅度/主臂长(m)"])
                    
        except sqlite3.Error as e:
            QMessageBox.warning(self, "数据库错误", f"查询起重能力数据时发生错误: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"发生未知错误: {str(e)}")

    def format_number(self, value):
        """格式化数字
        - 如果是整数，返回整数格式 (例如: 3.0 -> 3)
        - 如果是一位小数，保留一位小数 (例如: 3.5 -> 3.5)
        - 如果是两位小数，保留两位小数 (例如: 3.52 -> 3.52)
        - 如果不是数字，返回原始值
        """
        try:
            # 尝试转换为浮点数
            num = float(value)
            # 检查是否为整数
            if num.is_integer():
                return str(int(num))
            
            # 检查小数位数
            str_num = str(num)
            decimal_part = str_num.split('.')[1]
            
            # 如果小数部分第二位是0或不存在，只保留一位小数
            if len(decimal_part) == 1 or decimal_part[1] == '0':
                return f"{num:.1f}"
            # 否则保留两位小数
            return f"{num:.2f}"
            
        except (ValueError, TypeError):
            return str(value)

    def update_crane_model(self, model):
        """更新起重机型号并检查副臂吊装工况"""
        print(f"开始更新起重机型号: {model}")  # 添加日志
        self.Str_crane_modelName = model
        self.main_boom_conditions = []  # Clear previous data
        self.combined_boom_conditions = []  # Clear previous data

        if not self.cursor:
            QMessageBox.warning(self, "错误", "数据库游标未设置")
            return

        try:
            # 首先检查数据是否存在
            check_query = """
            SELECT COUNT(*) 
            FROM TruckCraneLiftingCapacityData 
            WHERE TruckCraneID = ?
            """
            self.cursor.execute(check_query, (model,))
            count = self.cursor.fetchone()[0]
            print(f"找到的数据记录数: {count}")  # 添加日志

            if count == 0:
                QMessageBox.warning(self, "提示", f"未找到型号 {model} 的起重能力数据")
                return

            # 加载主臂工况数据 - 只检查SpeWorkCondition是否有值
            query_main = """
            SELECT DISTINCT SpeWorkCondition
            FROM TruckCraneLiftingCapacityData
            WHERE TruckCraneID = ?
            AND SpeWorkCondition IS NOT NULL
            AND TRIM(SpeWorkCondition) != ''
            ORDER BY SpeWorkCondition
            """
            self.cursor.execute(query_main, (model,))
            main_conditions = self.cursor.fetchall()
            if main_conditions:
                self.main_boom_conditions = [cond[0] for cond in main_conditions]
                print(f"加载到的主臂工况: {self.main_boom_conditions}")
            else:
                print("未找到主臂工况数据")

            # 检查是否有副臂工况
            query_combined = """
            SELECT DISTINCT SecondSpeWorkCondition
            FROM TruckCraneLiftingCapacityData
            WHERE TruckCraneID = ?
            AND IsJibHosCon = '是'
            AND SecondSpeWorkCondition IS NOT NULL
            AND TRIM(SecondSpeWorkCondition) != ''
            ORDER BY SecondSpeWorkCondition
            """
            self.cursor.execute(query_combined, (model,))
            combined_conditions = self.cursor.fetchall()

            has_auxiliary = len(combined_conditions) > 0
            print(f"是否有副臂工况: {has_auxiliary}")  # 添加日志

            if has_auxiliary:
                self.combined_boom_conditions = [cond[0] for cond in combined_conditions]
                print(f"加载到的主臂+副臂工况: {self.combined_boom_conditions}")

            # 设置界面显示状态
            self.condition_combo.setCurrentText("是" if has_auxiliary else "否")
            self.main_content.setVisible(not has_auxiliary)
            self.tab_widget.setVisible(has_auxiliary)

            # 立即更新表格显示
            if has_auxiliary:
                # 如果有副臂工况，显示标签页模式
                self.tab_widget.setCurrentIndex(0)  # 默认显示主臂标签页
                # 更新两个标签页的数据
                self._populate_condition_table(self.main_condition_table, self.main_boom_conditions)
                self._populate_condition_table(self.combined_condition_table, self.combined_boom_conditions)
            else:
                # 如果只有主臂工况，显示主界面模式
                self._populate_condition_table(self.main_condition_table, self.main_boom_conditions)

            # 清空并重置起重能力表
            self._reset_capacity_tables()

        except sqlite3.Error as e:
            QMessageBox.warning(self, "数据库错误", f"更新起重机型号时发生错误: {str(e)}")
            print(f"数据库错误详情: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"更新起重机型号时发生未知错误: {str(e)}")
            print(f"错误详情: {str(e)}")

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = CraneSettingsDialog()
    dialog.show()
    sys.exit(app.exec_())
