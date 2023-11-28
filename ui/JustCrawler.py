from os.path import split

from PyQt5.QtCore import QFile, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, \
    QWidget, QHBoxLayout, QTextEdit, QTextBrowser, QLineEdit, QLabel, QTabWidget, QFrame, QFileDialog, QMessageBox
from qt_material import apply_stylesheet

from utils.comics_crawler import ComicsCrawlerForCMH5, PDF_generator
from utils.video_crawler import VideoCrawlerForYHDMDM
from utils.ztool import Auxiliary


class JustCrawlerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JustCrawler")
        self.setWindowIcon(QIcon('img/icon.png'))
        self.setFixedSize(1048, 800)
        # mainframe
        main_frame = QFrame()
        main_layout = QVBoxLayout(main_frame)
        # create TabWidget
        self.tabWidget = QTabWidget()
        # set banner
        pixmap = QPixmap('img/start.png')
        banner = QLabel()
        banner.setPixmap(pixmap)
        banner.setScaledContents(True)
        # set tips
        tips_label = QLabel("Tips: 这是一个JustCrawler爬虫,请输入 https://www.cmh5.com 链接爬取漫画, https://www.yhdmdm.com 链接爬取视频o("
                            "QWQ)o")
        tips_label.setStyleSheet("color: red")
        tips_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # copy enable
        # log button
        h_layout = QHBoxLayout()
        self.log_button = QPushButton('生成日志')
        h_layout.addWidget(tips_label)
        h_layout.addWidget(self.log_button)
        # For CartoonCrawler Page
        # first create the container
        container = QWidget()
        layout = QVBoxLayout(container)
        # we need three QHBoxLayout components
        self.h_layout_1 = QHBoxLayout()
        self.h_layout_2 = QHBoxLayout()
        self.h_layout_3 = QHBoxLayout()
        # init everything
        self.comics_run = QPushButton(text='RUN')
        self.open_file_button = QPushButton(text='打开输入文件')
        self.select_save_path = QPushButton(text='选择生成路径')
        self.check_crawler_result = QPushButton(text='查看爬取结果')

        self.textBrowser = QTextBrowser()
        self.textEditor_input = QTextEdit()
        self.lineEditor_show = QLineEdit()
        self.lineEditor_show.setReadOnly(True)
        self.textEditor_input.setPlaceholderText('请输入爬取漫画链接')
        self.textBrowser.setPlaceholderText('~~~爬虫活动日志~~~')
        # for 1: textEditor + button
        self.h_layout_1.addWidget(self.textEditor_input)
        self.h_layout_1.addWidget(self.comics_run)
        # for 2: lineEditor + button
        self.h_layout_2.addWidget(self.lineEditor_show)
        self.h_layout_2.addWidget(self.open_file_button)
        # for 3: two buttons
        self.h_layout_3.addWidget(self.select_save_path)
        self.h_layout_3.addWidget(self.check_crawler_result)

        layout.addLayout(self.h_layout_1)
        layout.addLayout(self.h_layout_2)
        layout.addLayout(self.h_layout_3)
        layout.addWidget(self.textBrowser)
        # layout.addWidget(tips_label)
        # For VideoCrawler
        container_ = QWidget()
        layout_ = QVBoxLayout(container_)
        self.textBrowser_ = QTextBrowser()
        self.textEditor_input_web = QTextEdit()
        self.textEditor_input_m3u8 = QTextEdit()
        self.lineEditor_show_ = QLineEdit()
        self.lineEditor_show_.setReadOnly(True)
        self.textEditor_input_web.setPlaceholderText('请输入爬取视频链接')
        self.textEditor_input_m3u8.setPlaceholderText('请输入对应的m3u8链接')
        self.textBrowser_.setPlaceholderText('~~~爬虫活动日志~~~')
        # string input / file input
        self.h_layout_4 = QHBoxLayout()
        self.h_layout_5 = QHBoxLayout()
        self.h_layout_6 = QHBoxLayout()

        self.video_run = QPushButton(text='RUN')
        self.open_m3u8_file = QPushButton(text='打开输入m3u8链接文件')
        self.select_save_path_ = QPushButton(text='选择生成路径')
        self.check_crawler_result_ = QPushButton(text='查看爬取结果')

        # for 4: textEditor + button
        self.h_layout_4.addWidget(self.textEditor_input_web)
        self.h_layout_4.addWidget(self.video_run)
        # for 5: lineEditor + button
        self.h_layout_5.addWidget(self.lineEditor_show_)
        self.h_layout_5.addWidget(self.open_m3u8_file)
        # for 6: 2 buttons
        self.h_layout_6.addWidget(self.select_save_path_)
        self.h_layout_6.addWidget(self.check_crawler_result_)

        layout_.addLayout(self.h_layout_4)
        layout_.addWidget(self.textEditor_input_m3u8)
        layout_.addLayout(self.h_layout_5)
        layout_.addLayout(self.h_layout_6)
        layout_.addWidget(self.textBrowser_)

        self.tabWidget.addTab(container, "CartoonCrawler")
        self.tabWidget.addTab(container_, "VideoCrawler")
        # set main layout
        main_layout.addWidget(banner)
        main_layout.addWidget(self.tabWidget)
        main_layout.addLayout(h_layout)

        # global variable
        # self.comics_string = None
        # self.comics_input_path = []
        self.comics_save_path = None

        # self.video_string = None
        # self.video_input_path = []
        # self.video_m3u8_path = []
        self.video_save_path = None

        self.tool = Auxiliary()

        self.setCentralWidget(main_frame)
        self.function_connect()

    def function_connect(self):
        # For comics crawler
        self.comics_run.clicked.connect(self.comics_RUN)
        self.open_file_button.clicked.connect(self.comics_openFile)
        self.select_save_path.clicked.connect(self.comics_saveFile)
        self.check_crawler_result.clicked.connect(self.check_crawler_result_FUN)
        # For video crawler
        self.video_run.clicked.connect(self.video_RUN)
        self.open_m3u8_file.clicked.connect(self.video_openFile)
        self.select_save_path_.clicked.connect(self.video_saveFile)
        self.check_crawler_result_.clicked.connect(self.check_crawler_result_FUN)
        # For log generator
        self.log_button.clicked.connect(self.log_generator)
        # others

    def comics_RUN(self):
        # Main codes
        pass

    def video_RUN(self):
        pass

    def open_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择输入文件", "", "All Files (*);;Text Files (*.txt)")
        return file_path

    def select_save_path_FUN(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择保存路径", "")
        return folder_path

    def check_crawler_result_FUN(self):
        pass

    def log_generator(self):
        logging = None
        if self.getTabStatus() == 'CartoonCrawler':
            logging = self.textBrowser.toPlainText()
        elif self.getTabStatus() == 'VideoCrawler':
            logging = self.textBrowser_.toPlainText()
        if logging:
            # 创建新文件对话框
            directory = QFileDialog.getExistingDirectory(self, "选择文件夹", "")
            if directory:
                file_dialog = QFileDialog(self)
                file_dialog.setWindowTitle("新建文件")
                file_dialog.setNameFilters(["Log Files (*.log)", "Text Files (*.txt)"])
                file_dialog.setDirectory(directory)
                file_dialog.setLabelText(QFileDialog.Accept, "保存")
                file_dialog.setLabelText(QFileDialog.Reject, "取消")

                if file_dialog.exec_() == QFileDialog.Accepted:
                    log_path = file_dialog.selectedFiles()[0]
                    _, log_name = split(log_path)
                    log_path = self.tool.log_generator(logging, log_name, log_path)
                    print('success')
                else:
                    print('failed')
        else:
            print('日志无内容')

    def getTabStatus(self):
        current_tab_index = self.tabWidget.currentIndex()
        current_tab_name = self.tabWidget.tabText(current_tab_index)
        return current_tab_name

    def comics_openFile(self):
        comics_input_path = self.open_input_file()
        self.lineEditor_show.setText(comics_input_path)

    def video_openFile(self):
        video_input_path = self.open_input_file()
        self.lineEditor_show_.setText(video_input_path)

    def comics_saveFile(self):
        self.comics_save_path = self.select_save_path_FUN()

    def video_saveFile(self):
        self.video_save_path = self.select_save_path_FUN()

    # noinspection DuplicatedCode
    def HandleInputWeb(self):
        if self.getTabStatus() == 'CartoonCrawler':
            input_string = self.textEditor_input.toPlainText()
            input_file = self.lineEditor_show.text()

            if input_string and input_file:
                input_string = self.tool.remove_string_list_tags(input_string)
                with open(input_file, 'r') as file:
                    input_content = file.read()
                input_content = self.tool.remove_string_list_tags(input_content)
                merge_list = input_string + input_content
                merge_list = list(set(merge_list))
                return merge_list

            elif input_string and not input_file:
                input_string = self.tool.remove_string_list_tags(input_string)
                return input_string

            elif input_file and not input_string:
                with open(input_file, 'r') as file:
                    input_content = file.read()
                input_content = self.tool.remove_string_list_tags(input_content)
                return input_content

            else:
                return False
        else:
            input_string = self.textEditor_input_web.toPlainText()

            if input_string:
                input_string = self.tool.remove_string_list_tags(input_string)
                return input_string
            else:
                return False

    def HandleInputM3U8(self):
        if self.getTabStatus() == 'VideoCrawler':
            m3u8_string = self.textEditor_input_m3u8.toPlainText()
            m3u8_file = self.lineEditor_show_.text()

            if m3u8_string and m3u8_file:
                m3u8_string = self.tool.remove_string_list_tags(m3u8_string)
                with open(m3u8_file, 'r') as file:
                    m3u8_content = file.read()
                m3u8_content = self.tool.remove_string_list_tags(m3u8_content)
                merge_list = m3u8_string + m3u8_content
                merge_list = list(set(merge_list))
                return merge_list

            elif m3u8_string and not m3u8_file:
                input_string = self.tool.remove_string_list_tags(m3u8_string)
                return input_string

            elif m3u8_file and not m3u8_string:
                with open(m3u8_file, 'r') as file:
                    m3u8_content = file.read()
                m3u8_content = self.tool.remove_string_list_tags(m3u8_content)
                return m3u8_content

            else:
                return False
        else:
            return False


if __name__ == '__main__':
    app = QApplication([])
    just_crawler = JustCrawlerWindow()
    apply_stylesheet(app, theme='light_purple_500.xml', invert_secondary=True)
    just_crawler.show()
    app.exec_()
