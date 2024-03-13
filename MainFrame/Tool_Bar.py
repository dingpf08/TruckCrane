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
        new_action = QAction('新建', self)
        open_action = QAction('打开', self)
        close_action = QAction('退出', self)
        # 绑定事件
        open_action.triggered.connect(self.open_file)

        self.addAction(new_action)
        self.addAction(open_action)
        self.addAction(close_action)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    tool_bar = ToolBar(mainWindow)
    mainWindow.addToolBar(tool_bar)
    mainWindow.show()
    sys.exit(app.exec_())
