import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar
#状态栏
class StatusBar(QStatusBar):
    def __init__(self, parent=None):
        self.m_name="状态栏"
        super().__init__(parent)
        self.showMessage('状态栏')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    status_bar = StatusBar(mainWindow)
    mainWindow.setStatusBar(status_bar)
    mainWindow.show()
    sys.exit(app.exec_())
