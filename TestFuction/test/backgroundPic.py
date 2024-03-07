from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QBrush
from PyQt5.QtWidgets import QDialog, QApplication

class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        # 设置窗口标志
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint| Qt.WindowCloseButtonHint)
        # 加载图片
        pixmap = QPixmap("background.png")

        # 创建背景画刷
        brush = QBrush(pixmap)

        # 设置背景
        self.setStyleSheet("background-image: url(background.png);")

if __name__ == "__main__":
    app = QApplication([])

    dialog = MyDialog()
    dialog.show()

    app.exec()
