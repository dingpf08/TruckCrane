from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, QCheckBox, QPushButton, QGroupBox, QFormLayout

class FormWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.groupBox = QGroupBox("表单标题")
        formLayout = QFormLayout()

        # 添加标签和输入框
        formLayout.addRow(QLabel("输入1:"), QLineEdit())
        formLayout.addRow(QLabel("输入2:"), QDoubleSpinBox())
        formLayout.addRow(QLabel("选项:"), QCheckBox("启用某功能"))
        formLayout.addRow(QPushButton("提交"), QPushButton("取消"))

        self.groupBox.setLayout(formLayout)

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.groupBox)
        self.setLayout(mainLayout)

if __name__ == '__main__':
    app = QApplication([])
    form_widget = FormWidget()
    form_widget.show()
    app.exec_()
