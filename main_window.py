from PySide6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QDockWidget, QListWidget, QListWidgetItem, QStackedWidget,
    QFileDialog,QComboBox,QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from upload_page import UploadPage
from image_manage import ImgManage
from prj_manage import PrjManage


class MainWindow(QMainWindow):
    def __init__(self,oss_utils):
        super().__init__()

        # 设置窗口标题
        self.setWindowTitle("Alioss 资源管理器")

        # 创建侧边栏
        self.dock_widget = QDockWidget(self)
        self.dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.dock_widget.setFeatures(QDockWidget.NoDockWidgetFeatures)
        # 隐藏侧边栏的标题
        self.dock_widget.setTitleBarWidget(QWidget())  # 隐藏标题栏
        self.dock_widget.setFixedWidth(150)  # 设置固定宽度为200px

        # 创建侧边栏中的选项列表
        self.list_widget = QListWidget()
        self.list_widget.addItem("上传图片")
        self.list_widget.addItem("图片管理")
        self.list_widget.addItem("文件包管理")

        # self.list_widget.addItem("设置")

        # 将选项列表添加到侧边栏
        self.dock_widget.setWidget(self.list_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)

        # 创建主内容区域，用于切换不同页面
        self.stack_widget = QStackedWidget()
        self.setCentralWidget(self.stack_widget)

        # 将各个页面添加到堆栈小部件中
        self.upload_page = UploadPage(oss_utils)
        self.img_manage_page = ImgManage(oss_utils)
        self.prj_manage_page = PrjManage(oss_utils)
    
        self.stack_widget.addWidget(self.upload_page)
        self.stack_widget.addWidget(self.img_manage_page)
        self.stack_widget.addWidget(self.prj_manage_page)

        # 连接侧边栏选项的点击事件，切换页面
        self.list_widget.currentRowChanged.connect(self.display_page)

    # 切换页面
    def display_page(self, index):
        self.stack_widget.setCurrentIndex(index)
