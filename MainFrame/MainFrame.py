import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog
#主对话框，组织所有其它控件和对话框
from Dock_Widget import CalculateDockWidget
from Menu_Bar  import ECSMenuBar
from Tool_Bar import ToolBar
from Table_Bar import ECSTabWidget
from Status_Bar import StatusBar
#这个变量self.m_dialog_data_map = {}在self.m_ECST标签页，self.m_CalDock项目树，self.m_toolbar工具栏都是同一个变量，在从工具栏打开文件的时候，其它位置的数据同步更新
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.m_dialog_data_map = {}  # 新增：存储每个对话框的数据，键为对话框的UUID，值为字典类型的数据，关闭标签且选择，
        # 这个数据在Tool_Bar.py中反序列化的时候，会给到MainFrame.py的self.m_dialog_data_map = {}  # 新增：存储每个对话框的数据，键为对话框的UUID，值为字典类型的数据，关闭标签且选择
        self.initUI()
        print(f"MainWindow中地址为：{self}")

    def initUI(self):
        self.setWindowTitle('施工计算软件')
        self.setGeometry(100, 100, 800, 600)
        self.m_CalDock = CalculateDockWidget('工程树图', self)#必须放在self.m_ECST的前面
        self.m_menu=ECSMenuBar(self)# 1、水平顶部设置菜单栏
        self.m_toolbar=ToolBar(self) # 2、水平中间添加工具栏
        self.m_statusbar=StatusBar(self)# 3、底部设置状态栏
        self.m_ECST=ECSTabWidget(self)# 4、设置中心标签页

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

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '请选择下一步操作', '是否保存当前工程？',
                                     QMessageBox.Yes | QMessageBox.No| QMessageBox.Cancel, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 用户选择了保存数据，弹出文件保存对话框让用户选择保存位置
            file_name, _ = QFileDialog.getSaveFileName(
                self, "保存文件", os.getenv('HOME'), "ZtzpCCS Files (*.ZtzpCCS)")
            if file_name:
                if not file_name.endswith('.ZtzpCCS'):#序列化的文件后缀为ZtzpCCS
                    file_name += '.ZtzpCCS'
                self.m_ECST.serialize_dialog_data_map(file_name)
            event.accept()#退出保存数据
        elif reply==QMessageBox.No:
            event.accept()#退出不保存
        elif reply==QMessageBox.Cancel:
            event.ignore()#不退出



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
