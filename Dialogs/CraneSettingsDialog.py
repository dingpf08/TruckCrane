from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget,
                           QComboBox, QLabel, QGridLayout, QGroupBox,
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QTabWidget, QLineEdit, QCheckBox,
                           QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import os
import sqlite3
# 起重机械设置对话框的数据流和逻辑
#
# 1. 初始化：
#    - 初始化 CraneSettingsDialog，设置 UI 并连接到数据库。
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
    """起重机械设置主对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []  # Initialize data as a member variable
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("起重机械设置")
        self.resize(800, 600)
        
        # Connect to the database
        db_path = os.path.join(ROOT_DIR, 'CraneDataBase')  # Adjusted for no extension
        print(f"Database path: {db_path}")

        try:
            # 建立数据库连接（注意：此处连接的是无扩展名的数据库文件）
            self.connection = sqlite3.connect(db_path)
            # 创建数据库游标对象用于执行SQL操作
            self.cursor = self.connection.cursor()

            # 从数据库TruckCrane表中获取起重机基础数据
            # 数据格式：(TruckCraneID, CraneManufacturers, MaxLiftingWeight)
            self.data = self.fetch_data_from_db()

        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to connect to the database: {e}")
        
        # 创建主布局
        layout = QVBoxLayout()
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        
        # 创建两个标签页内容
        self.custom_tab = CraneCustomTab(self.data, self.cursor)
        self.capacity_tab = CraneCapacityTab()
        
        # 添加标签页
        self.tab_widget.addTab(self.custom_tab, "起重机自定义")
        self.tab_widget.addTab(self.capacity_tab, "起重机额定起重能力表")
        
        # 将标签页控件添加到主布局
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
        
        # 连接信号
        self.custom_tab.crane_selected.connect(self.on_crane_selected)

    def fetch_data_from_db(self):
        """从数据库获取起重机基础数据
        数据来源：TruckCrane表
        数据结构：元组(TruckCraneID, 厂家, 最大起重量)
        数据用途：用于填充起重机自定义标签页的表格"""
        # SQL查询语句：选择起重机核心参数
        query = """
        SELECT TruckCraneID, CraneManufacturers, MaxLiftingWeight
        FROM TruckCrane
        """
        self.cursor.execute(query)  # 执行数据库查询
        data = self.cursor.fetchall()  # 获取全部查询结果

        # 格式化数据用于消息框展示（开发阶段调试用）
        # 格式示例：Model: STC120T5-1, Manufacturer: 三一, Capacity: 120
        data_str = "\n".join([f"Model: {model}, Manufacturer: {manufacturer}, Capacity: {capacity}"
                              for model, manufacturer, capacity in data])

        # 弹窗显示查询结果（正式版本建议移除，此处用于数据验证）
        #QMessageBox.information(self, "Fetched Data", data_str)

        return data  # 返回原始数据用于表格填充

    def on_crane_selected(self, model):
        """当选择了起重机型号时，更新起重能力表标签页名称"""
        self.capacity_tab.update_crane_model(model)
        # 更新第二个标签页的名称
        self.tab_widget.setTabText(1, f"{model}起重机额定起重能力表")

class CraneCustomTab(QWidget):
    """起重机自定义标签页"""
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
        self.axle_table.setHorizontalHeaderLabels(["第排车轮", "依次轴距(mm)", "轴荷(吨)"])
        self.axle_table.setRowCount(2)

        # 设置示例数据
        self.axle_table.setItem(0, 0, QTableWidgetItem("2"))
        self.axle_table.setItem(0, 1, QTableWidgetItem("4760"))
        self.axle_table.setItem(0, 2, QTableWidgetItem("13.000"))
        self.axle_table.setItem(1, 0, QTableWidgetItem("3"))
        self.axle_table.setItem(1, 1, QTableWidgetItem("1360"))
        self.axle_table.setItem(1, 2, QTableWidgetItem("13.000"))

        axle_layout.addWidget(self.axle_table, 2, 0, 1, 2)

        # 添加其他参数输入
        params = [
            ("起重机总重(吨):", "34.1"),
            ("支腿纵向距离L(m):", "5.4"),
            ("支腿横向距离B(m):", "6.4"),
            ("是否录入额定起重量表:", "是"),
            ("主臂铰链中心至地面距离h(m):", "3.05"),
            ("主臂铰链中心至回转中心距离a1(m):", "1.6")
        ]

        for i, (label, value) in enumerate(params):
            axle_layout.addWidget(QLabel(label), i + 3, 0)
            if label == "是否录入额定起重量表:":
                combo = QComboBox()
                combo.addItems(["是", "否"])
                axle_layout.addWidget(combo, i + 3, 1)
            else:
                edit = QLineEdit(value)
                axle_layout.addWidget(edit, i + 3, 1)

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
        """当点击表格项时"""
        row = item.row()
        model = self.table.item(row, 1).text()  # 获取型号列的文本
        self.crane_selected.emit(model)
        
        # Fetch detailed information from the database
        query = """
        SELECT CraneManufacturers, AxesNums, CraneTotalWeight, OutriggerLongDis,
               OutriggersHorizDis, IsEnterRatedWT, DisMAHToGroud, DisMAHToRotaCen
        FROM TruckCraneDetailInfo
        WHERE TruckCraneID = ?
        """
        self.cursor.execute(query, (model,))
        detail = self.cursor.fetchone()

        if detail:
            manufacturer, axes_nums, total_weight, long_dis, horiz_dis, is_enter_rated, dis_to_ground, dis_to_rotacen = detail
            
            # Populate the UI components with the fetched data
            self.manufacturer_edit.setText(manufacturer)
            self.axle_count_edit.setText(str(axes_nums))
            self.first_axle_load_edit.setText(str(total_weight))
            self.calc_checkbox.setChecked(is_enter_rated == "是")
            self.model_edit.setText(model)
            
            # Assuming you have QLineEdit for these fields
            self.axle_count_edit.setText(str(axes_nums))
            self.first_axle_load_edit.setText(str(total_weight))
            self.calc_checkbox.setChecked(is_enter_rated == "是")
            self.model_edit.setText(model)
            
            # Populate other fields if you have them
            # Example:
            # self.some_other_field.setText(str(long_dis))
            # self.another_field.setText(str(horiz_dis))

class CraneCapacityTab(QWidget):
    """起重机额定起重能力表标签页"""
    def __init__(self):
        super().__init__()
        self.Str_crane_modelName = "STC120T5-1"  # 默认的起重机型号名称
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # 顶部 - 副臂装置工况选择
        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("是否有副臂吊装工况:"))
        self.condition_combo = QComboBox()
        self.condition_combo.addItem("否")
        self.condition_combo.addItem("是")
        top_layout.addWidget(self.condition_combo)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        
        # 创建标签页控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setVisible(False)  # 初始设置为不可见
        
        # 创建主臂起重性能表标签页
        self.main_boom_tab = QWidget()
        self.init_main_boom_tab()
        self.tab_widget.addTab(self.main_boom_tab, "主臂起重性能表")
        
        # 创建主臂+副臂起重性能表标签页
        self.combined_boom_tab = QWidget()
        self.init_combined_boom_tab()
        self.tab_widget.addTab(self.combined_boom_tab, "主臂+副臂起重性能表")
        
        # 创建主要内容区域（非标签页模式）
        self.main_content = QWidget()
        self.init_main_content()
        
        main_layout.addWidget(self.main_content)
        main_layout.addWidget(self.tab_widget)
        
        # 底部说明文字
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
        
        # 连接信号
        self.condition_combo.currentTextChanged.connect(self.on_condition_changed)
        
    def init_main_content(self):
        """初始化主要内容区域（非标签页模式）"""
        layout = QVBoxLayout()
        
        # 主臂起重性能表组
        main_group = QGroupBox("主臂起重性能表")
        group_layout = QVBoxLayout()
        
        # 额定起重量确定方法
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("额定起重量确定方法:"))
        self.method_combo = QComboBox()
        self.method_combo.addItem("根据幅度、主臂长确定")
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        group_layout.addLayout(method_layout)
        
        # 主要内容区域 - 左右分布
        content_layout = QHBoxLayout()
        
        # 左侧 - 工况列表
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("主臂吊装工况:"))
        
        # 工况表格
        self.condition_table = QTableWidget()
        self.init_condition_table(self.condition_table)
        left_layout.addWidget(self.condition_table)
        left_layout.addStretch()
        
        # 右侧 - 起重能力表
        right_layout = QVBoxLayout()
        title_label = QLabel("工况1【配重1.2t，支腿全伸】额定起重量(吨)")
        right_layout.addWidget(title_label)
        
        self.capacity_table = QTableWidget()
        self.init_capacity_table(self.capacity_table)
        right_layout.addWidget(self.capacity_table)
        
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 3)
        
        group_layout.addLayout(content_layout)
        main_group.setLayout(group_layout)
        layout.addWidget(main_group)
        
        self.main_content.setLayout(layout)
        
    def init_main_boom_tab(self):
        """初始化主臂起重性能表标签页"""
        layout = QVBoxLayout()
        
        # 复制主要内容的布局
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
        
        condition_table = QTableWidget()
        self.init_condition_table(condition_table)
        left_layout.addWidget(condition_table)
        left_layout.addStretch()
        
        # 右侧 - 起重能力表
        right_layout = QVBoxLayout()
        title_label = QLabel("工况1【配重1.2t，支腿全伸】额定起重量(吨)")
        right_layout.addWidget(title_label)
        
        capacity_table = QTableWidget()
        self.init_capacity_table(capacity_table)
        right_layout.addWidget(capacity_table)
        
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 3)
        
        group_layout.addLayout(content_layout)
        main_group.setLayout(group_layout)
        layout.addWidget(main_group)
        
        self.main_boom_tab.setLayout(layout)
        
    def init_combined_boom_tab(self):
        """初始化主臂+副臂起重性能表标签页"""
        layout = QVBoxLayout()
        
        # 主臂+副臂起重性能表组
        main_group = QGroupBox("主臂+副臂起重性能表")
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
        
        condition_table = QTableWidget()
        self.init_condition_table(condition_table)
        left_layout.addWidget(condition_table)
        left_layout.addStretch()
        
        # 右侧 - 起重能力表
        right_layout = QVBoxLayout()
        title_label = QLabel("工况1【配重6.2吨，副臂长度8m，副臂安装角度0°，支腿全伸】额定起重量(吨)")
        right_layout.addWidget(title_label)
        
        capacity_table = QTableWidget()
        self.init_capacity_table(capacity_table, is_combined=True)
        right_layout.addWidget(capacity_table)
        
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 3)
        
        group_layout.addLayout(content_layout)
        main_group.setLayout(group_layout)
        layout.addWidget(main_group)
        
        self.combined_boom_tab.setLayout(layout)
        
    def init_condition_table(self, table):
        """初始化工况表格"""
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["工况", "具体工况"])
        table.setRowCount(2)
        
        conditions = [
            ("1", "配重1.2t，支腿全伸"),
            ("2", "配重1.2t，支腿半伸")
        ]
        
        for i, (condition, detail) in enumerate(conditions):
            item1 = QTableWidgetItem(condition)
            item2 = QTableWidgetItem(detail)
            item1.setFlags(item1.flags() & ~Qt.ItemIsEditable)
            item2.setFlags(item2.flags() & ~Qt.ItemIsEditable)
            table.setItem(i, 0, item1)
            table.setItem(i, 1, item2)
        
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setMinimumWidth(300)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.setColumnWidth(0, 50)
        
    def init_capacity_table(self, table, is_combined=False):
        """初始化起重能力表"""
        if not is_combined:
            # 主臂起重能力表
            headers = ["幅度/主臂长(m)", "9.6", "15.08", "20.56", "26.04", "31.52", "37"]
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            
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
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            
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
        
        table.setRowCount(len(data))
        
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(value if value else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                table.setItem(i, j, item)
        
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(True)
        table.setWordWrap(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #0078D7;
                color: white;
            }
        """)
        
    def on_condition_changed(self, text):
        """当副臂装置工况选择改变时"""
        if text == "是":
            self.main_content.setVisible(False)
            self.tab_widget.setVisible(True)
        else:
            self.main_content.setVisible(True)
            self.tab_widget.setVisible(False)
        
    def update_crane_model(self, model):
        """更新起重机型号"""
        self.Str_crane_modelName = model

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = CraneSettingsDialog()
    dialog.show()
    sys.exit(app.exec_())
