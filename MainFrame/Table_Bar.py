from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel, QTextEdit, QListWidget, QMenu, QApplication
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QMouseEvent
#父窗口是class MainWindow(QMainWindow)
from Tab1_SelectMajorInterface import  EngineerFuctionSelPage as EFSP
#标签页，管理各种对话框
#这里还会存储新建的计算工程对话框实例和对应的uuid，和左侧项目树共用同一个uuid
class ECSTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(ECSTabWidget, self).__init__(parent)
        self.m_Name="标签页管理对话框"
        self.m_dialog_uuid_map = {}  # 存储对话框的uuid和对应的对话框实例,都放到内存里面
        self.init_ui()

    def get_dialog_by_uuid(self, uuid):
        """
        根据提供的UUID，从字典中找到并返回对应的对话框实例。
        如果找不到，返回None。
        """
        dialog = self.m_dialog_uuid_map.get(uuid)
        if dialog:
            return dialog
        else:
            print(f"找不到UUID为 {uuid} 的对话框。")
            return None
    #region 初始化函数
    def init_ui(self):
        # 标签1
        self.AddNewLable("模块选择", EFSP(self))#添加第一个标签页
        #self.setStyleSheet("background-color: lightblue;")#标签页的背景颜色
    # endregion 初始化函数

    #region 鼠标按下操作
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:#鼠标右键
            index = self.tabBar().tabAt(event.pos())
            if index >= 0:
                self.showContextMenu(event.globalPos(), index)
        super(ECSTabWidget, self).mousePressEvent(event)
    # endregion 鼠标按下操作

    # region 弹出右键菜单
    def showContextMenu(self, position, index):
        menu = QMenu()
        close_action = menu.addAction("关闭")
        close_otheraction=menu.addAction("关闭其它")

        if index==0:#模块选择,不能关闭模块选择
            close_action.setEnabled(False)

        action = menu.exec_(position)

        if action == close_action:
            self.removeTab(index)
        elif action==close_otheraction:
            self.remove_other_tabs()
    #endregion 弹出右键菜单

    # region 添加新的标签页
        #strName为标签的名字，dialog为QWidget对话框
    def AddNewLable(self,strName,dialog,struuid=None):#默认添加的是QWidget
        if isinstance(dialog, QWidget):
            tab = QWidget()#定义一个标签
            tab_layout = QVBoxLayout()#定义一个竖直的布局
            tab_label = dialog#定义附件的控件或者对话框的类型
            tab_layout.addWidget(tab_label)#竖向布局添加对应的对话框
            tab.setLayout(tab_layout)#变迁添加对应的布局
            index=self.addTab(tab, strName)#将标签添加到
            self.m_dialog_uuid_map[struuid]=dialog#存储uuid和对应的对话框实例
            if index:
                return index
    # endregion 添加新的标签页

    # region 根据索引移除标签页
    #移除特定标签页，根据索引来移除，index是要移除的标签的索引。标签页的索引从开始计数。
    def removeTabByIndex(self, index):
        self.removeTab(index)
    # endregion

    def remove_other_tabs(self):
        count = self.count()
        for i in range(count - 1, -1, -1):
            if i != 0:
                self.removeTab(i)
    #region 根据名字移除标签页
    def removeTabByName(self, tabName):
        for index in range(self.count()):
            if self.tabText(index) == tabName:
                self.removeTab(index)
                break
    # endregion

def main():
    import sys
    app = QApplication(sys.argv)
    mainWindow = ECSTabWidget()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()