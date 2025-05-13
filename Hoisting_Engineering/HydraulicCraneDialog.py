"""
主对话框：液压汽车起重机吊装计算界面模块
Hydraulic Truck Crane Lifting Calculation Dialog Module

本模块实现了液压汽车起重机吊装计算的图形用户界面，
包括参数输入、起重机选型、相关参数设置及工况图展示等功能。

主要类：
    HydraulicCraneDialog: 主对话框，负责整体界面布局与数据交互。
    ImageLabel: 支持缩放与拖拽的图片显示控件。

子对话框：
    CraneRequirementsDialog: 吊装要求设置子对话框。
    CraneSelectionDialog: 起重机选型子对话框。
    CraneParametersDialog: 起重机相关参数设置子对话框。

每个子对话框负责其对应参数的采集与校验，通过信号与主对话框联动。
"""
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QRadioButton, QButtonGroup, QGroupBox, QComboBox, QGridLayout, QFormLayout, QSplitter, QWidget, QMessageBox, QFrame, QTabWidget, QSizePolicy
)
import sys
import os
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QPainter
from DataStruDef.EarthSlopeCalculation import VerificationProject
from DataStruDef.HydraulicCraneData import HydraulicCraneData
from Hoisting_Engineering.CraneRequirementsDialog import CraneRequirementsDialog
from Hoisting_Engineering.CraneSelectionDialog import CraneSelectionDialog
from Hoisting_Engineering.CraneParametersDialog import CraneParametersDialog
# para_uuid:
# 类型：UUID 或 None
# 作用：用于唯一标识对话框实例。如果没有提供，则在初始化时生成一个新的UUID。这在需要跟踪多个对话框实例时非常有用。
# para_craneData:
# 类型：字典或 None
# 作用：包含吊装计算所需的初始数据。如果没有提供，则使用默认值初始化。字典中的键值对包括：
# "load_capacity": 吊装能力，以吨为单位。
# "boom_length": 吊臂长度，以米为单位。
# "working_radius": 工作半径，以米为单位。#

class ImageLabel(QLabel):
    """
    支持缩放与拖拽的图片显示控件。
    Image display widget with zoom and drag support.
    """
    def __init__(self, parent=None):
        """
        初始化图片控件。
        Args:
            parent: 父控件。
        """
        super().__init__(parent)
        self._pixmap = None  # 当前显示的QPixmap对象
        self._scale = 1.0    # 当前缩放比例
        self._offset = QPoint(0, 0)  # 拖拽偏移量
        self._dragging = False  # 是否正在拖拽
        self._last_pos = None   # 上一次鼠标位置

    def setPixmap(self, pixmap):
        """
        设置要显示的图片，并重置缩放与偏移。
        Set the pixmap to display and reset scale/offset.
        Args:
            pixmap: QPixmap对象。
        """
        self._pixmap = pixmap
        self._scale = 1.0
        self._offset = QPoint(0, 0)
        self.update_image()

    def resizeEvent(self, event):
        """
        窗口尺寸变化时，重置偏移并刷新图片。
        Reset offset and update image on resize.
        """
        self._offset = QPoint(0, 0)
        self.update_image()
        super().resizeEvent(event)

    def wheelEvent(self, event):
        """
        鼠标滚轮缩放图片。
        Zoom image with mouse wheel.
        """
        if self._pixmap is None or self._pixmap.isNull():
            return
        angle = event.angleDelta().y()
        if angle > 0:
            self._scale *= 1.1
        else:
            self._scale /= 1.1
        self._scale = max(0.1, min(self._scale, 10))
        self._offset = QPoint(0, 0)  # 缩放时重置偏移，始终居中
        self.update_image()

    def mousePressEvent(self, event):
        """
        鼠标按下时准备拖拽。
        Prepare for dragging on mouse press.
        """
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._last_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        拖拽图片。
        Drag image on mouse move.
        """
        if self._dragging and self._pixmap and not self._pixmap.isNull():
            delta = event.pos() - self._last_pos
            self._offset += delta
            self._last_pos = event.pos()
            self.update_image()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放时结束拖拽。
        End dragging on mouse release.
        """
        if event.button() == Qt.LeftButton:
            self._dragging = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def update_image(self):
        """
        根据当前缩放和偏移刷新图片显示。
        Update image display according to scale and offset.
        """
        if self._pixmap and not self._pixmap.isNull():
            w = int(self._pixmap.width() * self._scale)
            h = int(self._pixmap.height() * self._scale)
            scaled_pixmap = self._pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            result = QPixmap(self.size())
            result.fill(Qt.transparent)
            painter = QPainter(result)
            x = (self.width() - scaled_pixmap.width()) // 2 + self._offset.x()
            y = (self.height() - scaled_pixmap.height()) // 2 + self._offset.y()
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.end()
            super().setPixmap(result)
        else:
            super().setPixmap(QPixmap())

class HydraulicCraneDialog(QDialog):
    """
    液压汽车起重机吊装计算主对话框。
    Main dialog for hydraulic truck crane lifting calculation.

    功能：
        - 输入基本参数（吊重、动力系数、推荐/自定义模式）
        - 通过子对话框设置吊装要求、起重机选型、相关参数
        - 显示工况图与支腿力计算简图
        - 数据变更与保存状态管理
    子对话框：
        - CraneRequirementsDialog: 采集吊装要求参数
        - CraneSelectionDialog: 采集起重机选型参数
        - CraneParametersDialog: 采集起重机相关计算参数
    """
    def __init__(self, uuid=None, data=None):
        """
        初始化主对话框。
        Args:
            uuid: 对话框唯一标识（可选）。
            data: 初始数据对象（HydraulicCraneData，可选）。
        """
        super().__init__()
        self.m_name = "液压汽车起重机吊装计算对话框"  # 对话框名称
        self.uuid = uuid  # 对话框唯一标识
        self.data = data if data else HydraulicCraneData()  # 计算数据对象
        if uuid:
            self.data.uuid = uuid
        self.IsSave = True  # 保存状态标志，True表示已保存，False表示有更改未保存
        self.verification_project = VerificationProject("液压汽车起重机吊装计算")  # 校核项目对象
        self.setMinimumSize(800, 600)
        self.setMaximumSize(1920, 1080)
        self.init_ui()  # 初始化界面

    def init_ui(self):
        """
        初始化用户界面，包括主布局、参数区、图片区及子对话框。
        Initialize UI: main layout, parameter area, image area, and subdialogs.
        """
        # 设置窗口标题和初始大小，适配主窗口宽度
        self.setWindowTitle("液压汽车起重机吊装计算")
        self.setGeometry(100, 100, 1500, 800)  # 与主窗口宽度一致

        # ===================== 主体布局结构 =====================
        # 创建主Splitter，实现左右分栏布局
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setStyleSheet("""
        QSplitter::handle {
            background: #888;
            width: 6px;
            border-radius: 3px;
        }
        """)
        # 设置TabWidget分界线样式
        tab_bar_style = """
        QTabWidget::tab-bar {
            qproperty-expanding: 1;
        }
        QTabBar::tab {
            border-right: 2px solid #a0a0a0;
            padding: 4px 12px 4px 12px;
            font-family: 'SimHei', '黑体', 'Microsoft YaHei', Arial, sans-serif;
            font-weight: bold;
            font-size: 10pt;
            min-width: 0;
        }
        QTabBar::tab:last {
            border-right: none;
        }
        """

        # ========== 左侧参数区 ========== #
        left_widget = QWidget()  # 左侧主容器
        left_layout = QVBoxLayout(left_widget)  # 左侧垂直布局
        left_layout.setContentsMargins(0, 0, 0, 0)
        # 1. 基本参数组
        basic_group = QGroupBox("基本参数")  # 基本参数分组框
        basic_layout = QGridLayout()  # 网格布局
        basic_layout.setContentsMargins(0, 0, 0, 0)
        # 吊重输入
        basic_layout.addWidget(QLabel("吊重Gw(吨):"), 0, 0)
        self.crane_weight_edit = QLineEdit(str(self.data.crane_weight))  # 吊重输入框
        self.crane_weight_edit.textChanged.connect(self.on_data_changed)  # 数据变更信号
        basic_layout.addWidget(self.crane_weight_edit, 0, 1)
        # 起重动力系数输入
        basic_layout.addWidget(QLabel("起重动力系数k1:"), 1, 0)
        self.power_factor_edit = QLineEdit(str(self.data.power_factor))  # 动力系数输入框
        self.power_factor_edit.textChanged.connect(self.on_data_changed)
        basic_layout.addWidget(self.power_factor_edit, 1, 1)
        # 单选按钮组（智能推荐/自定义）
        radio_group = QButtonGroup(self)
        self.smart_radio = QRadioButton("智能推荐起重机")  # 智能推荐模式
        self.custom_radio = QRadioButton("自定义起重机")  # 自定义模式
        radio_group.addButton(self.smart_radio)
        radio_group.addButton(self.custom_radio)
        self.smart_radio.setChecked(self.data.is_smart_recommendation)
        self.custom_radio.setChecked(not self.data.is_smart_recommendation)
        self.smart_radio.setToolTip('注：选择"智能推荐起重机"，点击下方"推荐"按钮，可对起吊高度、"起重能力"、"吊物安全距离"进行推荐择优！')
        basic_layout.addWidget(self.smart_radio, 2, 0)
        basic_layout.addWidget(self.custom_radio, 2, 1)
        basic_group.setLayout(basic_layout)
        # 2. 创建标签页组件（吊装要求、起重机选型、相关参数）
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(tab_bar_style)
        # 创建三个子对话框
        self.requirements_dialog = CraneRequirementsDialog(self)  # 吊装要求子对话框
        self.selection_dialog = CraneSelectionDialog(self)        # 起重机选型子对话框
        self.parameters_dialog = CraneParametersDialog(self)      # 相关参数子对话框
        # 添加标签页
        tab_widget.addTab(self.requirements_dialog, "吊装要求")
        tab_widget.addTab(self.selection_dialog, "起重机选型")
        tab_widget.addTab(self.parameters_dialog, "起重机相关计算参数")
        # 连接子对话框的数据改变信号
        self.requirements_dialog.data_changed.connect(self.on_data_changed)
        self.selection_dialog.data_changed.connect(self.on_data_changed)
        self.parameters_dialog.data_changed.connect(self.on_data_changed)
        left_layout.addWidget(basic_group)
        left_layout.addWidget(tab_widget)
        left_layout.addStretch(1)  # 控件靠上
        left_widget.setMinimumWidth(200)  # 左侧最小宽度，允许拖动
        main_splitter.addWidget(left_widget)  # 左侧加入主分割器

        # ========== 右侧图片视图区 ========== #
        right_widget = QWidget()  # 右侧主容器
        right_layout = QVBoxLayout(right_widget)  # 右侧垂直布局
        right_layout.setContentsMargins(0, 0, 0, 0)
        # 添加顶部Tab用于切换图片
        self.image_tab = QTabWidget()
        self.image_tab.addTab(QWidget(), "吊装工况图")
        self.image_tab.addTab(QWidget(), "支腿力计算简图")
        self.image_tab.setFixedHeight(30)  # 只显示tab按钮，不显示内容
        self.image_tab.currentChanged.connect(self.on_image_tab_changed)
        right_layout.addWidget(self.image_tab)  # Tab按钮放在右侧顶部
        self.image_label = ImageLabel()  # 图片显示控件
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFrameShape(QFrame.Box)
        # self.image_label.setMinimumSize(200, 200)  # 可选：设置图片最小尺寸
        # 默认显示吊装工况图
        self.show_image_by_tab(0)
        right_layout.addWidget(self.image_label)
        right_widget.setContentsMargins(0, 0, 0, 0)
        right_widget.setMinimumWidth(200)  # 右侧最小宽度
        main_splitter.addWidget(right_widget)  # 右侧加入主分割器

        # ========== 分割器比例与主布局 ========== #
        main_splitter.setStretchFactor(0, 0)  # 左侧不拉伸
        main_splitter.setStretchFactor(1, 1)  # 右侧可拉伸
        main_splitter.setSizes([400, 1100])  # 初始左400，右1100，允许拖动

        # ========== 总体主布局 ========== #
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)  # 应用主布局
        # self.showMaximized()  # 移除自动最大化，避免界面异常放大

    def on_data_changed(self):
        """
        数据变更时的处理函数，标记为未保存。
        Mark as unsaved when data changes.
        """
        self.IsSave = False
        
    def updateCalculationData(self):
        """
        更新并收集所有界面数据到self.data。
        Update and collect all UI data into self.data.
        Returns:
            HydraulicCraneData: 更新后的数据对象。
            None: 如果数据转换出错。
        """
        try:
            # 更新基本参数
            self.data.crane_weight = float(self.crane_weight_edit.text())  # 吊重
            self.data.power_factor = float(self.power_factor_edit.text())  # 动力系数
            self.data.is_smart_recommendation = self.smart_radio.isChecked()  # 推荐/自定义
            
            # 获取子对话框数据
            requirements_data = self.requirements_dialog.get_data()  # 吊装要求
            selection_data = self.selection_dialog.get_data()        # 选型
            parameters_data = self.parameters_dialog.get_data()      # 相关参数
            
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
        """
        获取对话框的UUID。
        Get the UUID of the dialog.
        Returns:
            str: UUID字符串。
        """
        return self.uuid

    def on_image_tab_changed(self, index):
        """
        图片Tab切换时的处理函数。
        Handle image tab change event.
        Args:
            index: 当前选中的Tab索引。
        """
        self.show_image_by_tab(index)

    def show_image_by_tab(self, index):
        """
        根据Tab索引显示对应图片。
        Show image according to tab index.
        Args:
            index: Tab索引（0-工况图，1-支腿力简图）。
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if index == 0:
            image_path = os.path.join(current_dir, "..", "DrawGraphinsScene", "TruckCrane.png")
        else:
            image_path = os.path.join(current_dir, "..", "DrawGraphinsScene", "OutForceCalDiagram.png")
        if os.path.exists(image_path):
            self.image_label._offset = QPoint(0, 0)  # 切换图片时重置偏移
            self.image_label.setPixmap(QPixmap(image_path))
        else:
            self.image_label.setText("未找到图片")
