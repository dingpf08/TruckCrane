import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction
#工具栏
class ToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        add_action = QAction('添加', self)
        delete_action = QAction('删除', self)
        edit_action = QAction('编辑', self)

        self.addAction(add_action)
        self.addAction(delete_action)
        self.addAction(edit_action)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    tool_bar = ToolBar(mainWindow)
    mainWindow.addToolBar(tool_bar)
    mainWindow.show()
    sys.exit(app.exec_())
