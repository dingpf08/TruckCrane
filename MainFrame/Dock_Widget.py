from PyQt5.QtWidgets import QDockWidget, QListWidget, QListWidgetItem, QApplication, QMainWindow
from PyQt5.QtCore import Qt
#父窗口为MainFrame.py中的class MainWindow(QMainWindow):
class CalculateDockWidget(QDockWidget):
    def __init__(self, title, parent=None):
        super(CalculateDockWidget, self).__init__(title, parent)
        self.init_ui()

    def init_ui(self):
        self.dock_widget_contents = QListWidget()
        self.dock_widget_contents.addItems(['条目1', '条目2', '条目3'])
        self.setWidget(self.dock_widget_contents)
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)
    #给根目录下添加节点
    def add_item_by_name(self, item_name):
        item = QListWidgetItem(item_name)
        self.dock_widget_contents.addItem(item)

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