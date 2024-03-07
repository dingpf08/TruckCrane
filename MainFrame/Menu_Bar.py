import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QAction
#菜单对话框
class ECSMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # 设置菜单栏的样式，调整高度
        file_menu = self.addMenu('文件')
        edit_menu = self.addMenu('编辑')
        settings_menu = self.addMenu('设置')
        window_menu = self.addMenu('窗口')
        help_menu = self.addMenu('帮助')

        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.exit_application)
        file_menu.addAction(exit_action)

    def exit_application(self):
        sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    menu_bar = ECSMenuBar(mainWindow)
    mainWindow.setMenuBar(menu_bar)
    mainWindow.show()
    sys.exit(app.exec_())
