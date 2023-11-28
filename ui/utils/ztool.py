# Auxiliary class some tools here
import os
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton


class Auxiliary:
    def __init__(self):
        self.flag = False

    def remove_string_list_tags(self, string_list):
        # return value: list
        # parameter: string_list -> list/string
        # replace ' ', ';', ',' with '\n' and then split using '\n', remove repeated elements
        if isinstance(string_list, (list, str)):
            split_list = []
            if isinstance(string_list, list):
                split_list = [item.replace(' ', '\n').replace(';', '\n').replace(',', '\n').split('\n') for item in
                              string_list]
                flattened_list = [segment.strip() for segments in split_list for segment in segments if segment.strip()]
                cleaned_list = list(set([item.replace(',', '').replace(';', '') for item in flattened_list]))
            elif isinstance(string_list, str):
                split_list = string_list.replace(' ', '\n').replace(';', '\n').replace(',', '\n').split('\n')
                flattened_list = [item.strip() for item in split_list if item.strip()]
                cleaned_list = list(set(flattened_list))
            else:
                return split_list
        else:
            cleaned_list = []
        return cleaned_list

    def log_generator(self, string_item, log_path, log_name):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_name = f'{log_name}_{timestamp}.log'
        log_path = os.path.normpath(os.path.join(log_path, log_name))
        with open(log_path, 'w') as file:
            if isinstance(string_item, str):
                file.write(string_item)
            elif isinstance(string_item, list):
                file.writelines(string_item)
        return log_path


# 自定义保存对话框
class SaveMessage(QDialog):
    # 保存信号
    save = QtCore.pyqtSignal()

    def __init__(self, icon, parent=None):
        super().__init__(parent)
        self.setWindowTitle("提示")
        self.setWindowIcon(icon)
        self.setFixedSize(350, 100)  # 设置对话框的固定大小
        v_layout = QVBoxLayout(self)
        h_layout = QHBoxLayout()
        label = QLabel("是否保存当前文件？")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        label.setAlignment(Qt.AlignCenter)  # 将文本水平和垂直居中显示
        v_layout.addWidget(label)
        label.setWordWrap(True)  # 设置标签的文本可换行
        button1 = QPushButton('保存文件')
        button2 = QPushButton('取消保存')
        button1.clicked.connect(self.save_file)
        button2.clicked.connect(self.reject)
        h_layout.addWidget(button1)
        h_layout.addWidget(button2)
        v_layout.addLayout(h_layout)

    def save_file(self):
        self.save.emit()
        self.accept()
