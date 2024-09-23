import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from qt_material import apply_stylesheet
from main_window import MainWindow
from waiting_page import WaitingWindow

# from qt_material import list_themes
# print(list_themes())

class MainApp(QApplication):
    def __init__(self):
        super(MainApp, self).__init__(sys.argv)
        self.setWindowIcon(QIcon("./assets/icon.svg"))
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
        from oss_utils import OssUtils
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




if __name__ == "__main__":
    MainApp().run()
