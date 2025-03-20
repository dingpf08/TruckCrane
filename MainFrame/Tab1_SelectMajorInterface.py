#模块选择对话框
import os
import sys
import uuid

from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QPushButton, QLabel, QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap, QBrush
from PyQt5.QtCore import QSize, Qt
#自定义对话框
from Tab2_Foundation import Foundation_CalculateTreeDialog as FounCal
from Tab6_Hoisting import Hoisting_CalculateTreeDialog as HoistCal
#首页："模块选择"对应的标签页对话框，对话框的背景为一张纯色的图片
class EngineerFuctionSelPage(QDialog):
    def __init__(self,parent=None):
        super(EngineerFuctionSelPage, self).__init__(parent)
        self.uuid = uuid.uuid4()  # 生成一个唯一的UUID
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('模块选择')
        self.setGeometry(100, 100, 600, 200)  # 设置对话框大小

        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)  # 设置网格内控件之间的间距为0
        # 设置背景图片：#目录修改#
        # 加载图片
        pixmap = QPixmap("Pic/background.png")#
        # 创建背景画刷
        brush = QBrush(pixmap)
        # 设置背景
        self.setStyleSheet("background-image: url(Pic/background.png);")#背景图片
        # 按钮图标和名称
        buttons_info = [
            ('EngnieeringDialog\icon1.png', '基坑工程'),
            ('EngnieeringDialog\icon2.png', '脚手架工程'),
            ('EngnieeringDialog\icon3.png', '钢结构工程'),
            ('EngnieeringDialog\icon4.png', '混凝土工程'),
            ('EngnieeringDialog\icon5.png', '平法施工'),
            ('EngnieeringDialog\icon6.png', '起重吊装'),
        ]
        # 创建按钮并添加到布局中
        for i, (icon_path, label_text) in enumerate(buttons_info):
            # Create the container for the button and the label
            container = QWidget()
            container_layout = QVBoxLayout(container)
            # Create and setup the button
            button = QPushButton()
            button.setText(label_text)#给按钮设置名字
            pixmap = QPixmap(icon_path)
            button.setIcon(QIcon(pixmap))
            button.setIconSize(QSize(100, 100))
            button.setFixedSize(100, 100)
            button.setStyleSheet("text-align: left;")  # 设置按钮的样式，让图片在文字上面
            # Connect the button's clicked signal to the on_button_clicked method
            print(f"第{i}个按钮的名称为{button.text()}")
            button.clicked.connect(lambda checked, button=button: self.on_button_clicked(button))#不理解
            # Add the button to the container layout
            container_layout.addWidget(button)
            # Create and setup the label
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignCenter)
            # Inside the loop
            label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            # Add the label to the container layout
            container_layout.addWidget(label)
            container_layout.setSpacing(5)
            # Set a fixed size for the container to avoid resizing
            container.setFixedSize(100, 150)
            # Add the container to the grid layout
            grid_layout.addWidget(container, 0, i)

        self.setLayout(grid_layout)

        parent = self.parent()
        if parent is not None:
            print("Tab1_SelectMajorInterfacede 父对话框的名称为：", parent.windowTitle())
        else:
            print("没有找到父对话框")
        #初始化各种选择对话框
        self.m_Fcalsel = FounCal(parent)  # 基坑工程选择对话框的父类为标签页，标签页的父类为主对话框
        self.m_Hcalsel = HoistCal(parent)  # 起重吊装选择对话框
    #选择页面没有参数
    def updateCalculationData(self):
        return None

    def on_button_clicked(self,button):
        #获取按钮的文本
        print("Tab_SelectMajorInterface:点击的按钮文本是：", button.text())
        text=button.text()
        if text=="基坑工程":
            self.m_Fcalsel.exec_()
            print("基坑工程")

        elif text=="脚手架工程":
            print("脚手架工程")
        elif text == "钢结构工程":
            print("钢结构工程")
        elif text == "混凝土工程":
            print("混凝土工程")
        elif text == "平法施工":
            print("平法施工")
        elif text == "起重吊装":
            self.m_Hcalsel.exec_()
            print("起重吊装")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = EngineerFuctionSelPage()
    dialog.show()
    sys.exit(app.exec_())
