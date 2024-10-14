from PySide6.QtWidgets import QWidget,QLabel,QVBoxLayout,QMenu,QInputDialog,QFileDialog,QMessageBox,QApplication
from PySide6.QtGui import QPixmap,QAction
from PySide6.QtCore import Qt,QModelIndex,QTimer
from oss_manage import OssTreeView,OSSModel
from oss_utils import OssUtils
class PrjManage(QWidget):
    def __init__(self,oss_utils:OssUtils):
        '''创建开源项目包管理页面'''
        super().__init__()
        self.oss_utils = oss_utils
        self.image_management_layout = QVBoxLayout(self)
        self.custom_tree_widget = OssTreeView(oss_utils,self.oss_utils.prj_prefix)
        self.custom_tree_widget.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.custom_tree_widget.customContextMenuRequested.connect(self.show_context_menu)

        self.image_management_layout.addWidget(self.custom_tree_widget)


        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("background-color: black; color: white; font-size: 16px;")
        self.status_label.setVisible(False)
        self.image_management_layout.addWidget(self.status_label)
    def hide_status_message(self):
        self.status_label.setVisible(False)
    def show_status_message(self, message, duration=2000):
        self.status_label.setText(message)
        self.status_label.setVisible(True)
        QTimer.singleShot(duration, self.hide_status_message)

    def show_context_menu(self, position):
        '''显示菜单，根据点击位置显示不同的菜单'''
        index = self.custom_tree_widget.indexAt(position)
        if not index.isValid():
            self.show_blank_context_menu(position)
        else:
            self.show_item_context_menu(position, index)
    def on_selection_changed(self, selected, deselected):
        '''左键点击图片时显示缩略图'''
        # for index in selected.indexes():
        #     node = index.internalPointer() 
        #     print(f"Selected: {node.name}")
        #     # get full path
        #     item_path = node.parent.name +"/"+node.name
        #     loop_parent_node = node.parent
        #     while(loop_parent_node.parent):
        #         loop_parent_node = loop_parent_node.parent
        #         item_path = loop_parent_node.name + "/" + item_path 
        #     print("[prjManage] select item_path: " + item_path)
        #     if(self.oss_utils.is_directory(item_path) is False):
        #         pixmap = QPixmap(self.oss_utils.get_resize_image(item_path,200))
        #         # pixmap.scaled(150, 150, Qt.KeepAspectRatio)
        #         self.image_label.setPixmap(pixmap)
        #         self.image_label.show()
    def show_item_context_menu(self, position, index):
        '''显示选中某项时的菜单'''
        menu = QMenu()
        
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(self.rename_item)
        menu.addAction(rename_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_item)
        menu.addAction(delete_action)
        
        if index.isValid():
            item = index.internalPointer()
        if(self.oss_utils.is_directory(item.name)):  
            new_folder_action = QAction(f"New Folder(/{item.name})", self)
            new_folder_action.triggered.connect(lambda: self.new_folder(index))
            menu.addAction(new_folder_action)

        copy_url_action = QAction("Copy Oss Link", self)
        menu.addAction(copy_url_action)
        copy_url_action.triggered.connect(lambda: self.copy_url())

        upload_file_action = QAction("Upload File", self)
        menu.addAction(upload_file_action)
        upload_file_action.triggered.connect(lambda: self.upload_file())



        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(lambda: self.refresh())
        menu.addAction(refresh_action)  
        menu.exec_(self.custom_tree_widget.viewport().mapToGlobal(position))
    def show_blank_context_menu(self, position):
        '''显示选中空白处时的菜单'''
        menu = QMenu()
        
        new_folder_action = QAction("New Folder", self)
        new_folder_action.triggered.connect(lambda: self.new_folder())
        menu.addAction(new_folder_action)
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(lambda: self.refresh())
        menu.addAction(refresh_action)
        menu.exec_(self.custom_tree_widget.viewport().mapToGlobal(position))
    def refresh(self):
        print("[prjManage] refresh")
        self.model = OSSModel(self.oss_utils,self.oss_utils.prj_prefix)
        self.custom_tree_widget.setModel(self.model)
        self.custom_tree_widget.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.custom_tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        # self.custom_tree_widget.expandAll()
    def copy_url(self):
        index = self.custom_tree_widget.currentIndex()
        if index.isValid():
            item = index.internalPointer()
            item_path = item.name
            while(item.parent):
                item = item.parent
                item_path = item.name + "/" + item_path 
            copy_url = f"{self.oss_utils.oss_global_base_url}/{item_path}"
            print(f"Copy url: {copy_url}")
            # copy to clipboard
            QApplication.clipboard().setText(copy_url)
            self.show_status_message("Copy url success")

            # self.oss_utils.copy_to_clipboard(item.name)

    def upload_file(self):
        print("[prjManage]upload file")
        index = self.custom_tree_widget.currentIndex()
        if index.isValid():
            item = index.internalPointer()
            item_path = item.name
            while(item.parent):
                item = item.parent
                item_path = item.name + "/" + item_path  
            # 只要压缩文件格式 tar.gz,zip
            file_path = QFileDialog.getOpenFileName(self, "Select File", "", "tar.gz Files (*.tar.gz);;zip Files (*.zip)")
            if file_path[0]:
                print(f"Selected file: {file_path[0]} , upload to {item_path}")
                try:
                    self.oss_utils.upload(item_path,file_path[0])
                    self.refresh()
                except ConnectionError as e:
                    print(e)
                    QMessageBox.warning(self, "提示", "Failed to connect to OSS")
    def rename_item(self):
        index = self.custom_tree_widget.currentIndex()
        if index.isValid():
            item = self.custom_tree_widget.model.itemFromIndex(index)
            new_text, ok = QInputDialog.getText(self, "Rename Item", "New name:", text=item.text())
            if ok and new_text:
                self.custom_tree_widget.model.rename_item(index, new_text)

    def delete_item(self):
        print("[prjManage]delete")
        index = self.custom_tree_widget.currentIndex()
        if index.isValid():
            self.custom_tree_widget.model.remove_item(index)

    def new_folder(self,index=None):
        print("[prjManage]create new folder")

        if index is not None:
            item = index.internalPointer()
            new_folder_name, ok = QInputDialog.getText(None, f"New Folder{item.name}/", "Folder name:")
        else:
            new_folder_name, ok = QInputDialog.getText(None, f"New Folder", "Folder name:")

        if ok and new_folder_name:
            if index is None:
                self.custom_tree_widget.model.add_item(QModelIndex(), new_folder_name)
            else:
                self.custom_tree_widget.model.add_item(index, new_folder_name)
            # self.refresh()