from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel
from PySide6.QtWidgets import QApplication, QTreeView, QMenu,QMessageBox,QInputDialog
from PySide6.QtGui import QAction,QPixmap
from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel, QPoint

from emalioss.file_manage.tree_node import TreeNode
from emalioss.file_manage.oss_utils import OssUtils

from PySide6.QtCore import QSortFilterProxyModel,QModelIndex
from PySide6.QtCore import Qt,Signal

# 自定义过滤模型
class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.filter_query = ""

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        # 先获取源模型
        model = self.sourceModel()
        if not model:
            return False
        
        # 获取当前行的数据
        index = model.index(sourceRow, 0, sourceParent)
        item = index.internalPointer()
        matches_filter = self.filter_query.lower() in item.name.lower()  # 检查是否匹配
        
        # TODO: 需要优化，
        # 递归检查子项是否匹配
        if matches_filter:
            return True
        # 如果父项匹配，则直接返回 True
        parentIndex = index.parent()
        if parentIndex.isValid():
            parentItem = parentIndex.internalPointer()
            if self.filter_query in parentItem.name.lower():
                return True

        # 都不匹配则递归检查子项
        for i in range(model.rowCount(model.index(sourceRow, 0, sourceParent))):
            if self.filterAcceptsRow(i, model.index(sourceRow, 0, sourceParent)):
                return True

        return False

    def set_filter_query(self, query: str):
        self.filter_query = query
        self.invalidateFilter()  # 重新应用过滤

# 文件树模型类
class VirtualFileTreeModel(QAbstractItemModel):
    def __init__(self, root_node:TreeNode,oss_help:OssUtils, parent=None):
        super().__init__(parent)
        self.oss_help = oss_help
        self.root_name = root_node.name
        print(f"Virtual root name {self.root_name}")

        self.get_model_data(self.oss_help.get_all_files(self.root_name), root_node)

        self._root_node = root_node
    def get_model_data(self,data:list[str], parent:TreeNode):
        '''
        @description: 递归获取所有文件夹和文件
        @param {list[str]} data: 读取到的文件夹和文件列表
        @param {TreeNode} parent: 父节点
        '''
        for item in data:
            parts = item.split('/')
            current_node = parent
            for part in parts:
                if part:
                    found = False
                    for child in current_node.children:
                        if child.name == part:
                            current_node = child
                            found = True
                            break
                    if not found:
                        new_node = TreeNode(part, current_node)
                        current_node.add_child(new_node)
                        current_node = new_node
    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            node = self._root_node
        else:
            node = parent.internalPointer()
        return node.child_count()

    def columnCount(self, parent=QModelIndex()):
        return self._root_node.column_count()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        node = index.internalPointer()
        if role == Qt.DisplayRole:
            return node.name
        elif role == Qt.DecorationRole:
            if node.is_folder:
                return "📁"
            else:
                return "📄"
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return self.root_name
                # return "Name"
        return None

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_node = self._root_node
        else:
            parent_node = parent.internalPointer()

        child_node = parent_node.child(row)
        if child_node:
            return self.createIndex(row, column, child_node)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_node = index.internalPointer()
        parent_node = child_node.parent

        if parent_node == self._root_node or parent_node is None:
            return QModelIndex()

        return self.createIndex(parent_node.row(), 0, parent_node)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def add_item(self, parent_index, name):
        if parent_index is None:
            parent_index = QModelIndex()
            parent_node = self._root_node
            item_path = parent_node.name+"/"+name
        else:
            parent_node = parent_index.internalPointer()
            item_path = self.get_object_full_path(parent_index)+"/"+name
 
        print(f"[{self.__class__.__name__}] add item_path: " + item_path)

        if(self.oss_help.create_folder(item_path)):
            new_node = TreeNode(name, parent_node)
            self.beginInsertRows(parent_index, parent_node.child_count(), parent_node.child_count())
            parent_node.add_child(new_node)
            self.endInsertRows()
            print("create folder success")
        else:
            print("create folder failed")
            QMessageBox.warning(self, "提示", "create folder failed")
    def rename_item(self, index, new_name):
        if index.isValid():
            node = index.internalPointer()
            old_name_path = self.get_object_full_path(index)
            node.name = new_name
            new_name_path = self.get_object_full_path(index)
            print(f"[{self.__class__.__name__}] rename item_path: {old_name_path} to {new_name_path}")
            new_name = self.oss_help.rename(old_name_path,new_name_path)
            node.name = new_name
            print(new_name)
            self.dataChanged.emit(index, index, [Qt.DisplayRole])
    def removeRow(self, row, parent=QModelIndex()):
        return self.removeRows(row, 1, parent)

    def removeRows(self, row, count, parent=QModelIndex()):
        if not parent.isValid():
            parent_node = self._root_node
        else:
            parent_node = parent.internalPointer()

        self.beginRemoveRows(parent, row, row + count - 1)

        for i in range(count):
            parent_node.remove_child_by_row(row)

        self.endRemoveRows()

        return True
    def get_object_full_path(self,index):
        if index.isValid():
            node = index.internalPointer()
        parent_node = node.parent
        # get full path
        item_path = parent_node.name +"/"+node.name
        loop_parent_node = parent_node
        while(loop_parent_node.parent):
            loop_parent_node = loop_parent_node.parent
            item_path = loop_parent_node.name + "/" + item_path  
        return item_path
    def refresh(self):
        self.beginResetModel()
        self.get_model_data(self.oss_help.get_all_files(self.root_name), self._root_node)
        self.endResetModel()
    def search(self, query):
        """搜索树节点，返回匹配的 QModelIndex 列表。"""
        matching_indexes = []
        self._search_node(self._root_node, query, matching_indexes)
        return matching_indexes

    def _search_node(self, node, query, matching_indexes, parent_index=QModelIndex()):
        """递归搜索节点。"""
        index = None  # 初始化 index

        if query.lower() in node.name.lower():  # 忽略大小写匹配
            index = self.createIndex(node.row(), 0, node)
            matching_indexes.append(index)

        for i in range(node.child_count()):
            child_node = node.child(i)
            self._search_node(child_node, query, matching_indexes, index)




# 自定义 QTreeView 来支持右键菜单
class FileTreeView(QTreeView):
    copy_url_signal = Signal(str)  # 定义信号
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.setModel(model)
    def validMenu(self, index):
        node = index.internalPointer()
        if node is None:  # 检查 item 是否有效
            return  # 如果无效，则退出
        model = self.model().sourceModel()
        menu = QMenu(self)

        # Refresh
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(lambda: model.refresh())
        menu.addAction(refresh_action) 

        # New Folder
        if(node.is_folder):
            new_folder_action = QAction(f"New Folder ({node.name})", self)
            new_folder_action.triggered.connect(lambda: self.new_folder(index))
            menu.addAction(new_folder_action)

        # Rename
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self.rename_file(index))
        menu.addAction(rename_action)
        # Delete
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_node(index))
        menu.addAction(delete_action)
        # Cut
        cut_action = QAction("Cut", self)
        #TODO: 用cut + paste实现移动文件
        cut_action.triggered.connect(lambda: QMessageBox.information(self, "Cut", "TODO"))
        menu.addAction(cut_action)
        # Paste
        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(lambda: QMessageBox.information(self, "Paste", "TODO"))
        menu.addAction(paste_action)

        # Copy Oss Link
        if(node.is_folder is False):
            copy_url_action = QAction("Copy Oss Link", self)
            selct_path =model.get_object_full_path(index)
            copy_url_action.triggered.connect(lambda: self.copy_oss_url(index))
            menu.addAction(copy_url_action)
        return menu
    def invalidMenu(self, index):
        model = self.model().sourceModel()

        menu = QMenu(self)
        # New Folder
        new_folder_action = QAction("New Folder", self)
        new_folder_action.triggered.connect(lambda: self.new_folder(index))
        menu.addAction(new_folder_action)
        # Refresh
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(lambda: model.refresh())
        menu.addAction(refresh_action)
        return menu
    def additionalMenu(self, index,menu):
        return menu
    def contextMenuEvent(self, event):
        # 获取点击位置的索引
        index = self.indexAt(event.pos())
        # 使用了QSortFilterProxyModel，需要转换为源模型的索引,否则在访问node时会crash
        source_index = self.model().mapToSource(index)
        node = None
        if source_index.isValid():
            menu = self.validMenu(source_index)
            menu = self.additionalMenu(source_index,menu)
        else:
            menu = self.invalidMenu(source_index)
            menu = self.additionalMenu(source_index,menu)
        menu.exec(self.viewport().mapToGlobal(event.pos()))

    def new_folder(self, index):
        print(f"[{self.__class__.__name__}]create new folder")
        model = self.model().sourceModel()

        if index.isValid():
            node = index.internalPointer() 
            new_folder_name, ok = QInputDialog.getText(None, f"New Folder ({node.name}/)", "Folder name:")
            print(f"New folder name: {new_folder_name}")
            if ok and new_folder_name != "":
                model.add_item(index, new_folder_name)
        else: 
            new_folder_name, ok = QInputDialog.getText(None, f"New Folder", "Folder name:")
            if ok and new_folder_name != "":
                model.add_item(None, new_folder_name)
            else:
                QMessageBox.warning(self, "创建失败", "文件夹名不能为空")
    def rename_file(self,index):
        model = self.model().sourceModel()
        if index.isValid():
            node = index.internalPointer() 
            # item = model.itemFromIndex(index)
            new_text, ok = QInputDialog.getText(None, "Rename Item", "New name:", text=node.name)
            if ok and new_text != "":
                model.rename_item(index, new_text)
    def delete_node(self, index):
        model = self.model().sourceModel()
        parent_index = model.parent(index)
        model_path = model.get_object_full_path(index)
        if self.show_confirmation("Delete Confirmation", f"Delete {model_path}?"):
            # TODO：判断是否成功删除
            model.oss_help.delete(model_path)
            # 成功删除 Oss 文件后再删除节点
            model.removeRow(index.row(), parent_index)
        else:
            return        
    def rename_node(self,index):
        model = self.model().sourceModel()
        if index.isValid():
            item = index.internalPointer()
            new_text, ok = QInputDialog.getText(self, "Rename Item", "New name:", text=item.name)
            if ok and new_text:
                model.rename_item(index, new_text)
    def show_confirmation(self,title,text):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        result = msg_box.exec() # 显示消息框并获取用户选择的按钮
        if result == QMessageBox.Yes:
            return True
        else:
            return False
    def copy_oss_url(self,index):
        '''复制OSS链接'''
        # index = self.custom_tree_widget.currentIndex()
        model = self.model().sourceModel()
        if index.isValid():
            item = index.internalPointer()
            item_path = model.get_object_full_path(index)
            print(f"Copy {model.oss_help.oss_global_base_url}/{item_path} to clipboard")
            QApplication.clipboard().setText(f"{model.oss_help.oss_global_base_url}/{item_path}")
            self.copy_url_signal.emit("Copy url success")





