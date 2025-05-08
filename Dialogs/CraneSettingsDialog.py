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
                # 保证主臂tab相关控件可见
                self.capacity_tab.main_condition_table.setVisible(True)
                self.capacity_tab.main_capacity_table.setVisible(True)
                if self.capacity_tab.main_capacity_title:
                    self.capacity_tab.main_capacity_title.setVisible(True)

            elif index == 1:  # 主臂+副臂起重性能表
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
                # 保证副臂tab相关控件可见
                self.capacity_tab.combined_condition_table.setVisible(True)
                self.capacity_tab.combined_capacity_table.setVisible(True)
                if self.capacity_tab.combined_capacity_title:
                    self.capacity_tab.combined_capacity_title.setVisible(True)

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
    """起重机额定起重能力表标签页"""
    def __init__(self, cursor):
        super().__init__()
        self.Str_crane_modelName = None
        self.cursor = cursor
        self.main_boom_conditions = []
        self.combined_boom_conditions = []
        # 主界面模式专用表格
        self.main_condition_table_main = QTableWidget()
        self.main_condition_table_main.setColumnCount(2)
        self.main_condition_table_main.setHorizontalHeaderLabels(["工况编号", "具体工况"])
        self.main_condition_table_main.horizontalHeader().setStretchLastSection(True)
        self.main_condition_table_main.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.main_condition_table_main.setColumnWidth(0, 80)
        self.main_condition_table_main.setSelectionBehavior(QTableWidget.SelectRows)
        self.main_condition_table_main.setSelectionMode(QTableWidget.SingleSelection)
        self.main_condition_table_main.setEditTriggers(QTableWidget.NoEditTriggers)
        self.main_condition_table_main.setMinimumWidth(300)
        self.main_condition_table_main.setMinimumHeight(200)
        self.main_condition_table_main.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)
        self.main_condition_table_main.itemClicked.connect(self.on_condition_clicked)
        self.main_capacity_table_main = QTableWidget()
        self.main_capacity_title_main = QLabel("额定起重量(吨)")
        # tab模式专用表格
        self.main_condition_table = QTableWidget()
        self.main_condition_table.setColumnCount(2)
        self.main_condition_table.setHorizontalHeaderLabels(["工况编号", "具体工况"])
        self.main_condition_table.horizontalHeader().setStretchLastSection(True)
        self.main_condition_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.main_condition_table.setColumnWidth(0, 80)
        self.main_condition_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.main_condition_table.setSelectionMode(QTableWidget.SingleSelection)
        self.main_condition_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.main_condition_table.setMinimumWidth(300)
        self.main_condition_table.setMinimumHeight(200)
        self.main_condition_table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)
        self.main_condition_table.itemClicked.connect(self.on_condition_clicked)
        self.main_capacity_table = QTableWidget()
        self.main_capacity_title = QLabel("额定起重量(吨)")
        self.combined_condition_table = None
        self.combined_capacity_table = None
        self.combined_capacity_title = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("是否有副臂吊装工况:"))
        self.condition_combo = QComboBox()
        self.condition_combo.addItems(["否", "是"])
        top_layout.addWidget(self.condition_combo)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        self.tab_widget = QTabWidget()
        self.tab_widget.setVisible(False)
        # 主臂tab
        self.main_boom_tab = QWidget()
        tab1_layout = QVBoxLayout()
        group1 = QGroupBox("主臂起重性能表")
        group1_layout = QVBoxLayout()
        method1_layout = QHBoxLayout()
        method1_layout.addWidget(QLabel("额定起重量确定方法:"))
        method1_combo = QComboBox()
        method1_layout.addWidget(method1_combo)
        method1_layout.addStretch()
        group1_layout.addLayout(method1_layout)
        content1_layout = QHBoxLayout()
        left1_layout = QVBoxLayout()
        left1_layout.addWidget(QLabel("主臂吊装工况:"))
        left1_layout.addWidget(self.main_condition_table)
        left1_layout.addStretch()
        right1_layout = QVBoxLayout()
        right1_layout.addWidget(self.main_capacity_title)
        right1_layout.addWidget(self.main_capacity_table)
        content1_layout.addLayout(left1_layout, 1)
        content1_layout.addLayout(right1_layout, 2)
        group1_layout.addLayout(content1_layout)
        group1.setLayout(group1_layout)
        tab1_layout.addWidget(group1)
        self.main_boom_tab.setLayout(tab1_layout)
        self.tab_widget.addTab(self.main_boom_tab, "主臂起重性能表")
        # 主臂+副臂tab
        self.combined_boom_tab = QWidget()
        tab2_layout = QVBoxLayout()
        group2 = QGroupBox("主臂+副臂起重性能表")
        group2_layout = QVBoxLayout()
        method2_layout = QHBoxLayout()
        method2_layout.addWidget(QLabel("额定起重量确定方法:"))
        method2_combo = QComboBox()
        method2_layout.addWidget(method2_combo)
        method2_layout.addStretch()
        group2_layout.addLayout(method2_layout)
        content2_layout = QHBoxLayout()
        left2_layout = QVBoxLayout()
        left2_layout.addWidget(QLabel("主臂+副臂吊装工况:"))
        self.combined_condition_table = QTableWidget()
        self.combined_condition_table.setColumnCount(2)
        self.combined_condition_table.setHorizontalHeaderLabels(["工况编号", "具体工况"])
        self.combined_condition_table.horizontalHeader().setStretchLastSection(True)
        self.combined_condition_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.combined_condition_table.setColumnWidth(0, 80)
        self.combined_condition_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.combined_condition_table.setSelectionMode(QTableWidget.SingleSelection)
        self.combined_condition_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.combined_condition_table.setMinimumWidth(300)
        self.combined_condition_table.setMinimumHeight(200)
        self.combined_condition_table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)
        self.combined_condition_table.itemClicked.connect(self.on_condition_clicked)
        left2_layout.addWidget(self.combined_condition_table)
        left2_layout.addStretch()
        right2_layout = QVBoxLayout()
        self.combined_capacity_title = QLabel("额定起重量(吨)")
        right2_layout.addWidget(self.combined_capacity_title)
        self.combined_capacity_table = QTableWidget()
        right2_layout.addWidget(self.combined_capacity_table)
        content2_layout.addLayout(left2_layout, 1)
        content2_layout.addLayout(right2_layout, 2)
        group2_layout.addLayout(content2_layout)
        group2.setLayout(group2_layout)
        tab2_layout.addWidget(group2)
        self.combined_boom_tab.setLayout(tab2_layout)
        self.tab_widget.addTab(self.combined_boom_tab, "主臂+副臂起重性能表")
        # 主界面模式
        self.main_content = QWidget()
        main_content_layout = QVBoxLayout()
        group = QGroupBox("主臂起重性能表")
        group_layout = QVBoxLayout()
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("额定起重量确定方法:"))
        self.method_combo = QComboBox()
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        group_layout.addLayout(method_layout)
        content_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("主臂吊装工况:"))
        left_layout.addWidget(self.main_condition_table_main)
        left_layout.addStretch()
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.main_capacity_title_main)
        right_layout.addWidget(self.main_capacity_table_main)
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 2)
        group_layout.addLayout(content_layout)
        group.setLayout(group_layout)
        main_content_layout.addWidget(group)
        self.main_content.setLayout(main_content_layout)
        main_layout.addWidget(self.main_content)
        main_layout.addWidget(self.tab_widget)
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
        self.setLayout(main_layout)
        self.condition_combo.currentTextChanged.connect(self.on_condition_changed)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.main_content.setVisible(True)
        self.tab_widget.setVisible(False)

    def on_condition_changed(self, text):
        try:
            if text == "是":
                self.main_content.setVisible(False)
                self.tab_widget.setVisible(True)
                self._populate_condition_table(self.main_condition_table, self.main_boom_conditions)
                self._populate_condition_table(self.combined_condition_table, self.combined_boom_conditions)
                self.tab_widget.setCurrentIndex(0)
            else:
                self.main_content.setVisible(True)
                self.tab_widget.setVisible(False)
                self._populate_condition_table(self.main_condition_table_main, self.main_boom_conditions)
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
                # 保证主臂tab相关控件可见
                self.main_condition_table.setVisible(True)
                self.main_capacity_table.setVisible(True)
                if self.main_capacity_title:
                    self.main_capacity_title.setVisible(True)

            elif index == 1:  # 主臂+副臂起重性能表
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
                # 保证副臂tab相关控件可见
                self.combined_condition_table.setVisible(True)
                self.combined_capacity_table.setVisible(True)
                if self.combined_capacity_title:
                    self.combined_capacity_title.setVisible(True)

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
            # 判断当前是主界面还是tab模式
            if self.main_content.isVisible():
                table = self.main_condition_table_main
                capacity_table = self.main_capacity_table_main
                capacity_title = self.main_capacity_title_main
            else:
                current_tab = self.tab_widget.currentWidget()
                if current_tab == self.main_boom_tab:
                    table = self.main_condition_table
                    capacity_table = self.main_capacity_table
                    capacity_title = self.main_capacity_title
                elif current_tab == self.combined_boom_tab:
                    table = self.combined_condition_table
                    capacity_table = self.combined_capacity_table
                    capacity_title = self.combined_capacity_title
                else:
                    return
            if table is None or item is None:
                return
            cell = table.item(item.row(), 1)
            if cell is None:
                return
            condition = cell.text()
            # 更新标题
            if capacity_title:
                capacity_title.setText(f"工况{item.row() + 1}【{condition}】额定起重量(吨)")
            # 查询对应的起重能力数据
            if (self.main_content.isVisible() or (not self.main_content.isVisible() and self.tab_widget.currentWidget() == self.main_boom_tab)):
                # 主臂工况，无论主界面还是tab，都只查SpeWorkCondition
                query = """
                SELECT DISTINCT 
                    TruckCraneRange,           -- 汽车吊幅度
                    TruckCraneMainArmLen,      -- 主臂长度
                    TruckCraneRatedLiftingCap  -- 额定起重量
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND SpeWorkCondition = ?
                AND TruckCraneRatedLiftingCap IS NOT NULL
                AND TruckCraneRatedLiftingCap != ''
                ORDER BY CAST(TruckCraneRange AS FLOAT)
                """
                self.cursor.execute(query, (self.Str_crane_modelName, condition))
                data = self.cursor.fetchall()
                if data:
                    arm_lengths = sorted(set(str(row[1]) for row in data), key=lambda x: float(x) if x else 0)
                    ranges = sorted(set(str(row[0]) for row in data), key=lambda x: float(x) if x else 0)
                    capacity_table.setColumnCount(len(arm_lengths) + 1)
                    headers = ["幅度/主臂长(m)"] + arm_lengths
                    capacity_table.setHorizontalHeaderLabels(headers)
                    capacity_table.setRowCount(len(ranges))
                    capacity_dict = {}
                    for row in data:
                        capacity_dict[(str(row[0]), str(row[1]))] = str(row[2])
                    for i, range_val in enumerate(ranges):
                        capacity_table.setItem(i, 0, QTableWidgetItem(str(range_val)))
                        for j, arm_len in enumerate(arm_lengths):
                            capacity = capacity_dict.get((range_val, arm_len), "")
                            if capacity:
                                formatted_capacity = self.format_number(capacity)
                                capacity_table.setItem(i, j + 1, QTableWidgetItem(formatted_capacity))
                            else:
                                capacity_table.setItem(i, j + 1, QTableWidgetItem(""))
                    capacity_table.resizeColumnsToContents()
                else:
                    capacity_table.setRowCount(0)
                    capacity_table.setColumnCount(1)
                    capacity_table.setHorizontalHeaderLabels(["幅度/主臂长(m)"])
            elif table == self.combined_condition_table:
                query = """
                SELECT DISTINCT 
                    SecondElevation,           -- 幅度（纵坐标）
                    SecondMainArmLen,          -- 主臂长（表头）
                    SecondTruckCraneRatedLiftingCap  -- 额定起重量
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND SecondSpeWorkCondition = ?
                AND SecondTruckCraneRatedLiftingCap IS NOT NULL
                AND SecondTruckCraneRatedLiftingCap != ''
                ORDER BY CAST(SecondElevation AS FLOAT)
                """
                self.cursor.execute(query, (self.Str_crane_modelName, condition))
                data = self.cursor.fetchall()
                if data:
                    arm_lengths = sorted(set(str(row[1]) for row in data), key=lambda x: float(x) if x else 0)
                    elevations = sorted(set(str(row[0]) for row in data), key=lambda x: float(x) if x else 0)
                    capacity_table.setColumnCount(len(arm_lengths) + 1)
                    headers = ["幅度/仰角(m/°)"] + arm_lengths
                    capacity_table.setHorizontalHeaderLabels(headers)
                    capacity_table.setRowCount(len(elevations))
                    capacity_dict = {}
                    for row in data:
                        capacity_dict[(str(row[0]), str(row[1]))] = str(row[2])
                    for i, elevation in enumerate(elevations):
                        capacity_table.setItem(i, 0, QTableWidgetItem(str(elevation)))
                        for j, arm_len in enumerate(arm_lengths):
                            capacity = capacity_dict.get((elevation, arm_len), "")
                            if capacity:
                                formatted_capacity = self.format_number(capacity)
                                capacity_table.setItem(i, j + 1, QTableWidgetItem(formatted_capacity))
                            else:
                                capacity_table.setItem(i, j + 1, QTableWidgetItem(""))
                    capacity_table.resizeColumnsToContents()
                else:
                    capacity_table.setRowCount(0)
                    capacity_table.setColumnCount(1)
                    capacity_table.setHorizontalHeaderLabels(["幅度/仰角(m/°)"])
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
                self._populate_condition_table(self.main_condition_table_main, self.main_boom_conditions)

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
