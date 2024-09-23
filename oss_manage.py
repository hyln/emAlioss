from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide6.QtWidgets import QWidget, QTreeView, QLabel, QMenu, QInputDialog,QMessageBox,QAbstractItemView,QHBoxLayout
from PySide6.QtGui import QAction,QPixmap
from oss_utils import OssUtils

class TreeNode:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def child(self, row):
        return self.children[row]

    def child_count(self):
        return len(self.children)

    def row(self):
        if self.parent:
            return self.parent.children.index(self)
        return 0

    def column_count(self):
        return 1


class OSSModel(QAbstractItemModel):
    def __init__(self,oss_utils:OssUtils,prefix, parent=None):
        super().__init__(parent)
        self.root = TreeNode(prefix)
        self.oss_prefix = prefix

        self.oss_utils = oss_utils
        data = self.oss_utils.get_all_files(self.oss_prefix)
        self.setup_model_data(data, self.root)

    def setup_model_data(self, data, parent):
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
        if parent.isValid():
            node = parent.internalPointer()
            return node.child_count()
        return self.root.child_count()

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            node = parent.internalPointer()
            return node.column_count()
        return self.root.column_count()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole:
            return node.name
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.oss_prefix
        return None

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parent_node = self.root
        else:
            parent_node = parent.internalPointer()
        child_node = parent_node.child(row)
        if child_node:
            return self.createIndex(row, column, child_node)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        parent_node = node.parent
        if parent_node == self.root or not parent_node:
            return QModelIndex()
        return self.createIndex(parent_node.row(), 0, parent_node)

    def add_item(self, parent_index, name):
        parent_node = parent_index.internalPointer() if parent_index.isValid() else self.root

        # get full path
        item_path = parent_node.name +"/"+name
        loop_parent_node = parent_node
        while(loop_parent_node.parent):
            loop_parent_node = loop_parent_node.parent
            item_path = loop_parent_node.name + "/" + item_path  
        print("[ossManage]add item_path: " + item_path)

        if(self.oss_utils.create_folder(item_path)):
            new_node = TreeNode(name, parent_node)
            self.beginInsertRows(parent_index, parent_node.child_count(), parent_node.child_count())
            parent_node.add_child(new_node)
            self.endInsertRows()
            print("create folder success")
        else:
            print("create folder failed")
            QMessageBox.warning(self, "提示", "create folder failed")

    def remove_item(self, index):
        node = index.internalPointer()
        parent_node = node.parent

        # get full path
        item_path = parent_node.name +"/"+node.name
        loop_parent_node = parent_node
        while(loop_parent_node.parent):
            loop_parent_node = loop_parent_node.parent
            item_path = loop_parent_node.name + "/" + item_path  
        print("[ossManage]remove item_path: " + item_path)

        self.beginRemoveRows(index.parent(), node.row(), node.row())
        parent_node.remove_child(node)
        self.oss_utils.delete(item_path,self.oss_prefix)
        self.endRemoveRows()

    def rename_item(self, index, new_name):
        if index.isValid():
            node = index.internalPointer()
            old_name_path = self.get_object_full_path(index)
            node.name = new_name
            new_name_path = self.get_object_full_path(index)
            new_name = self.oss_utils.rename(old_name_path,new_name_path)

            self.dataChanged.emit(index, index, [Qt.DisplayRole])
    def get_object_full_path(self,index):
        node = index.internalPointer()
        parent_node = node.parent
        # get full path
        item_path = parent_node.name +"/"+node.name
        loop_parent_node = parent_node
        while(loop_parent_node.parent):
            loop_parent_node = loop_parent_node.parent
            item_path = loop_parent_node.name + "/" + item_path  
        return item_path
            

class OssTreeView(QTreeView):
    def __init__(self,oss_utils:OssUtils,prefix):
        ''''''
        super().__init__()
        self.oss_utils = oss_utils
        self.model = OSSModel(oss_utils,prefix)
        self.setModel(self.model)
        # 为树视图设置右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.setSelectionMode(QAbstractItemView.SingleSelection)

        # self.doubleClicked.connect(self.open_folder)
        # self.setHeaderHidden(True)

        # TODO: Enable drag and drop
        # Enable drag and drop
        # self.setDragEnabled(True)
        # self.setAcceptDrops(True)
        # self.setDragDropMode(QTreeView.InternalMove)

