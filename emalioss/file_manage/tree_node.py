import os
# 树节点类
# @oss_url: item oss path
# @oss_type: item type, file or folder
class TreeNode:
    def __init__(self, name, parent=None, is_folder=False):
        self.name = name
        if is_folder is  False:
            self.is_folder = self.is_directory(name)
        else:
            self.is_folder = is_folder
        self.parent = parent
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def remove_child_by_row(self, row):
        if 0 <= row < len(self.children):
            del self.children[row]

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
    def is_directory(self,path:str):
        """
        判断path是否是文件夹,依据是否有后缀名,路径可以时局部路径或者全局路径
        """
        return not os.path.splitext(path)[1]  # 如果没有后缀名，则是文件夹
