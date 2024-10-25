from PySide6.QtWidgets import QWidget,QLabel,QHBoxLayout,QVBoxLayout,QMenu,QInputDialog,QMessageBox,QLineEdit
from PySide6.QtGui import QPixmap,QAction
from PySide6.QtCore import Qt,QModelIndex,QTimer
from emalioss.file_manage.oss_utils import OssUtils
from emalioss.file_manage.file_manage import FilterProxyModel,VirtualFileTreeModel,TreeNode,FileTreeView

class ImgTreeView(FileTreeView):
    def __init__(self,model):
        super().__init__(model)
        # self.setHeaderHidden(True)
    def additionalMenu(self, index,menu:QMenu):
        if index.isValid():
            menu.addSeparator()
            upload_action = QAction("Upload Img", self)
            upload_action.triggered.connect(lambda: QMessageBox.information(self, "Upload Img", "TODO"))
            menu.addAction(upload_action)
        else:
            pass
        return menu
    def upload_img(self):
        pass
    
class Imgwidget(QWidget):
    def __init__(self,oss_utils:OssUtils):
        '''创建图片管理页面'''
        super().__init__()

        self.oss_utils = oss_utils
        self.V_layout = QVBoxLayout(self) # 只能有一个传入self，并被setlayout
        H0_layout = QHBoxLayout()
        H1_layout = QHBoxLayout()
        H2_layout = QHBoxLayout()

        # 创建搜索框
        self.search_box = QLineEdit(self)
        self.search_box.setStyleSheet("color: white; font-size: 16px;")
        self.search_box.textChanged.connect(self.perform_search)

        H0_layout.addWidget(self.search_box)
        self.V_layout.addLayout(H0_layout)
        # 创建树形视图
        root_node = TreeNode(oss_utils.image_prefix)
        model = VirtualFileTreeModel(root_node,oss_utils)
        self.proxy_model = FilterProxyModel()
        self.proxy_model.setSourceModel(model)

        self.tree_view = ImgTreeView(self.proxy_model)
        self.tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.tree_view.copy_url_signal.connect(self.show_status_message)
        # 创建图片预览标签
        self.image_label = QLabel()
        self.image_label.setMinimumSize(200, 200)
        self.image_label.setText("图片预览")
        self.image_label.hide()
        self.image_label.setAlignment(Qt.AlignCenter)
        
        H1_layout.addWidget(self.tree_view)
        H1_layout.addWidget(self.image_label)
        self.V_layout.addLayout(H1_layout)
        # 创建状态标签
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("background-color: black; color: white; font-size: 16px;")
        self.status_label.setVisible(False)
        H2_layout.addWidget(self.status_label)
        self.V_layout.addLayout(H2_layout)
        # self.show_status_message("Copy url success")
        # self.setLayout(self.V_layout)

    def hide_status_message(self):
        self.status_label.setVisible(False)
    def show_status_message(self, message, duration=2000):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("background-color: #5daa8c; color: white; font-size: 16px;")
        self.status_label.setVisible(True)
        QTimer.singleShot(duration, self.hide_status_message)
    def on_selection_changed(self, selected, deselected):
        '''左键点击图片时显示缩略图'''
        for index in selected.indexes():
            source_index = self.proxy_model.mapToSource(index) # 使用了QSortFilterProxyModel，需要转换为源模型的索引,否则在访问node时会crash
            node = source_index.internalPointer() 
            # get full path 
            item_path = self.proxy_model.sourceModel().get_object_full_path(source_index)
            # print("item_path: " + item_path)
            if(node.is_folder is False):
                if(self.oss_utils.get_path_suffix(item_path) == ".svg"):
                    pixmap = QPixmap(self.oss_utils.get_resize_image(item_path,-1))
                else:
                    pixmap = QPixmap(self.oss_utils.get_resize_image(item_path,200))
                pixmap.scaled(200, 200, Qt.KeepAspectRatio)
                self.image_label.setPixmap(pixmap)
                self.image_label.show()
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