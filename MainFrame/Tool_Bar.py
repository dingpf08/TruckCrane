import pickle
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QFileDialog, QMessageBox


#工具栏
class ToolBar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_dialog_data_map = {}  # 新增：存储每个对话框的数据，键为对话框的UUID，值为字典类型的数据，关闭标签且选择，
        # 这个数据在反序列化的时候，会给到Table_Bar的self.m_dialog_data_map = {}  # 新增：存储每个对话框的数据，键为对话框的UUID，值为字典类型的数据，关闭标签且选择
        self.initUI()

    def initUI(self):
        self.m_name = "工具栏"
        new_action = QAction('新建', self)
        open_action = QAction('打开', self)
        close_action = QAction('退出', self)
        crane_settings_action = QAction('起重机械设置', self)  # 新增起重机械设置按钮
        
        # 绑定事件
        open_action.triggered.connect(self.open_file)
        close_action.triggered.connect(self.exit_application)
        crane_settings_action.triggered.connect(self.show_crane_settings)  # 绑定新事件
        
        self.addAction(new_action)
        self.addAction(open_action)
        self.addAction(crane_settings_action)  # 添加新按钮
        self.addAction(close_action)

    def exit_application(self):
        print('点击了"工具栏的退出"按钮')
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
    def UpdateUiAndData(self,prodata):
        self.parent().m_dialog_data_map = prodata  # 主对话框的数据更新
        self.parent().m_ECST.UpdataDialogData(prodata)#标签页更新数据和对应的对话框
        self.parent().m_CalDock.m_dialog_data_map = prodata  # 项目树对话框的数据更新
        self.parent().m_CalDock.refresh_project_tree()

    #打开文件反序列化文件内容到内存
    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "打开文件", "", "ZtzpCCS Files (*.ZtzpCCS)")
        if file_name:
            try:
                with open(file_name, 'rb') as file:
                    self.m_dialog_data_map = pickle.load(file)
                QMessageBox.information(self, "成功", "文件加载成功")

                # 假设你可以通过主窗口访问到Tab_Bar的实例
                # 注意：你需要根据自己的代码结构来调整这里的代码
                self.UpdateUiAndData(self.m_dialog_data_map)#根据数据更新对话框界面和各个子控件的数据
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载文件失败: {e}")

    def show_crane_settings(self):
        """显示起重机械设置对话框"""
        try:
            from Dialogs.CraneSettingsDialog import CraneSettingsDialog
            dialog = CraneSettingsDialog(self)
            dialog.exec_()
        except Exception as e:
            print(f"Error in show_crane_settings: {e}")
            QMessageBox.critical(self, "错误", f"显示起重机械设置对话框时发生错误: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    tool_bar = ToolBar(mainWindow)
    mainWindow.addToolBar(tool_bar)
    mainWindow.show()
    sys.exit(app.exec_())
