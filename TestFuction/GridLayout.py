import sys
from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize


class CustomDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Custom Dialog')
        self.setGeometry(100, 100, 600, 200)  # 设置对话框大小

        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)  # 设置网格内控件之间的间距为0

        # 按钮图标和名称
        buttons_info = [
            ('icon1.png', '基坑工程计算'),
            ('icon2.png', '脚手架工程计算'),
            ('icon3.png', '钢结构工程计算'),
            ('icon4.png', '混凝土工程计算'),
            ('icon5.png', '平法施工计算'),
        ]

        # 创建按钮并添加到布局中
        for i, (icon_path, label_text) in enumerate(buttons_info):
            button = QPushButton()
            pixmap = QPixmap(icon_path)
            button.setIcon(QIcon(pixmap))
            button.setIconSize(QSize(64, 64))  # 设置图标大小
            button.setFixedSize(100, 100)  # 设置按钮大小
            grid_layout.addWidget(button, 0, i)  # 添加按钮到第一行

            label = QLabel(label_text)
            grid_layout.addWidget(label, 1, i)  # 添加标签到第二行

        self.setLayout(grid_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = CustomDialog()
    dialog.show()
    sys.exit(app.exec_())
