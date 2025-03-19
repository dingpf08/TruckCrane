#起重吊装专业 对应的选择对话框
#父窗口是Table_Bar.py中的class ECSTabWidget(QTabWidget):
#class ECSTabWidget(QTabWidget):的父窗口为#MainFrame中的class MainWindow(QMainWindow):
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QTreeWidget, QTreeWidgetItem, QVBoxLayout


#起重吊装计算选择对话框
class Hoisting_CalculateTreeDialog(QDialog):
    def __init__(self,mainWindow=None):
        super().__init__(mainWindow, Qt.WindowSystemMenuHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)  #最大最小关闭按钮
        self.m_MainWindow=mainWindow  #传入主对话框
        print(f"Hoisting传入的主对话为：{self.m_MainWindow}")
        if self.m_MainWindow is not None:
            print(f"Hoisting传入的主对话为-----：{self.m_MainWindow.windowTitle()}")
        self.initUI()

    #初始化起重吊装的各种计算界面
    def InitChildDialog(self):
        pass  # 这里后续会添加具体的计算界面类的实例化

    def initUI(self):
        self.setWindowTitle("起重吊装计算合集")
        self.InitChildDialog()  #初始化起重吊装计算的子对话框
        layout = QVBoxLayout(self)
        # Use QTreeWidget instead of QTreeView
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        # Create a root item for the tree widget
        self.root_item = QTreeWidgetItem(self.tree_widget)
        self.root_item.setText(0, "起重吊装")

        # 添加两个子项目
        self.child_item1 = QTreeWidgetItem(self.root_item)
        self.child_item1.setText(0, "液压汽车起重机吊装计算")

        self.child_item2 = QTreeWidgetItem(self.root_item)
        self.child_item2.setText(0, "履带式起重机吊装计算")

        # Expand all sections in the tree widget
        self.tree_widget.expandAll()
        self.tree_widget.itemDoubleClicked.connect(self.onItemDoubleClicked)

        layout.addWidget(self.tree_widget)
        self.setLayout(layout)

    #双击起重吊装中的树节点
    def onItemDoubleClicked(self, item, column):
        itemtext = item.text(0)
        if itemtext == "液压汽车起重机吊装计算":
            print("双击：液压汽车起重机吊装计算")
            self.hide()
            parent = self.parent()  #Table_Bar.py中的class ECSTabWidget(QTabWidget):
            print(f"父对话框为：{parent.windowTitle()}")
            if parent:
                # TODO: 这里需要添加具体的计算界面类
                pass
        elif itemtext == "履带式起重机吊装计算":
            print("双击：履带式起重机吊装计算")
            self.hide()
            parent = self.parent()
            print(f"父对话框为：{parent.windowTitle()}")
            if parent:
                # TODO: 这里需要添加具体的计算界面类
                pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = Hoisting_CalculateTreeDialog()
    dialog.show()  # Use show() for non-modal dialog or exec_() for modal dialog
    sys.exit(app.exec_()) 