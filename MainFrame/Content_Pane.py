import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton

class ContentPane(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        button = QPushButton('示例按钮', self)
        layout.addWidget(button)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    content_pane = ContentPane(mainWindow)
    mainWindow.setCentralWidget(content_pane)
    mainWindow.show()
    sys.exit(app.exec_())
