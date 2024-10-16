import os
from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtGui import QPainterPath
from PySide6.QtGui import QRegion

class WaitingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("等待连接")
        self.setGeometry(500, 300, 300, 200)
        # self.setFixedSize(500, 500)  # 设置窗口大小为500x500
        self.set_rounded_corners(20)

        self.setWindowFlags(Qt.FramelessWindowHint)
        layout = QVBoxLayout()
        self.label = QLabel("OSS等待连接...")
        self.label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.label)

        self.setLayout(layout)
    def set_rounded_corners(self, radius):
        path = QPainterPath()
        path.addRoundedRect(QRect(0, 0, self.width(), self.height()), radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
    def update_status(self, status):
        """更新连接状态"""
        self.label.setText(status)
    def show_close_button(self):
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        layout = self.layout()
        layout.addWidget(self.close_button)
    def check_cfg_exist(self):
        current_directory = os.getcwd()
        file_name = "config.ini"
        if os.path.exists(os.path.join(current_directory, file_name)):
            print(f"{file_name} 文件存在。")
            return True
        else:
            print(f"{file_name} 文件不存在。")
            return False