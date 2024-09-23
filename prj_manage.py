from PySide6.QtWidgets import QWidget,QLabel,QHBoxLayout,QMenu,QInputDialog
from PySide6.QtGui import QPixmap,QAction
from PySide6.QtCore import Qt,QModelIndex
from oss_manage import OssTreeView,OSSModel
from oss_utils import OssUtils
class PrjManage(QWidget):
    def __init__(self,oss_utils:OssUtils):
        '''创建开源项目包管理页面'''
        super().__init__()
        self.oss_utils = oss_utils
        self.image_management_layout = QHBoxLayout(self)
        self.custom_tree_widget = OssTreeView(oss_utils,self.oss_utils.prj_prefix)
        self.custom_tree_widget.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.custom_tree_widget.customContextMenuRequested.connect(self.show_context_menu)

        self.image_management_layout.addWidget(self.custom_tree_widget)
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

        upload_file_action = QAction("Upload File", self)
        menu.addAction(upload_file_action)


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