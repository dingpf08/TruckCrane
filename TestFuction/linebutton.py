import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 创建三个按钮
        btn1 = QPushButton('Button 1', self)
        btn2 = QPushButton('Button 2', self)
        btn3 = QPushButton('Button 3', self)

        # 创建水平布局并添加按钮
        hbox = QHBoxLayout()
        hbox.addWidget(btn1)
        hbox.addWidget(btn2)
        hbox.addWidget(btn3)

        # 设置窗口的主布局
        self.setLayout(hbox)

        self.setWindowTitle('Horizontal Buttons Example')
        self.setGeometry(300, 300, 300, 200)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
