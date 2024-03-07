import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QWidget, QVBoxLayout, QFileSystemModel, QLabel, \
    QTreeWidget


class TreeView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        label = QLabel('工程树图')
        layout.addWidget(label)

        self.tree = QTreeView(self)
        # 设置树状图节点
        layout.addWidget(self.tree)

        self.model = QFileSystemModel()
        self.model.setRootPath('')

        self.tree.setModel(self.model)

        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    tree_view = TreeView(mainWindow)
    mainWindow.setCentralWidget(tree_view)
    mainWindow.show()
    sys.exit(app.exec_())
