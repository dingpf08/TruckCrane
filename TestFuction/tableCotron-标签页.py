# Let's create an example of a tab widget using PyQt5

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a TabWidget
        tab_widget = QTabWidget()

        # Create first tab
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        tab1_label = QLabel('Content of Tab 1')
        tab1_layout.addWidget(tab1_label)
        tab1.setLayout(tab1_layout)

        # Create second tab
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        tab2_label = QLabel('Content of Tab 2')
        tab2_layout.addWidget(tab2_label)
        tab2.setLayout(tab2_layout)

        # Add tabs to the tab widget
        tab_widget.addTab(tab1, 'Tab 1')
        tab_widget.addTab(tab2, 'Tab 2')

        # Set the tab widget as the central widget of the main window
        self.setCentralWidget(tab_widget)

        # Set main window properties
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('QTabWidget Example')

        # Show the main window
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


# Run the example
main()
