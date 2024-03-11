#基坑工程专业 对应的选择对话框
#父窗口是Table_Bar.py中的class ECSTabWidget(QTabWidget):
#class ECSTabWidget(QTabWidget):的父窗口为#MainFrame中的class MainWindow(QMainWindow):
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QTreeWidget, QTreeWidgetItem, QVBoxLayout
from Foundation_Engineering.EarthSlope import EarthSlopeDialog as ES    #边坡界面
from Dock_Widget import CalculateDockWidget as CD#左侧的项目树
#基坑工程计算选择对话框
class Foundation_CalculateTreeDialog(QDialog):
    def __init__(self,mainWindow=None):
        super().__init__(mainWindow, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)#最大最小关闭按钮
        self.m_MainWindow=mainWindow#传入主对话框
        print(f"Foundation传入的主对话为：{self.m_MainWindow}")
        if self.m_MainWindow is not None:
            print(f"Foundation传入的主对话为-----：{self.m_MainWindow.windowTitle()}")
        self.initUI()
    #初始化基坑工程的各种计算界面
    def InitChildDialog(self):
            self.es=ES()#边坡绘制区域
    def initUI(self):
        self.setWindowTitle("基坑工程计算合集")
        self.InitChildDialog()#初始化基坑计算的子对话框
        layout = QVBoxLayout(self)
        # Use QTreeWidget instead of QTreeView
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        # Create a root item for the tree widget
        self.root_item = QTreeWidgetItem(self.tree_widget)
        self.root_item.setText(0, "基坑工程")

        # Add a child item to the root item
        self.child_item = QTreeWidgetItem(self.root_item)
        self.child_item.setText(0, "土方边坡计算")



        # Expand all sections in the tree widget
        self.tree_widget.expandAll()
        self.tree_widget.itemDoubleClicked.connect(self.onItemDoubleClicked)

        layout.addWidget(self.tree_widget)
        self.setLayout(layout)

    #双击基坑工程中的树节点
    def onItemDoubleClicked(self, item, column):
        itemtext=item.text(0)
        if itemtext == "土方边坡计算":
            print("双击传入：土方边坡计算")
            self.hide()
            parent=self.parent()#Table_Bar.py中的class ECSTabWidget(QTabWidget):
            print(f"父对话框为：{parent.windowTitle()}")
            if parent:
                es = ES()  # 边坡绘制区域
                uuid=es.Getuuid()#获取边坡绘制对话框的uuid
                struuid=str(uuid)#边坡对话框的uuid：文字格式

                index=parent.AddNewLable(itemtext,es,struuid)#给上面添加标签页
                print(f"标签页的id为：{index}")
                #parent.setCurrentIndex(index)#显示当前的标签页
                grdparent=parent.parent()#MainFrame中的class MainWindow(QMainWindow):
                if grdparent:#给右侧的项目树添加节点
                    grdparent.m_CalDock.add_item_by_name(itemtext,struuid)#对话框的uuid和左侧项目树节点共用同一个uuid

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = Foundation_CalculateTreeDialog()
    dialog.show()  # Use show() for non-modal dialog or exec_() for modal dialog
    sys.exit(app.exec_())

