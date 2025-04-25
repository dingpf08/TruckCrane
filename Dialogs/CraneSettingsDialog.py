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
    """起重机械设置主对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []  # Initialize data as a member variable
        self.init_ui()
        
    def init_ui(self):
        # 设置窗口标题
        self.setWindowTitle("起重机械设置")
        # 设置窗口大小
        self.resize(800, 600)
        
        # 连接到数据库
        db_path = os.path.join(ROOT_DIR, 'CraneDataBase')  # 调整为无扩展名
        print(f"Database path: {db_path}")

        try:
            # 建立数据库连接（注意：此处连接的是无扩展名的数据库文件）
            self.connection = sqlite3.connect(db_path)
            # 创建数据库游标对象用于执行SQL操作
            self.cursor = self.connection.cursor()

            # 从数据库TruckCrane表中获取起重机基础数据
            # 数据格式：(TruckCraneID, CraneManufacturers, MaxLiftingWeight)
            self.data = self.fetch_data_from_db()

            # 创建主布局
            layout = QVBoxLayout()
            
            # 创建标签页控件
            self.tab_widget = QTabWidget()
            
            # 创建两个标签页内容
            self.custom_tab = CraneCustomTab(self.data, self.cursor)
            self.capacity_tab = CraneCapacityTab()
            # 设置数据库游标
            self.capacity_tab.set_database_cursor(self.cursor)
            
            # 添加标签页
            self.tab_widget.addTab(self.custom_tab, "起重机自定义")
            self.tab_widget.addTab(self.capacity_tab, "起重机额定起重能力表")
            
            # 将标签页控件添加到主布局
            layout.addWidget(self.tab_widget)
            
            self.setLayout(layout)
            
            # 连接信号
            self.custom_tab.crane_selected.connect(self.on_crane_selected)
            # 添加标签页切换信号连接
            self.tab_widget.currentChanged.connect(self.on_tab_changed)

        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to connect to the database: {e}")
            
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
        """当选择了起重机型号时，更新起重能力表标签页名称并加载工况数据"""
        self.capacity_tab.update_crane_model(model)
        # 更新第二个标签页的名称
        self.tab_widget.setTabText(1, f"{model}起重机额定起重能力表")
        # 加载并显示工况数据
        self.capacity_tab.load_working_conditions(model, self.cursor)

    def on_tab_changed(self, index):
        """处理标签页切换事件"""
        if index == 1:  # 当切换到起重机额定起重能力表标签页时
            try:
                # 查询是否有副臂吊装工况
                query = """
                SELECT DISTINCT IsJibHosCon 
                FROM TruckCraneLiftingCapacityData 
                WHERE TruckCraneID = ?
                """
                
                self.cursor.execute(query, (self.capacity_tab.Str_crane_modelName,))
                result = self.cursor.fetchone()
                
                if result:
                    has_auxiliary = result[0] == "是"
                    
                    # 更新工况选择下拉框
                    self.capacity_tab.condition_combo.setCurrentText("是" if has_auxiliary else "否")
                    
                    # 更新标签页显示
                    self.capacity_tab.main_content.setVisible(not has_auxiliary)
                    self.capacity_tab.tab_widget.setVisible(has_auxiliary)
                    
                    # 如果有副臂吊装工况，显示所有标签页
                    if has_auxiliary:
                        self.capacity_tab.tab_widget.clear()
                        self.capacity_tab.tab_widget.addTab(self.capacity_tab.main_boom_tab, "主臂起重性能表")
                        self.capacity_tab.tab_widget.addTab(self.capacity_tab.combined_boom_tab, "主臂+副臂起重性能表")
                    else:
                        # 如果没有副臂吊装工况，只显示主臂标签页
                        self.capacity_tab.tab_widget.clear()
                        self.capacity_tab.tab_widget.addTab(self.capacity_tab.main_boom_tab, "主臂起重性能表")
                else:
                    QMessageBox.warning(self, "查询结果", f"未找到型号为 {self.capacity_tab.Str_crane_modelName} 的副臂吊装工况信息")
                    
            except sqlite3.Error as e:
                QMessageBox.warning(self, "数据库错误", f"查询副臂吊装工况时发生错误: {str(e)}")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"发生未知错误: {str(e)}")

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
    def __init__(self):
        super().__init__()
        self.Str_crane_modelName = "STC120T5-1"  # 默认的起重机型号名称
        self.cursor = None  # 初始化数据库游标
        self.main_content = QWidget()  # 创建主要内容区域
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
        
        # 连接标签页切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 初始化主要内容区域
        main_content_layout = QVBoxLayout()
        
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
        self.main_content_condition_table = QTableWidget()
        self.init_condition_table(self.main_content_condition_table)
        left_layout.addWidget(self.main_content_condition_table)
        left_layout.addStretch()
        
        # 右侧 - 起重能力表
        right_layout = QVBoxLayout()
        title_label = QLabel("工况1【配重1.2t，支腿全伸】额定起重量(吨)")
        right_layout.addWidget(title_label)
        
        self.main_content_capacity_table = QTableWidget()
        self.init_capacity_table(self.main_content_capacity_table)
        right_layout.addWidget(self.main_content_capacity_table)
        
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 3)
        
        group_layout.addLayout(content_layout)
        main_group.setLayout(group_layout)
        main_content_layout.addWidget(main_group)
        
        self.main_content.setLayout(main_content_layout)
        
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

    def on_tab_changed(self, index):
        """处理标签页切换事件"""
        if not self.cursor or not self.Str_crane_modelName:
            return
            
        try:
            if index == 0:  # 主臂起重性能表
                self.load_main_boom_conditions()
            elif index == 1:  # 主臂+副臂起重性能表
                self.load_combined_boom_conditions()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载工况数据时发生错误: {str(e)}")

    def load_main_boom_conditions(self):
        """加载主臂吊装工况"""
        try:
            # 查询主臂吊装工况
            query = """
            SELECT DISTINCT SpeWorkCondition
            FROM TruckCraneLiftingCapacityData
            WHERE TruckCraneID = ?
            AND SpeWorkCondition IS NOT NULL
            AND SpeWorkCondition != ''
            ORDER BY SpeWorkCondition
            """
            
            self.cursor.execute(query, (self.Str_crane_modelName,))
            conditions = self.cursor.fetchall()
            
            if conditions:
                # 获取唯一的工况列表
                unique_conditions = list(set([cond[0] for cond in conditions if cond[0]]))
                unique_conditions.sort()  # 排序工况
                
                # 设置表格行数
                self.main_content_condition_table.setRowCount(len(unique_conditions))
                
                # 填充工况数据
                for i, condition in enumerate(unique_conditions):
                    # 设置工况编号
                    self.main_content_condition_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                    # 设置工况描述
                    self.main_content_condition_table.setItem(i, 1, QTableWidgetItem(condition))
                    
                # 自动调整列宽
                self.main_content_condition_table.resizeColumnsToContents()
            else:
                QMessageBox.warning(self, "查询结果", f"未找到型号为 {self.Str_crane_modelName} 的主臂吊装工况数据")
                
        except sqlite3.Error as e:
            QMessageBox.warning(self, "数据库错误", f"加载主臂工况数据时发生错误: {str(e)}")

    def load_combined_boom_conditions(self):
        """加载主臂+副臂吊装工况"""
        try:
            # 查询主臂+副臂吊装工况
            query = """
            SELECT DISTINCT SecondSpeWorkCondition
            FROM TruckCraneLiftingCapacityData
            WHERE TruckCraneID = ?
            AND SecondSpeWorkCondition IS NOT NULL
            AND SecondSpeWorkCondition != ''
            ORDER BY SecondSpeWorkCondition
            """
            
            self.cursor.execute(query, (self.Str_crane_modelName,))
            conditions = self.cursor.fetchall()
            
            if conditions:
                # 获取唯一的工况列表
                unique_conditions = list(set([cond[0] for cond in conditions if cond[0]]))
                unique_conditions.sort()  # 排序工况
                
                # 设置表格行数
                self.combined_condition_table.setRowCount(len(unique_conditions))
                
                # 填充工况数据
                for i, condition in enumerate(unique_conditions):
                    # 设置工况编号
                    self.combined_condition_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                    # 设置工况描述
                    self.combined_condition_table.setItem(i, 1, QTableWidgetItem(condition))
                    
                # 自动调整列宽
                self.combined_condition_table.resizeColumnsToContents()
            else:
                QMessageBox.warning(self, "查询结果", f"未找到型号为 {self.Str_crane_modelName} 的主臂+副臂吊装工况数据")
                
        except sqlite3.Error as e:
            QMessageBox.warning(self, "数据库错误", f"加载主臂+副臂工况数据时发生错误: {str(e)}")

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
        
        # 创建主臂工况表格
        self.main_condition_table = QTableWidget()
        self.init_condition_table(self.main_condition_table)
        left_layout.addWidget(self.main_condition_table)
        left_layout.addStretch()
        
        # 右侧 - 起重能力表
        right_layout = QVBoxLayout()
        title_label = QLabel("工况1【配重1.2t，支腿全伸】额定起重量(吨)")
        right_layout.addWidget(title_label)
        
        self.main_capacity_table = QTableWidget()
        self.init_capacity_table(self.main_capacity_table)
        right_layout.addWidget(self.main_capacity_table)
        
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
        
        # 创建主臂+副臂工况表格
        self.combined_condition_table = QTableWidget()
        self.init_condition_table(self.combined_condition_table)
        left_layout.addWidget(self.combined_condition_table)
        left_layout.addStretch()
        
        # 右侧 - 起重能力表
        right_layout = QVBoxLayout()
        title_label = QLabel("工况1【配重6.2吨，副臂长度8m，副臂安装角度0°，支腿全伸】额定起重量(吨)")
        right_layout.addWidget(title_label)
        
        self.combined_capacity_table = QTableWidget()
        self.init_capacity_table(self.combined_capacity_table, is_combined=True)
        right_layout.addWidget(self.combined_capacity_table)
        
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 3)
        
        group_layout.addLayout(content_layout)
        main_group.setLayout(group_layout)
        layout.addWidget(main_group)
        
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
        if text == "是":
            self.main_content.setVisible(False)
            self.tab_widget.setVisible(True)
        else:
            self.main_content.setVisible(True)
            self.tab_widget.setVisible(False)
        
    def update_crane_model(self, model):
        """更新起重机型号并检查副臂吊装工况"""
        self.Str_crane_modelName = model
        
        try:
            # 查询是否有副臂吊装工况
            query = """
            SELECT DISTINCT IsJibHosCon 
            FROM TruckCraneLiftingCapacityData 
            WHERE TruckCraneID = ?
            """
            
            self.cursor.execute(query, (model,))
            result = self.cursor.fetchone()
            
            if result:
                has_auxiliary = result[0] == "是"
                
                # 更新工况选择下拉框
                self.condition_combo.setCurrentText("是" if has_auxiliary else "否")
                
                # 更新标签页显示
                self.main_content.setVisible(not has_auxiliary)
                self.tab_widget.setVisible(has_auxiliary)
                
                # 如果有副臂吊装工况，显示所有标签页
                if has_auxiliary:
                    self.tab_widget.clear()
                    self.tab_widget.addTab(self.main_boom_tab, "主臂起重性能表")
                    self.tab_widget.addTab(self.combined_boom_tab, "主臂+副臂起重性能表")
                else:
                    # 如果没有副臂吊装工况，只显示主臂标签页
                    self.tab_widget.clear()
                    self.tab_widget.addTab(self.main_boom_tab, "主臂起重性能表")
            else:
                QMessageBox.warning(self, "查询结果", f"未找到型号为 {model} 的副臂吊装工况信息")
                
        except sqlite3.Error as e:
            QMessageBox.warning(self, "数据库错误", f"查询副臂吊装工况时发生错误: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"发生未知错误: {str(e)}")

    def set_database_cursor(self, cursor):
        """设置数据库游标"""
        self.cursor = cursor
        
    def load_working_conditions(self, crane_model, cursor):
        """加载起重机工况数据"""
        try:
            self.cursor = cursor  # 更新游标
            # 查询该型号的所有工况
            query = """
            SELECT DISTINCT SpeWorkCondition
            FROM TruckCraneLiftingCapacityData
            WHERE TruckCraneID = ?
            ORDER BY SpeWorkCondition
            """
            
            self.cursor.execute(query, (crane_model,))
            conditions = self.cursor.fetchall()
            
            if conditions:
                # 获取唯一的工况列表
                unique_conditions = list(set([cond[0] for cond in conditions if cond[0]]))
                unique_conditions.sort()  # 排序工况
                
                # 设置表格行数
                self.main_content_condition_table.setRowCount(len(unique_conditions))
                
                # 填充工况数据
                for i, condition in enumerate(unique_conditions):
                    # 设置工况编号
                    self.main_content_condition_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                    # 设置工况描述
                    self.main_content_condition_table.setItem(i, 1, QTableWidgetItem(condition))
                    
                # 自动调整列宽
                self.main_content_condition_table.resizeColumnsToContents()
                
            else:
                QMessageBox.warning(self, "查询结果", f"未找到型号为 {crane_model} 的工况数据")
                
        except sqlite3.Error as e:
            QMessageBox.warning(self, "数据库错误", f"加载工况数据时发生错误: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载工况数据时发生未知错误: {str(e)}")

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

    def on_condition_clicked(self, item):
        if self.tab_widget.isVisible():
            current_tab = self.tab_widget.currentWidget()
            if current_tab == self.main_boom_tab:
                condition = self.main_condition_table.item(item.row(), 1).text()
                self.load_capacity_data(condition, is_combined=False)
            elif current_tab == self.combined_boom_tab:
                condition = self.combined_condition_table.item(item.row(), 1).text()
                self.load_capacity_data(condition, is_combined=True)
        else:
            condition = self.main_content_condition_table.item(item.row(), 1).text()
            self.load_capacity_data(condition, is_combined=False)

    def load_capacity_data(self, condition, is_combined=False):
        """加载起重能力数据"""
        try:
            # 根据是否是组合工况选择不同的查询
            if is_combined:
                query = """
                SELECT 
                    TruckCraneRange,           -- 汽车吊幅
                    TruckCraneMainArmLen,      -- 主臂长
                    TruckCraneRatedLiftingCap  -- 额定起重量
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND SecondSpeWorkCondition = ?
                AND TruckCraneRatedLiftingCap IS NOT NULL 
                AND TruckCraneRatedLiftingCap != ''
                ORDER BY CAST(TruckCraneMainArmLen AS FLOAT) ASC, CAST(TruckCraneRange AS FLOAT) ASC
                """
            else:
                query = """
                SELECT 
                    TruckCraneRange,           -- 汽车吊幅
                    TruckCraneMainArmLen,      -- 主臂长
                    TruckCraneRatedLiftingCap  -- 额定起重量
                FROM TruckCraneLiftingCapacityData
                WHERE TruckCraneID = ?
                AND SpeWorkCondition = ?
                AND TruckCraneRatedLiftingCap IS NOT NULL 
                AND TruckCraneRatedLiftingCap != ''
                ORDER BY CAST(TruckCraneMainArmLen AS FLOAT) ASC, CAST(TruckCraneRange AS FLOAT) ASC
                """
            
            self.cursor.execute(query, (self.Str_crane_modelName, condition))
            data = self.cursor.fetchall()
            
            if data:
                # 获取要填充的表格
                if self.tab_widget.isVisible():
                    if is_combined:
                        target_table = self.combined_capacity_table
                    else:
                        target_table = self.main_capacity_table
                else:
                    target_table = self.main_content_capacity_table
                
                # 创建一个字典来存储额定起重量数据
                capacity_dict = {}
                valid_ranges = set()
                valid_arm_lengths = set()
                
                # 首先收集所有有效的数据
                for row in data:
                    range_val = self.format_number(row[0])
                    arm_len = self.format_number(row[1])
                    lifting_cap = row[2]
                    
                    # 只处理有效的额定起重量数据
                    if lifting_cap and str(lifting_cap).strip():
                        try:
                            if float(lifting_cap) > 0:
                                capacity_dict[(range_val, arm_len)] = self.format_number(lifting_cap)
                                valid_ranges.add(range_val)
                                valid_arm_lengths.add(arm_len)
                        except ValueError:
                            continue
                
                # 转换为排序后的列表
                ranges = sorted(list(valid_ranges), key=lambda x: float(x) if x else 0)
                main_arm_lengths = sorted(list(valid_arm_lengths), key=lambda x: float(x) if x else 0)
                
                # 设置表格的行数和列数
                target_table.setRowCount(len(ranges))
                target_table.setColumnCount(len(main_arm_lengths) + 1)
                
                # 设置表格标题
                headers = ["幅度/主臂长(m)"] + main_arm_lengths
                target_table.setHorizontalHeaderLabels(headers)
                
                # 填充第一列（吊幅值）
                for i, range_val in enumerate(ranges):
                    target_table.setItem(i, 0, QTableWidgetItem(range_val))
                
                # 填充额定起重量数据
                for i, range_val in enumerate(ranges):
                    for j, arm_len in enumerate(main_arm_lengths):
                        # 获取对应的额定起重量，如果不存在则设置为空字符串
                        capacity = capacity_dict.get((range_val, arm_len), "")
                        target_table.setItem(i, j + 1, QTableWidgetItem(capacity))
                
                # 调整表格显示
                target_table.resizeColumnsToContents()
                target_table.resizeRowsToContents()
                
            else:
                QMessageBox.warning(self, "查询结果", f"未找到工况 '{condition}' 的数据")
                
        except sqlite3.Error as e:
            QMessageBox.warning(self, "数据库错误", f"查询数据时发生错误: {str(e)}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"发生未知错误: {str(e)}")

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = CraneSettingsDialog()
    dialog.show()
    sys.exit(app.exec_())
