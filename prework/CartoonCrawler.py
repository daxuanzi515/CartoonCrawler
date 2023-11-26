import os.path
import requests
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
from PIL import Image
import json
class CartoonCrawlerForCMH5:
    def __init__(self, target):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}
        self.target = target
        self.session = requests.Session()
        self.soup = None
        self.alldata = {}
        self.absolute_path = None
        self.comic_name = None

    def get_contents_component(self, web):
        # update soup and init_content to avoid repeated works
        if web:
            response = self.session.get(web, headers=self.headers)
            if response.status_code == 200:
                init_content = response.text
                if init_content is None or []:
                    return False
                self.soup = BeautifulSoup(init_content, 'html.parser')
                return True
        return False

    def get_crawl_list(self):
        is_state = self.get_contents_component(self.target)
        # get crawl list
        if is_state:
            self.comic_name = self.soup.find('p', class_='comic-title j-comic-title').get_text(strip=True)
            links = self.soup.find_all('a', class_='j-chapter-link')
            chapter_links = [{'chapter_name': link.get_text(strip=True), 'chapter_link': 'https://www.cmh5.com' + str(link.get('href'))}
                             for link in links]
            return chapter_links
        return {}

    def get_chapter_src(self, target_link_dist):
        for item in target_link_dist:
            name, link = item['chapter_name'], item['chapter_link']
            is_state = self.get_contents_component(link)
            if is_state:
                img_tags = self.soup.find_all('img', class_='lazy-read')
                src_list = [str(img['data-original']) for img in img_tags]
                item['chapter_src_list'] = src_list
        self.alldata = target_link_dist

    def create_folder(self, name):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        new_folder_path = os.path.join(os.path.dirname(current_directory), 'results', name)
        os.makedirs(new_folder_path, exist_ok=True)
        return new_folder_path

    def downloader(self, img_url):
        response = self.session.get(img_url, headers=self.headers)
        if response.status_code == 200:
            return response.content
        return None

    def download_img(self):
        # download and rename them
        # create folders like: target_name/chapter_name/img_name...
        src_path_data = {}
        if self.alldata and self.target:
            self.absolute_path = self.create_folder(self.comic_name)
            self.datalog(self.alldata,'crawl-data-set.json')

            img_folder_path = os.path.join(self.absolute_path, 'img')
            os.makedirs(img_folder_path, exist_ok=True)
            img_folder_path = os.path.normpath(img_folder_path)

            for item in self.alldata:
                chapter_name = item['chapter_name']
                chapter_src_list = item['chapter_src_list']
                chapter_src_path = []
                for idx, per_src in enumerate(chapter_src_list):
                    chapter_folder = os.path.join(img_folder_path,chapter_name)
                    os.makedirs(chapter_folder, exist_ok=True)
                    img_data = self.downloader(per_src)
                    img_name = f'{idx+1}.jpg'
                    img_path = os.path.join(chapter_folder, img_name)
                    chapter_src_path.append(img_path)
                    with open(img_path, 'wb') as img_file:
                        img_file.write(img_data)
                    print('{}的{}张图片下载完成!'.format(chapter_name, idx+1))
                src_path_data[chapter_name] = chapter_src_path
            return src_path_data
        return False

    def datalog(self, dist_data, json_file_path):
        json_folder_path = os.path.join(self.absolute_path, 'json')
        os.makedirs(json_folder_path, exist_ok=True)

        json_file_path = os.path.join(json_folder_path, json_file_path)
        json_file_path = os.path.normpath(json_file_path)

        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(dist_data, json_file, ensure_ascii=False, indent=4)

    def Launcher(self):
        chapter_list = self.get_crawl_list()
        if chapter_list:
            self.get_chapter_src(chapter_list)
            isok = self.download_img()
            if isok:
                self.datalog(isok, 'real-img-path.json')
                print("CartoonCrawlerForCMH5 爬取完成！")
                return isok
            else:
                print("爬取过程中意外失败...")
                return False

class PDF_generator:
    def __init__(self, output_path, src_path_data):
        self.output_path = output_path
        self.src_path_data = src_path_data

    def create_pdf(self, chapter_name, img_paths):
        # create a pdf
        pdf_folder_path = os.path.join(self.output_path, 'pdf')
        os.makedirs(pdf_folder_path, exist_ok=True)
        pdf_path = os.path.join(pdf_folder_path, f'{chapter_name}.pdf')
        pdf_path = os.path.normpath(pdf_path)

        c = canvas.Canvas(pdf_path, pagesize=(595, 842))  # A4 size
        # add images
        for img_path in img_paths:
            img = Image.open(img_path)
            img_width, img_height = img.size
            aspect_ratio = img_height / img_width
            page_width, page_height = 595, 842  # A4 size
            c.drawImage(img_path, 0, 0, width=page_width, height=page_width * aspect_ratio)
            c.showPage()
        c.save()
        return pdf_path

    def connect_img(self):
        #src_path_data = {chapter_name,chapter_src_paths} str:list->[]
        pdf_paths = []
        for chapter_name, chapter_src_paths in self.src_path_data.items():
            pdf_path = self.create_pdf(chapter_name, chapter_src_paths)
            pdf_paths.append(pdf_path)
        return pdf_paths

    def Launcher(self):
        print('PDF转换完成！')
        return self.connect_img()

def PreChecker():
    # get current absolute path
    # check target_web_list.txt already exist or not?
    # if not then create one, else check the content in it.
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, 'target_web_list.txt')
    # check it
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()
        return content
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            pass
        return []

if __name__ == '__main__':
    target_web_list = PreChecker()
    cleaned_list = [item.strip() for item in target_web_list if item.strip()]
    if target_web_list:
        for target in cleaned_list:
            cartoon_crawler = CartoonCrawlerForCMH5(target=target)
            is_success = cartoon_crawler.Launcher()
            if is_success:
                pdf_gen = PDF_generator(output_path=cartoon_crawler.absolute_path, src_path_data=is_success)
                pdf_paths = pdf_gen.Launcher()