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
        print(f"点击了“菜单栏的退出”按钮")
        if isinstance(self.parent(), QMainWindow):
            # 如果父窗口是 MainWindow 实例,调用 SaveBeforClose 方法
            if self.parent().SaveBeforeClose():
                sys.exit()
            else:
                # SaveBeforeClose 返回 False,表示不应该退出程序
                # 在这里添加需要执行的代码,例如显示一个消息框
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "提示", "无法退出程序,请保存当前工作后重试。")
        else:
            # 如果父窗口不是 MainWindow 实例,直接退出应用程序
            sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    menu_bar = ECSMenuBar(mainWindow)
    mainWindow.setMenuBar(menu_bar)
    mainWindow.show()
    sys.exit(app.exec_())
