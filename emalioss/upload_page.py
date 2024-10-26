from PySide6.QtWidgets import QVBoxLayout,QHBoxLayout,QWidget,QPushButton,QComboBox,QLabel,QFileDialog,QProgressBar
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMessageBox

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap,QKeyEvent
from emalioss.file_manage.oss_utils import OssUtils
from time import time
import time
import os
class CustomComboBox(QComboBox):
    def __init__(self, oss_utils:OssUtils) -> None:
        super().__init__()
        self.oss_utils = oss_utils
        self.currentIndexChanged.connect(self.handle_selection_change)
        self.selected_folder = ""

    def showPopup(self):
        self.update_combobox_items()
        super().showPopup()

    def update_combobox_items(self):
        """在下拉列表显示时更新 QComboBox 的项"""
        try:
            new_items = self.oss_utils.get_folder_list(self.oss_utils.image_prefix)
            self.clear()  # 清除当前项
            self.addItems(new_items)  # 添加新的项
        except ConnectionError as e:
            QMessageBox.critical(self, "网络异常", "无法连接到服务器，请检查您的网络连接。")

    def handle_selection_change(self, index):
        selected_item = self.itemText(index)
        if(selected_item == "选择存储文件夹" or selected_item == ""):
            return 
        print(f"Selected folder: {selected_item}")
        self.selected_folder = selected_item

class UploadPage(QWidget):
    def __init__(self,oss_utils:OssUtils) -> None:
        super().__init__()
        self.oss_utils = oss_utils
        self.current_image_path = ""
        layout = QVBoxLayout()

        self.upload_button = QPushButton("上传图片")
        self.upload_button.clicked.connect(self.upload_image)
        
        # 创建 QComboBox（选项框）
        self.comboBox = CustomComboBox(oss_utils)
        self.comboBox.addItems(["选择存储文件夹"])  # 添加分类选项
        self.comboBox.setStyleSheet("color: white;")

        # 创建进度条容器
        self.progress_container = QWidget()
        self.progress_layout = QHBoxLayout(self.progress_container)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)  # 最小值
        self.progress_bar.setMaximum(100)  # 最大值
        self.progress_bar.setValue(0)  # 初始值
        self.progress_bar.setTextVisible(True)  # 显示文本

        # self.image_container = QWidget()
        # self.image_layout = QHBoxLayout(self.image_container)

        # self.image_labels = []
        # for _ in range(4):
        #     label = QLabel()
        #     label.setAlignment(Qt.AlignCenter)
        #     self.image_labels.append(label)
        #     self.image_layout.addWidget(label)

        # layout.addWidget(self.image_container)

        self.upload_status_label = QLabel("等待图片上传")

        self.progress_layout.addWidget(self.progress_bar)
        self.progress_layout.addWidget(self.upload_status_label)
        self.progress_container.setMaximumHeight(50)  

        self.upload_label = QLabel("托拽图片上传|Ctrl+V粘贴")
        self.upload_label.setAlignment(Qt.AlignCenter)

        self.copy_url_button = QPushButton("复制当前图片链接")
        self.copy_url_button.clicked.connect(self.handle_button_click)
        
        self.text_box = QLineEdit("在此输入V粘贴图片")
        self.text_box.setReadOnly(True)
        self.text_box.setStyleSheet("color: white;")
        layout.addWidget(self.comboBox)
        layout.addWidget(self.upload_label)
        layout.addWidget(self.text_box)
        layout.addWidget(self.progress_container)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.copy_url_button)

        self.setAcceptDrops(True)
        self.setLayout(layout)

    def upload_file2oss(self,file_path:str):
        if(self.has_folder_choose() == False):
            print("没有选择文件夹")
            return False
        print("selected_folder"+self.comboBox.selected_folder)
        self.oss_utils.upload(self.comboBox.selected_folder,file_path.replace("\\","/"))
        print(self.oss_utils.get_latest_upload_url())
        self.text_box.setText(self.oss_utils.get_latest_upload_url())    
        return True                                       
        
    # def has_same_image(self, image_path):
    def upload_image(self):
        if(self.has_folder_choose() == False):
                return
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["Images (*.png *.jpg *.jpeg *.bmp *.gif)"])
        if file_dialog.exec():
            if(self.upload_file2oss(file_dialog.selectedFiles()[0])):  
                file_path = file_dialog.selectedFiles()[0]
                print(file_path)
                pixmap = QPixmap(file_path)
                self.upload_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
                self.progress_bar.setFormat("上传成功")
                print(self.current_image_path)
                self.progress_bar.setValue(100)
    def has_folder_choose(self):
        if self.comboBox.selected_folder == "选择存储文件夹" or self.comboBox.selected_folder == "":
            QMessageBox.warning(self, "提示", "你没有选择存储文件夹")
            print("你没有选择存储文件夹")
            return False
        else:
            return True
    def preview_image(self, image_path):
        """预览图片"""
        pixmap = QPixmap(image_path)
        self.upload_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
    # 处理粘贴事件
    def keyPressEvent(self, event:QKeyEvent):
        if event.key() == Qt.Key_V and QApplication.clipboard().mimeData().hasImage():
            # 获取剪贴板中的图片
            if(self.has_folder_choose() == False):
                return
            image = QApplication.clipboard().image()
            
            if not image.isNull():
                # 保存图片到临时文件
                temp_dir = "./tmp"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                current_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
                temp_file_path = os.path.join(temp_dir, f"image_{current_time}.png")
                image.save(temp_file_path)
                print(temp_file_path)

                self.preview_image(temp_file_path)
                self.upload_file2oss(temp_file_path)
            # 当拖拽进入窗口时调用
    def dragEnterEvent(self, event):
        # 检查拖拽的数据是否是文件 URL
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # 当文件拖拽到窗口并释放时调用
    def dropEvent(self, event):
        # 获取拖拽的文件路径
        files = event.mimeData().urls()
        if files:
            if(self.has_folder_choose() == False):
                return
            # 获取文件路径列表（可能有多个文件）
            file_paths = [url.toLocalFile() for url in files]
            print(file_paths)
            for i in file_paths:
                print(i)
                self.upload_file2oss(i)
            # 显示出来
            pixmap = QPixmap(file_paths[0])
            self.upload_label.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
    def handle_button_click(self):
        url = self.oss_utils.get_latest_upload_url()
        self.text_box.setText(url)
        QApplication.clipboard().setText(url)
        print("[upload_page]复制当前图片链接")
