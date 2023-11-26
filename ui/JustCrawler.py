from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, \
    QWidget, QHBoxLayout, QTextEdit, QTextBrowser
from PyQt5.QtGui import QIcon, QPixmap
from qt_material import apply_stylesheet


class JustCrawlerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JustCrawler")
        self.setWindowIcon(QIcon('icon.png'))
        self.setFixedSize(800, 600)
        # add components
        self.layout = QVBoxLayout(self)

        self.h_layout = QHBoxLayout()
        # init everything
        self.pixmap = QPixmap('start.png')
        self.smaller_pixmap = self.pixmap.scaled(24, 24)  # 将图像调整为24*24的尺寸

        self.input_text_button = QPushButton(text='输入爬取网站')
        self.open_file_button = QPushButton(text='打开输入文件')
        self.select_save_path = QPushButton(text='选择生成路径')
        self.check_crawler_result = QPushButton(text='查看爬取结果')

        self.textBrowser = QTextBrowser()
        self.textEditor = QTextEdit()

        self.layout.addWidget()

    def on_button_click(self):
        # ... （其他代码）
        pass


if __name__ == '__main__':
    app = QApplication([])
    just_crawler = JustCrawlerWindow()
    apply_stylesheet(app, theme='light_purple_500.xml', invert_secondary=True)
    just_crawler.show()
    app.exec_()
