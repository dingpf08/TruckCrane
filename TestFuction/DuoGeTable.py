import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QTabWidget,
                             QGraphicsView, QGraphicsScene, QWidget)


class CustomGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        # 初始化一个 QGraphicsScene，您可以根据需要添加更多的图形项
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

    # 您可以在这个类中添加更多的方法来配置您的 QGraphicsView


class TabbedDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('多标签视图对话框')
        self.setGeometry(100, 100, 800, 600)

        # 创建 QTabWidget
        self.tabs = QTabWidget()

        # 创建标签页并添加自定义的 QGraphicsView
        self.tab1 = QWidget()
        self.view1 = CustomGraphicsView()  # 创建第一个视图
        self.tab1_layout = QVBoxLayout()
        self.tab1_layout.addWidget(self.view1)
        self.tab1.setLayout(self.tab1_layout)

        self.tab2 = QWidget()
        self.view2 = CustomGraphicsView()  # 创建第二个视图
        self.tab2_layout = QVBoxLayout()
        self.tab2_layout.addWidget(self.view2)
        self.tab2.setLayout(self.tab2_layout)

        self.tab3 = QWidget()
        self.view3 = CustomGraphicsView()  # 创建第三个视图
        self.tab3_layout = QVBoxLayout()
        self.tab3_layout.addWidget(self.view3)
        self.tab3.setLayout(self.tab3_layout)

        # 将标签页添加到 QTabWidget 中
        self.tabs.addTab(self.tab1, "视图1")
        self.tabs.addTab(self.tab2, "视图2")
        self.tabs.addTab(self.tab3, "视图3")

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)


# 下面是创建和运行应用程序的标准方法
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = TabbedDialog()
    mainWindow.show()
    sys.exit(app.exec_())
