import os
import sys
##
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QDialog, QTreeWidget, QTreeWidgetItem, QVBoxLayout
#主对话框，组织所有其它控件和对话框
from Dock_Widget import CalculateDockWidget
from Menu_Bar  import ECSMenuBar
from Tool_Bar import ToolBar
from Table_Bar import ECSTabWidget
from Status_Bar import StatusBar
from Hoisting_Engineering.HydraulicCraneDialog import HydraulicCraneDialog  # 导入HydraulicCraneDialog
#这个变量self.m_dialog_data_map = {}在self.m_ECST标签页，self.m_CalDock项目树，self.m_toolbar工具栏都是同一个变量，在从工具栏打开文件的时候，其它位置的数据同步更新
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.m_dialog_data_map = {}  # 新增：存储每个对话框的数据，键为对话框的UUID，值为字典类型的数据，关闭标签且选择，
        # 这个数据在Tool_Bar.py中反序列化的时候，会给到MainFrame.py的self.m_dialog_data_map = {}  # 新增：存储每个对话框的数据，键为对话框的UUID，值为字典类型的数据，关闭标签且选择
        self.initUI()
        print(f"MainWindow中地址为：{self}")
#测试案例
    def initUI(self):
        self.setWindowTitle('施工计算软件')
        self.setGeometry(100, 100, 800, 600)
        self.m_CalDock=CalculateDockWidget("工程树图")
        self.m_menu=ECSMenuBar(self)# 1、水平顶部设置菜单栏
        self.m_toolbar=ToolBar(self) # 2、水平中间添加工具栏
        self.m_statusbar=StatusBar(self)# 3、底部设置状态栏
        self.m_ECST=ECSTabWidget(self)# 4、设置中心标签页
        # 应用全局样式表
        self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0; /* 浅灰色背景 */
                }
                QMenuBar {
                    background-color: #e0e0e0;
                    color: #333333;
                }
                QMenuBar::item:selected {
                    background-color: #d0e4f7; /* 选中菜单时的颜色 */
                }
                QToolBar {
                    background-color: #e0e0e0;
                    spacing: 3px; /* 工具栏项目间距 */
                }
                QPushButton {
                    background-color: #d0e4f7;
                    border: none;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #c0d4e7;
                }
                QLabel, QDockWidget {
                    color: #333333;
                }
                QStatusBar {
                    background-color: #e0e0e0;
                    color: #333333;
                }
                QTabWidget::pane {
                    border: 1px solid #a0a0a0; /* 标签页边框 */
                }
                QTabBar::tab {
                    background: #f0f0f0;
                    padding: 5px;
                }
                QTabBar::tab:selected {
                    background: #d0e4f7;
                    margin-bottom: -1px;
                }
            """)
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

    def SaveBeforeClose(self):
        reply = QMessageBox.question(self, '请选择下一步操作', '是否保存当前工程？',
                                     QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.No)


        if reply == QMessageBox.Yes:
            default_file_name = "Pro.ZtzpCCS"
            # 获取当前用户的桌面路径
            # 构建当前用户桌面的路径
            initial_directory = desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            default_save_path =None

            #
            if initial_directory is not None and default_file_name is not None:
                default_save_path = os.path.join(initial_directory, default_file_name)
            else:
                print("错误：initial_directory 或 default_file_name 之一为 None。")
            # 用户选择了保存数据，弹出文件保存对话框让用户选择保存位置
            file_name, _ = QFileDialog.getSaveFileName(
                self, "保存文件", default_save_path, "ZtzpCCS Files (*.ZtzpCCS)")
            if file_name:
                if not file_name.endswith('.ZtzpCCS'):  # 序列化的文件后缀为ZtzpCCS
                    file_name += '.ZtzpCCS'
                self.m_ECST.serialize_dialog_data_map(file_name)
            return True  # 返回 True 表示允许退出

        elif reply == QMessageBox.No:
            return True  # 返回 True 表示允许退出

        elif reply == QMessageBox.Cancel:
            return False  # 返回 False 表示取消退出

        # 默认情况下,不退出
        return False
    def closeEvent(self, event):
        if self.SaveBeforeClose():
            event.accept()  # 允许退出
        else:
            event.ignore()  # 取消退出

class Hoisting_CalculateTreeDialog(QDialog):
    def __init__(self, mainWindow=None):
        super().__init__(mainWindow, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.m_MainWindow = mainWindow
        self.initUI()

    def initUI(self):
        self.setWindowTitle("起重吊装计算合集")
        layout = QVBoxLayout(self)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.root_item = QTreeWidgetItem(self.tree_widget)
        self.root_item.setText(0, "起重吊装")

        self.child_item1 = QTreeWidgetItem(self.root_item)
        self.child_item1.setText(0, "液压汽车起重机吊装计算")

        self.child_item2 = QTreeWidgetItem(self.root_item)
        self.child_item2.setText(0, "履带式起重机吊装计算")

        self.tree_widget.expandAll()
        self.tree_widget.itemDoubleClicked.connect(self.onItemDoubleClicked)

        layout.addWidget(self.tree_widget)
        self.setLayout(layout)

    def onItemDoubleClicked(self, item, column):
        itemtext = item.text(0)
        if itemtext == "液压汽车起重机吊装计算":
            print("双击：液压汽车起重机吊装计算")
            self.hide()
            parent = self.parent()
            if parent:
                dialog = HydraulicCraneDialog(parent)
                uuid = dialog.winId()  # 使用窗口ID作为唯一标识
                index = parent.AddNewLable(itemtext, dialog, str(uuid))
                print(f"标签页的id为：{index}")
                # parent.setCurrentIndex(index)  # 显示当前的标签页

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
