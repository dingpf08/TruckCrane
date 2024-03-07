import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QRadioButton, QSplitter, QGraphicsView, QGraphicsScene, QMainWindow
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 创建一个水平分割器
        hsplitter = QSplitter(Qt.Horizontal, self)

        # 创建一个包含单选按钮的小部件
        leftWidget = QWidget()
        leftLayout = QVBoxLayout(leftWidget)
        radio1 = QRadioButton("选项 1")
        leftLayout.addWidget(radio1)

        # 创建一个绘图界面
        drawArea = QGraphicsView()
        drawArea.setScene(QGraphicsScene())

        # 将小部件和绘图区添加到分割器
        hsplitter.addWidget(leftWidget)
        hsplitter.addWidget(drawArea)

        # 设置分割器作为窗口中心部件
        self.setCentralWidget(hsplitter)

        # 设置窗口标题和大小
        self.setWindowTitle('可拖动的分割器示例')
        self.setGeometry(300, 300, 600, 400)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
