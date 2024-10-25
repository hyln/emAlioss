import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from qt_material import apply_stylesheet
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from emalioss.main_window import MainWindow
from emalioss.waiting_page import WaitingWindow
import logging
# from qt_material import list_themes
# print(list_themes())

# 配置日志记录
import logging
import platform
import os
from datetime import datetime

# 获取当前时间戳并格式化为文件名（如：20241016_153000）
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 获取不同操作系统的 Documents 目录
if platform.system() == "Windows":
    documents_dir = os.path.join(os.path.expanduser('~'), 'Documents')
elif platform.system() == "Darwin":  # macOS
    documents_dir = os.path.expanduser('~/Documents')
elif platform.system() == "Linux":
    documents_dir = os.path.expanduser('~/Documents')
else:
    documents_dir = './'  # 默认路径

# 创建子目录存放日志
log_dir = os.path.join(documents_dir, 'emalioss_logs')
os.makedirs(log_dir, exist_ok=True)

# 日志文件路径，文件名带有时间戳
log_file = os.path.join(log_dir, f'emalioss_{timestamp}.log')

# 设置日志配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=log_file,
                    filemode='a')
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='emalioss.log', filemode='a')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='emalioss.log', filemode='a')

class PrintLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.strip() != "":
            self.logger.log(self.level, message.strip())

    def flush(self):
        pass

# 重定向 print 输出到日志
# sys.stdout = PrintLogger(logging.getLogger(), logging.INFO)
# sys.stderr = PrintLogger(logging.getLogger(), logging.ERROR)


class MainApp(QApplication):
    def __init__(self):
        super(MainApp, self).__init__(sys.argv)
        current_file_path = os.path.abspath(__file__)
        current_directory = os.path.dirname(current_file_path)
        self.setWindowIcon(QIcon(current_directory+"/assets/icon.svg"))
        apply_stylesheet(self, theme='dark_blue.xml')
        self.init_waiting_window()

    def init_waiting_window(self):
        self.waiting_window = WaitingWindow()
        self.waiting_window.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.waiting_window.show()
        self.waiting_window.update_status("Initializing...")
        QTimer.singleShot(100, lambda: self.init_oss_connect())
        # if(self.waiting_window.check_cfg_exist()):
        #     self.waiting_window.update_status("配置文件存在,准备连接")
        #     QTimer.singleShot(100, lambda: self.init_oss_connect())
        # else:
        #     self.waiting_window.update_status("配置文件不存在,请参考readme检查")
        #     self.waiting_window.show_close_button()
        #     self.waiting_window.show()
        sys.exit(self.exec())

    def show_main_window(self, waiting_window, main_window):
        '''关闭等待窗口并显示主窗口'''
        main_window.show()
        QTimer.singleShot(500, lambda: waiting_window.close())
        
    def init_oss_connect(self):
        from emalioss.file_manage.oss_utils import OssUtils
        try:
            self.oss_utils = OssUtils()
            self.waiting_window.update_status("成功连接至OSS")
            self.main_window = MainWindow(self.oss_utils)
            self.main_window.resize(800, 600)
            QTimer.singleShot(500, lambda: self.show_main_window(self.waiting_window, self.main_window))
        except FileNotFoundError as e:
            print(e)
            self.waiting_window.update_status("配置文件不存在")
            self.waiting_window.show_close_button()
            self.waiting_window.show()
        except ConnectionError as e:
            print(e)
            self.waiting_window.update_status("无法连接至OSS，请检查配置文件或网络")
            self.waiting_window.show_close_button()
            self.waiting_window.show()


def main():
    MainApp().run()


if __name__ == "__main__":
    main()