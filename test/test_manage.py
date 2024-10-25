from PySide6.QtWidgets import QApplication
from oss_utils import OssUtils
from tree_node import TreeNode
from file_manage import VirtualFileTreeModel
from image_manage import ImgTreeView
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QMenu
from PySide6.QtCore import Qt
from file_manage import FilterProxyModel

import logging

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,  # 设置日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',  # 设置输出格式
    handlers=[
        logging.FileHandler("app.log"),  # 输出到文件
        logging.StreamHandler()  # 输出到控制台
    ]
)


class FileView(QWidget):
    def __init__(self, model):
        super().__init__()
        # self.model = model
        self.proxy_model = FilterProxyModel()
        self.proxy_model.setSourceModel(model)
        self.tree_view = ImgTreeView(self.proxy_model)
            # tree_view = ImgTreeView(model)
        # self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)  # 启用自定义上下文菜单
        # self.tree_view.customContextMenuRequested.connect(self.open_menu)  # 连接右键菜单事件

        self.search_box = QLineEdit(self)

        self.init_ui()
    def open_menu(self, position):
        self.proxy_model.invalidate()  # 刷新代理模型

        index = self.tree_view.indexAt(position)

        if not index.isValid():
            return
         # critical,don't use index directly
        source_index = self.proxy_model.mapToSource(index)
        node = None
        if source_index.isValid():
            node = source_index.internalPointer()  # 从源模型获取节点
            print(node)
        menu = QMenu()
        # node = index.internalPointer()
        print(node)
        if node.is_file():
            menu.addAction("Open")
            menu.addAction("Copy Path")
            menu.addAction("Rename")
            menu.addAction("Delete")
        else:
            menu.addAction("New Folder")
            menu.addAction("New File")
            menu.addAction("Rename")
            menu.addAction("Delete")

        action = menu.exec(self.tree_view.viewport().mapToGlobal(position))
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.search_box)
        layout.addWidget(self.tree_view)
        
        # self.tree_view.setModel(self.model)
        self.tree_view.setModel(self.proxy_model)
        # 连接搜索框的文本变化信号
        self.search_box.textChanged.connect(self.perform_search)

    def perform_search(self):
        query = self.search_box.text()
        self.proxy_model.set_filter_query(query)

        # 清空选择并展开匹配项的父节点
        self.tree_view.clearSelection()
        
        # 遍历源模型以展开所有符合条件的项
        for row in range(self.proxy_model.rowCount()):
            index = self.proxy_model.index(row, 0)
            if index.isValid():
                self.tree_view.expand(index)  # 展开匹配项
                # 选择当前节点
                self.tree_view.setCurrentIndex(index)
        # matching_indexes = self.tree_view.model().search(query)
        
        # if matching_indexes:
        #     # 高亮显示匹配项
        #     self.tree_view.clearSelection()
        #     for index in matching_indexes:
        #         self.tree_view.setCurrentIndex(index)
        #     # 可选：自动展开匹配的项
        #     for index in matching_indexes:
        #         self.tree_view.expand(index)
        # else:
        #     QMessageBox.information(self, "No Matches", "No items matched your search.")


if __name__ == "__main__":
    app = QApplication([])

    # 创建虚拟文件树并绑定模型
    oss_help = OssUtils()
    root_node = TreeNode(oss_help.image_prefix)
    model = VirtualFileTreeModel(root_node,oss_help)


    # 创建视图并设置模型
    view = FileView(model)
    view.setWindowTitle("Searchable File Tree")
    view.resize(400, 300)
    view.show()

    # 创建自定义的 FileTreeView 视图并设置模型
    # tree_view = FileTreeView(model)
    # tree_view = ImgTreeView(model)

    # tree_view.setWindowTitle("Virtual File Tree with Right-click Menu")
    # tree_view.show()

    app.exec()