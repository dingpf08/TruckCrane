import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
#主对话框，组织所有其它控件和对话框
from Dock_Widget import CalculateDockWidget
from Menu_Bar  import ECSMenuBar
from Tool_Bar import ToolBar
from Table_Bar import ECSTabWidget
from Status_Bar import StatusBar

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        print(f"MainWindow中地址为：{self}")

    def initUI(self):
        self.setWindowTitle('施工计算软件')
        self.setGeometry(100, 100, 800, 600)
        self.m_menu=ECSMenuBar(self)# 顶部设置菜单栏
        self.m_toolbar=ToolBar(self) # 中间添加工具栏
        self.m_statusbar=StatusBar(self)# 底部设置状态栏
        self.m_ECST=ECSTabWidget(self)# 设置中心标签页
        self.m_CalDock=CalculateDockWidget('工程树图', self)
        # 顶部设置菜单栏
        self.setMenuBar(self.m_menu)
        # 中间添加工具栏
        self.addToolBar(self.m_toolbar)
        # 底部设置状态栏
        self.setStatusBar(self.m_statusbar)
        # 设置中心标签页
        self.setCentralWidget(self.m_ECST)
        # 左侧添加浮动窗口
        self.addDockWidget(Qt.LeftDockWidgetArea, self.m_CalDock)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
