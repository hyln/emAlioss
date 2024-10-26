from PySide6.QtWidgets import QWidget,QLabel,QHBoxLayout,QVBoxLayout,QMenu,QFileDialog,QMessageBox,QLineEdit
from PySide6.QtGui import QPixmap,QAction
from PySide6.QtCore import Qt,QModelIndex,QTimer,Signal
from emalioss.file_manage.oss_utils import OssUtils
from emalioss.file_manage.file_manage import FilterProxyModel,VirtualFileTreeModel,TreeNode,FileTreeView


class ObjTreeView(FileTreeView):
    upload_file_signal = Signal(str, str,int)  
    def __init__(self,model):
        super().__init__(model)
        # self.setHeaderHidden(True)
    def additionalMenu(self, index,menu:QMenu):
        if index.isValid():
            menu.addSeparator()
            upload_action = QAction("Upload File", self)
            upload_action.triggered.connect(lambda: self.upload_file(index))
            menu.addAction(upload_action)
        else:
            pass
        return menu
    def upload_file(self,index):
        print("[ObjTreeView]upload file")
        if index.isValid():
            item = index.internalPointer()
            model = self.model().sourceModel()
            item_path = model.get_object_full_path(index)

            # 只要压缩文件格式 tar.gz,zip
            # file_path = QFileDialog.getOpenFileName(self, "Select File", "", "tar.gz Files (*.tar.gz);;zip Files (*.zip)")
            file_path = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
            if file_path[0]:
                print(f"Selected file: {file_path[0]} , upload to {item_path}")
                
                print(f"Copy {model.oss_help.oss_global_base_url}/{item_path} to clipboard")
                self.upload_file_signal.emit("Uploading","info",-1)
                QTimer.singleShot(100, 
                                  lambda: self.upload(model,item_path,file_path[0]))
               
    def upload(self,model,oss_file_path:str,local_file_path:str):
        try:
            model.oss_help.upload(oss_file_path,local_file_path)
            # self.refresh()
            self.upload_file_signal.emit("Upload success","success",2000)
        except ConnectionError as e:
            print(e)
            self.upload_file_signal.emit("Failed to connect to OSS","error",2000)
        except Exception as e:
            print(e)
            self.upload_file_signal.emit("Upload failed","error",2000)
class ObjWidget(QWidget):
    def __init__(self,oss_utils:OssUtils):
        '''创建文件管理页面'''
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
        root_node = TreeNode(oss_utils.prj_prefix)
        model = VirtualFileTreeModel(root_node,oss_utils)
        self.proxy_model = FilterProxyModel()
        self.proxy_model.setSourceModel(model)

        self.tree_view = ObjTreeView(self.proxy_model)
        # self.tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.tree_view.copy_url_signal.connect(self.show_status_message)
        self.tree_view.upload_file_signal.connect(self.show_status_message)

        H1_layout.addWidget(self.tree_view)
        self.V_layout.addLayout(H1_layout)
        # 创建状态标签
        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("background-color: black; color: white; font-size: 16px;")
        self.status_label.setVisible(False)
        H2_layout.addWidget(self.status_label)
        self.V_layout.addLayout(H2_layout)

    def hide_status_message(self):
        self.status_label.setVisible(False)
    def show_status_message(self, message,msg_type='success', duration=2000):
        self.status_label.setText(message)
        if(msg_type == "info"):
            self.status_label.setStyleSheet("background-color: #909083; color: white; font-size: 16px;")
        elif(msg_type == "warning"):
            self.status_label.setStyleSheet("background-color: #d4a883; color: white; font-size: 16px;")
        elif(msg_type == "success"):
            self.status_label.setStyleSheet("background-color: #5daa8c; color: white; font-size: 16px;")
        elif(msg_type == "error"):
            self.status_label.setStyleSheet("background-color: #c85662; color: white; font-size: 16px;")
        self.status_label.setVisible(True)
        if(duration > 0):
            QTimer.singleShot(duration, self.hide_status_message)
    # def on_selection_changed(self, selected, deselected):
    #     '''左键点击图片时显示缩略图'''
    #     for index in selected.indexes():
    #         source_index = self.proxy_model.mapToSource(index) # 使用了QSortFilterProxyModel，需要转换为源模型的索引,否则在访问node时会crash
    #         node = source_index.internalPointer() 
    #         # get full path 
    #         item_path = self.proxy_model.sourceModel().get_object_full_path(source_index)
    #         # print("item_path: " + item_path)
    #         if(node.is_folder is False):
    #             if(self.oss_utils.get_path_suffix(item_path) == ".svg"):
    #                 pixmap = QPixmap(self.oss_utils.get_resize_image(item_path,-1))
    #             else:
    #                 pixmap = QPixmap(self.oss_utils.get_resize_image(item_path,200))
    #             pixmap.scaled(200, 200, Qt.KeepAspectRatio)
    #             self.image_label.setPixmap(pixmap)
    #             self.image_label.show()
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