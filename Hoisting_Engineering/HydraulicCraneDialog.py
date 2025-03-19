from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QRadioButton, QGroupBox, QComboBox, QGridLayout
)
import sys

class HydraulicCraneDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("液压汽车起重机吊装计算")
        self.setGeometry(100, 100, 400, 300)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 吊重和起吊力系数
        weight_layout = QHBoxLayout()
        weight_label = QLabel("吊重GW (吨):")
        weight_input = QLineEdit()
        weight_input.setText("30")
        weight_layout.addWidget(weight_label)
        weight_layout.addWidget(weight_input)

        factor_label = QLabel("起吊力系数K:")
        factor_input = QLineEdit()
        factor_input.setText("1.2")
        weight_layout.addWidget(factor_label)
        weight_layout.addWidget(factor_input)

        layout.addLayout(weight_layout)

        # 起重机选择
        crane_group = QGroupBox("起重机选择")
        crane_layout = QHBoxLayout()
        smart_radio = QRadioButton("智能推荐起重机")
        custom_radio = QRadioButton("自定义起重机")
        crane_layout.addWidget(smart_radio)
        crane_layout.addWidget(custom_radio)
        crane_group.setLayout(crane_layout)

        layout.addWidget(crane_group)

        # 吊装要求
        requirements_group = QGroupBox("吊装要求")
        requirements_layout = QGridLayout()

        max_height_label = QLabel("吊物顶距地面最大吊装高度h1 (m):")
        max_height_input = QLineEdit()
        max_height_input.setText("10")
        requirements_layout.addWidget(max_height_label, 0, 0)
        requirements_layout.addWidget(max_height_input, 0, 1)

        min_distance_label = QLabel("吊物顶距起重臂端部的最小距离h2 (m):")
        min_distance_input = QLineEdit()
        min_distance_input.setText("3")
        requirements_layout.addWidget(min_distance_label, 1, 0)
        requirements_layout.addWidget(min_distance_input, 1, 1)

        method_label = QLabel("工作幅度确定方法:")
        method_combo = QComboBox()
        method_combo.addItems(["智能确定", "手动输入工作幅度"])
        requirements_layout.addWidget(method_label, 2, 0)
        requirements_layout.addWidget(method_combo, 2, 1)

        layout.addWidget(requirements_group)
        requirements_group.setLayout(requirements_layout)

        # 安全距离复核
        safety_group = QGroupBox("吊物与起重臂安全距离复核")
        safety_layout = QGridLayout()

        structure_label = QLabel("构件边缘与起重臂（起重臂中心线）中心的水平距离:")
        structure_input = QLineEdit()
        structure_input.setText("1")
        safety_layout.addWidget(structure_label, 0, 0)
        safety_layout.addWidget(structure_input, 0, 1)

        safety_group.setLayout(safety_layout)
        layout.addWidget(safety_group)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = HydraulicCraneDialog()
    dialog.show()
    sys.exit(app.exec_()) 