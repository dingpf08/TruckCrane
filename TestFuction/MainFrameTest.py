import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QMenuBar,
                             QToolBar, QLabel, QDockWidget, QTextEdit,
                             QVBoxLayout, QWidget, QGridLayout, QPushButton,
                             QLineEdit, QFormLayout)
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建主窗口的布局
        self.setWindowTitle('PyQt5 Interface Example')
        self.setGeometry(100, 100, 800, 600)

        # 创建菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件(F)')
        edit_menu = menubar.addMenu('编辑(E)')

        # 创建工具栏
        toolbar = QToolBar('Main Toolbar')
        self.addToolBar(toolbar)
        toolbar.addAction(QAction('Open', self))
        toolbar.addAction(QAction('Save', self))
        toolbar.addAction(QAction('Exit', self))

        # 创建状态栏
        statusbar = self.statusBar()
        statusbar.showMessage('Ready')

        # 创建左侧的设置区域
        left_dock_widget = QDockWidget('设置区域', self)
        self.addDockWidget(Qt.LeftDockWidgetArea, left_dock_widget)
        settings_widget = QWidget()
        settings_layout = QFormLayout()
        settings_widget.setLayout(settings_layout)

        # 添加输入框和按钮
        settings_layout.addRow('参数1:', QLineEdit())
        settings_layout.addRow('参数2:', QLineEdit())
        settings_layout.addRow(QPushButton('应用'), QPushButton('重置'))

        left_dock_widget.setWidget(settings_widget)

        # 创建中间的绘图显示区域
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        central_layout.addWidget(QLabel('绘图显示区域'))

        # 创建右侧的日志输出区域
        right_dock_widget = QDockWidget('日志输出区域', self)
        self.addDockWidget(Qt.RightDockWidgetArea, right_dock_widget)
        log_widget = QTextEdit()
        right_dock_widget.setWidget(log_widget)

        self.setCentralWidget(central_widget)

        # 创建底部的信息显示区
        bottom_dock_widget = QDockWidget('信息显示区', self)
        self.addDockWidget(Qt.BottomDockWidgetArea, bottom_dock_widget)
        info_widget = QLabel('信息显示')
        bottom_dock_widget.setWidget(info_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
