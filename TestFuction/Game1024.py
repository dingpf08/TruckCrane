import sys
import numpy as np
import random
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QGridLayout, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette

class Game2048(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.grid_size = 4
        self.matrix = np.zeros((self.grid_size, self.grid_size), dtype=int)
        self.setWindowTitle('2048 Game')
        self.setFixedSize(400, 400)
        self.setStyleSheet("background-color: #bbada0;")
        self.labels = [[QLabel(self) for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        gridLayout = QGridLayout()
        gridLayout.setSpacing(10)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                label = self.labels[i][j]
                label.setFont(QFont('Arial', 20, QFont.Bold))
                label.setAlignment(Qt.AlignCenter)
                label.setFixedSize(80, 80)
                gridLayout.addWidget(label, i, j)
                label.setStyleSheet("QLabel { background-color: #cdc1b4; border-radius: 10px; }")

        self.setLayout(gridLayout)
        self.init_game()

    def init_game(self):
        self.add_new_tile()
        self.add_new_tile()
        self.update_grid_cells()

    def add_new_tile(self):
        value = 2 if random.random() < 0.9 else 4
        empty_pos = np.argwhere(self.matrix == 0)
        if len(empty_pos) > 0:
            chosen_pos = random.choice(empty_pos)
            self.matrix[tuple(chosen_pos)] = value

    def update_grid_cells(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cell_value = self.matrix[i][j]
                label = self.labels[i][j]
                if cell_value == 0:
                    label.setText('')
                else:
                    label.setText(str(cell_value))
                label.setStyleSheet("QLabel { background-color: %s; color: %s; }" % (
                self.background_color(cell_value), self.text_color(cell_value)))

    def background_color(self, value):
        if value == 0:
            return '#cdc1b4'
        colors = {
            2: '#eee4da', 4: '#ede0c8', 8: '#f2b179', 16: '#f59563',
            32: '#f67c5f', 64: '#f65e3b', 128: '#edcf72', 256: '#edcc61',
            512: '#edc850', 1024: '#edc53f', 2048: '#edc22e'
        }
        return colors.get(value, '#3c3a32')

    def text_color(self, value):
        if value <= 4:
            return '#776e65'
        return '#f9f6f2'

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.move('left')
        elif key == Qt.Key_Right:
            self.move('right')
        elif key == Qt.Key_Up:
            self.move('up')
        elif key == Qt.Key_Down:
            self.move('down')

        self.update_grid_cells()
        if np.any(self.matrix == 1024):
            QMessageBox.information(self, '2048', 'You win!')
        elif not self.move_possible():
            QMessageBox.information(self, '2048', 'Game over!')

    def move(self, direction):
        original = self.matrix.copy()
        if direction in ('left', 'right'):
            self.matrix = np.apply_along_axis(self.compress_and_merge, 1, self.matrix if direction == 'left' else np.fliplr(self.matrix))
            if direction == 'right':
                self.matrix = np.fliplr(self.matrix)
        else:  # up or down
            self.matrix = np.apply_along_axis(self.compress_and_merge, 1, self.matrix.T if direction == 'up' else np.flipud(self.matrix.T))
            self.matrix = self.matrix.T if direction == 'up' else np.flipud(self.matrix.T)
        if not np.array_equal(original, self.matrix):
            self.add_new_tile()

    def compress_and_merge(self, row):
        # Helper function to compress and merge the row
        non_zero = row[row != 0]  # strip zeros
        merged = []
        skip = False
        for i in range(len(non_zero)):
            if skip:
                skip = False
                continue
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged.append(2 * non_zero[i])
                skip = True
            else:
                merged.append(non_zero[i])
        return np.array(merged + [0] * (len(row) - len(merged)))

    def move_possible(self):
        if np.any(self.matrix == 0):
            return True
        for i in range(self.grid_size):
            for j in range(self.grid_size - 1):
                if self.matrix[i][j] == self.matrix[i][j + 1] or self.matrix[j][i] == self.matrix[j + 1][i]:
                    return True
        return False


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setCentralWidget(Game2048())
        self.setGeometry(300, 300, 450, 450)
        self.setWindowTitle('2048 Game')
        self.show()


def main():
    app = QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
