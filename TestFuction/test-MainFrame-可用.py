import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QStatusBar,
                             QToolBar, QTextEdit, QDockWidget, QListWidget, QTabWidget, QWidget, QVBoxLayout, QLabel)
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # 设置主窗口的标题和初始大小
        self.setWindowTitle('PyQt5 控件示例')
        self.setGeometry(100, 100, 600, 400)

        # 创建菜单栏
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('文件')

        # 创建菜单项
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 创建工具栏
        tool_bar = self.addToolBar('工具栏')
        tool_bar.addAction(exit_action)

        # 创建状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('状态栏信息')

        # 创建中心窗口部件
        tab_widget = QTabWidget()
        self.setCentralWidget(tab_widget)

        # 创建标签页内容
        # 标签1
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        tab1_label = QLabel('这是标签1的内容')
        tab1_layout.addWidget(tab1_label)
        tab1.setLayout(tab1_layout)
        tab_widget.addTab(tab1, '标签1')

        # 标签2
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        tab2_text_edit = QTextEdit()
        tab2_layout.addWidget(tab2_text_edit)
        tab2.setLayout(tab2_layout)
        tab_widget.addTab(tab2, '标签2')

        # 标签3
        tab3 = QWidget()
        tab3_layout = QVBoxLayout()
        tab3_list_widget = QListWidget()
        tab3_list_widget.addItems(['列表项A', '列表项B', '列表项C'])
        tab3_layout.addWidget(tab3_list_widget)
        tab3.setLayout(tab3_layout)
        tab_widget.addTab(tab3, '标签3')

        # 创建浮动窗口，并默认放置在界面的左侧
        dock = QDockWidget('工程树图', self)
        dock_widget_contents = QListWidget()
        dock_widget_contents.addItems(['条目1', '条目2', '条目3'])
        dock.setWidget(dock_widget_contents)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        # 使停靠栏成为固定的
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
