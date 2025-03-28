from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QApplication)
import sys
import math

class CraneSupportForceCalculator:
    def __init__(self, weight, boom_length, angle, distance):
        self.weight = weight  # 吊重
        self.boom_length = boom_length  # 吊臂长度
        self.angle = angle  # 吊臂角度
        self.distance = distance  # 支腿距离

    def calculate_support_force(self):
        # 计算支腿反力
        angle_radians = math.radians(self.angle)
        force = (self.weight * self.boom_length * math.cos(angle_radians)) / self.distance
        return force

class CraneSupportForceCalculatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.weight_input = QLineEdit(self)
        self.weight_input.setPlaceholderText("Enter weight (kg)")
        layout.addWidget(QLabel("Weight (kg):"))
        layout.addWidget(self.weight_input)

        self.boom_length_input = QLineEdit(self)
        self.boom_length_input.setPlaceholderText("Enter boom length (m)")
        layout.addWidget(QLabel("Boom Length (m):"))
        layout.addWidget(self.boom_length_input)

        self.angle_input = QLineEdit(self)
        self.angle_input.setPlaceholderText("Enter angle (degrees)")
        layout.addWidget(QLabel("Angle (degrees):"))
        layout.addWidget(self.angle_input)

        self.distance_input = QLineEdit(self)
        self.distance_input.setPlaceholderText("Enter distance (m)")
        layout.addWidget(QLabel("Distance (m):"))
        layout.addWidget(self.distance_input)

        self.calculate_button = QPushButton("Calculate Support Force", self)
        self.calculate_button.clicked.connect(self.calculate_force)
        layout.addWidget(self.calculate_button)

        self.result_label = QLabel("", self)
        layout.addWidget(self.result_label)

        self.setLayout(layout)
        self.setWindowTitle("Crane Support Force Calculator")

    def calculate_force(self):
        try:
            weight = float(self.weight_input.text())
            boom_length = float(self.boom_length_input.text())
            angle = float(self.angle_input.text())
            distance = float(self.distance_input.text())

            calculator = CraneSupportForceCalculator(weight, boom_length, angle, distance)
            support_force = calculator.calculate_support_force()
            self.result_label.setText(f"Support Force: {support_force:.2f} N")
        except ValueError:
            self.result_label.setText("Please enter valid numbers.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CraneSupportForceCalculatorUI()
    window.show()
    sys.exit(app.exec_())