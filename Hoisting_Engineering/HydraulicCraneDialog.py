#液压汽车起重机吊装计算界面
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QRadioButton, QButtonGroup, QGroupBox, QComboBox, QGridLayout, QFormLayout, QSplitter, QWidget, QMessageBox, QFrame, QTabWidget, QSizePolicy
)
import sys
import os
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import uuid
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self._base_size = None
        self._scale = 1.0

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        self._base_size = None
        self._scale = 1.0
        self.update_image()

    def resizeEvent(self, event):
        if self._pixmap and not self._pixmap.isNull():
            self._base_size = self.size()
            self._scale = 1.0
            self.update_image()
        super().resizeEvent(event)

    def wheelEvent(self, event):
        if self._pixmap is None or self._pixmap.isNull():
            return
        angle = event.angleDelta().y()
        if angle > 0:
            self._scale *= 1.1
        else:
            self._scale /= 1.1
        self.update_image()

    def update_image(self):
        if self._pixmap and not self._pixmap.isNull():
            if self._base_size is None:
                self._base_size = self.size()
            w = int(self._base_size.width() * self._scale)
            h = int(self._base_size.height() * self._scale)
            super().setPixmap(self._pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))

class HydraulicCraneDialog(QDialog):
    def __init__(self, uuid=None, data=None):
        super().__init__()
        self.m_name = "液压汽车起重机吊装计算对话框"

        self.uuid = uuid
        self.data = data if data else HydraulicCraneData()
        if uuid:
            self.data.uuid = uuid
        
        self.IsSave = True  # 保存状态标志
        # Add verification project initialization
        self.verification_project = VerificationProject("液压汽车起重机吊装计算")#后续支持修改项目树节点的名称，目前还没有用到

        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题和初始大小（放大一倍，便于显示更多内容）
        self.setWindowTitle("液压汽车起重机吊装计算")
        self.setGeometry(100, 100, 3000, 1400)  # 设置对话框的初始大小（放大一倍）

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
        self.smart_radio = QRadioButton("智能推荐起重机")
        self.custom_radio = QRadioButton("自定义起重机")
        radio_group.addButton(self.smart_radio)
        radio_group.addButton(self.custom_radio)
        self.smart_radio.setChecked(self.data.is_smart_recommendation)
        self.custom_radio.setChecked(not self.data.is_smart_recommendation)
        basic_layout.addWidget(self.smart_radio, 2, 0)
        basic_layout.addWidget(self.custom_radio, 2, 1)
        basic_group.setLayout(basic_layout)
        # 2. 创建标签页组件（吊装要求、起重机选型、相关参数）
        tab_widget = QTabWidget()
        # 创建三个子对话框
        self.requirements_dialog = CraneRequirementsDialog(self)  # 吊装要求
        self.selection_dialog = CraneSelectionDialog(self)        # 起重机选型
        self.parameters_dialog = CraneParametersDialog(self)      # 相关参数
        # 添加标签页
        tab_widget.addTab(self.requirements_dialog, "吊装要求")
        tab_widget.addTab(self.selection_dialog, "起重机选型")
        tab_widget.addTab(self.parameters_dialog, "起重机相关计算参数")
        # 连接子对话框的数据改变信号
        self.requirements_dialog.data_changed.connect(self.on_data_changed)
        self.selection_dialog.data_changed.connect(self.on_data_changed)
        self.parameters_dialog.data_changed.connect(self.on_data_changed)
        # 控件不拉伸，靠上排列
        basic_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        tab_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        left_layout.addWidget(basic_group)
        left_layout.addWidget(tab_widget)
        left_layout.addStretch(1)  # 控件靠上
        left_widget.setContentsMargins(0, 0, 0, 0)
        left_widget.setMinimumWidth(30)  # 保证不会完全不可见
        main_splitter.addWidget(left_widget)  # 左侧加入主分割器

        # ========== 右侧图片视图区 ========== #
        right_widget = QWidget()  # 右侧主容器
        right_layout = QVBoxLayout(right_widget)  # 右侧垂直布局
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.image_label = ImageLabel()  # 图片显示控件
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFrameShape(QFrame.Box)
        # self.image_label.setMinimumSize(800, 800)  # 注释掉或改为较小值
        # 加载起重机示意图
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_image_path = os.path.join(current_dir, "..", "DrawGraphinsScene", "TruckCrane.png")
        if os.path.exists(default_image_path):
            pixmap = QPixmap(default_image_path)
            self.image_label.setPixmap(pixmap)
        else:
            self.image_label.setText("未找到图片")
        right_layout.addWidget(self.image_label)
        right_widget.setContentsMargins(0, 0, 0, 0)
        right_widget.setMinimumWidth(30)  # 保证不会完全不可见
        main_splitter.addWidget(right_widget)  # 右侧加入主分割器

        # ========== 分割器比例与主布局 ========== #
        main_splitter.setStretchFactor(0, 0)  # 左侧不拉伸
        main_splitter.setStretchFactor(1, 1)  # 右侧可拉伸
        main_splitter.setSizes([4, 6])  # 按比例分配宽度，右侧更宽

        # ========== 总体主布局 ========== #
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)  # 应用主布局
        # self.showMaximized()  # 移除自动最大化，避免界面异常放大

    def on_data_changed(self):
        """当数据改变时的处理函数"""
        self.IsSave = False
        
    def updateCalculationData(self):
        """更新计算数据"""
        try:
            # 更新基本参数
            self.data.crane_weight = float(self.crane_weight_edit.text())
            self.data.power_factor = float(self.power_factor_edit.text())
            self.data.is_smart_recommendation = self.smart_radio.isChecked()
            
            # 获取子对话框数据
            requirements_data = self.requirements_dialog.get_data()
            selection_data = self.selection_dialog.get_data()
            parameters_data = self.parameters_dialog.get_data()
            
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
        """获取对话框的UUID"""
        return self.uuid

# 移除或注释掉以下内容，防止自动启动界面
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     crane_dialog = HydraulicCraneDialog()
#     crane_dialog.show()
#     sys.exit(app.exec_()) 