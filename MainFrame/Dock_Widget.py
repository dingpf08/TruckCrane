from PyQt5.QtWidgets import QDockWidget, QListWidget, QListWidgetItem, QApplication, QMainWindow
from PyQt5.QtCore import Qt
#父窗口为MainFrame.py中的class MainWindow(QMainWindow):
class CalculateDockWidget(QDockWidget):
    def __init__(self, title, parent=None):
        super(CalculateDockWidget, self).__init__(title, parent)
        self.m_dialog_data_map = {}  # 新增：存储每个对话框的数据，键为对话框的UUID，值为字典类型的数据，关闭标签且选择，
        # 这个数据在反序列化的时候，会给到CalculateDockWidget的self.m_dialog_data_map = {}  # 新增：存储每个对话框的数据，键为对话框的UUID，值为字典类型的数据，关闭标签且选择
        self.init_ui()

    def init_ui(self):
        self.dock_widget_contents = QListWidget()
        self.setWidget(self.dock_widget_contents)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
        # 连接双击信号到槽函数
        self.dock_widget_contents.itemDoubleClicked.connect(self.on_item_double_clicked)

    def on_item_double_clicked(self, item):
        # 获取关联的UUID
        struuid = item.data(Qt.UserRole)
        mainframe=self.parent()#获取父窗口
        if mainframe:
            Table_bar=mainframe.m_ECST#获取Table_Bar
            dialog=Table_bar.get_dialog_by_uuid(struuid)#根据uuid获取对话框
            dialogname=None
            if dialog:
                dialogname=dialog.m_name
                print(f"双击的对话框名字为：{dialogname}")
            if dialogname:
                index = Table_bar.AddNewLable(dialogname, dialog, struuid)  # 给上面添加标签页

        # 双击的时候如果已经附件了对话框 就不要重复添加了

        #通过标签页对话框获取uuid对应的对话框 然后将对话框附加到标签页 self.m_dialog_uuid_map = {}  # 存储对话框的uuid和对应的对话框实例的字典


    #给根目录下添加节点
    def add_item_by_name(self, item_name,struuid):
        item = QListWidgetItem(item_name)
        # 关联UUID到列表项，使用Qt.UserRole来存储自定义数据
        item.setData(Qt.UserRole, struuid)
        self.dock_widget_contents.addItem(item)

    def refresh_project_tree(self):
        """使用self.m_dialog_data_map中的数据刷新项目树。"""
        self.dock_widget_contents.clear()  # 首先清空当前的项目树列表

        for struuid, dialog_data in self.m_dialog_data_map.items():
            # 假设dialog_data字典中有一个"name"键，我们用它来作为项目树中显示的名称
            item_name =dialog_data.caltypename
            self.add_item_by_name(item_name, struuid)
def main():
    import sys
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    calculate_dock_widget = CalculateDockWidget("测试悬浮", main_window)
    main_window.addDockWidget(Qt.LeftDockWidgetArea, calculate_dock_widget)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()