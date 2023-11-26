# test link:《葬送的芙莉莲》
# https://www.yhdmdm.com/tv/dm15979.html
# download file *.ts and connect them to *.mp4
import concurrent.futures
import json
import os
import re
import shutil
import requests
from bs4 import BeautifulSoup


class VideoDownloader:
    def __init__(self, target):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/72.0.3626.121 Safari/537.36'}
        self.target = target
        self.session = requests.Session()
        self.soup = None
        self.alldata = []
        self.ts_data = []
        self.absolute_path = None
        self.video_name = None

    def create_folder(self, name):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        new_folder_path = os.path.join(os.path.dirname(current_directory), 'video', name)
        os.makedirs(new_folder_path, exist_ok=True)
        return new_folder_path

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

    def get_video_name(self):
        is_state = self.get_contents_component(self.target)
        if is_state:
            self.video_name = self.soup.select_one('div.stui-content h1.title').get_text(strip=True)
            # create new folder /video
            self.absolute_path = self.create_folder(name=self.video_name)
            return True
        return False

    def get_crawl_list(self):
        links = self.soup.select('.stui-content__playlist.clearfix li')
        chapter_links = [
                {'chapter_name': str(link.a['title']), 'chapter_link': 'https://www.yhdmdm.com' + str(link.a['href'])}
                for link in links]
        return chapter_links

    def get_shared_link(self, chapter_links):
        for item in chapter_links:
            chapter_link = item['chapter_link']
            is_state = self.get_contents_component(chapter_link)
            if is_state:
                script_tag = self.soup.find('script', string=re.compile(r'var now="(.+)"'))
                if script_tag:
                    # RegEx
                    match = re.search(r'var now="([^"]+)"', script_tag.string)
                    if match:
                        now_value = match.group(1)
                        item['chapter_shared_link'] = now_value
        self.alldata = chapter_links

    def get_m3u8_links(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_directory, 'm3u8_links.txt')
        # check it
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.readlines()
            # update new data
            if not any(line.strip() for line in content):
                return False
            else:
                self.Get_alldata()
                min_length = min(len(content), len(self.alldata))
                for per_item, item in zip(self.alldata[:min_length], content):
                    stripped_item = item.strip()
                    if stripped_item:  # \n -> '' not save
                        per_item['m3u8_link'] = stripped_item
                self.datalog(self.alldata, 'real-m3u8-links.json')
                return content
        else:
            with open(file_path, 'w', encoding='utf-8'):
                pass
            return False

    def datalog(self, dist_data, json_file_path):
        json_folder_path = os.path.join(self.absolute_path, 'json')
        os.makedirs(json_folder_path, exist_ok=True)

        json_file_path = os.path.join(json_folder_path, json_file_path)
        json_file_path = os.path.normpath(json_file_path)

        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(dist_data, json_file, ensure_ascii=False, indent=4)

    def Get_alldata(self):
        json_file_path = os.path.join(self.absolute_path, r'json\\shared-link-for-network.json')
        with open(json_file_path, 'r', encoding='utf-8') as file:
            self.alldata = json.load(file)

    def PreWork(self):
        # .json exist not enter this part
        is_existed = self.get_video_name()
        json_file_path = os.path.join(self.absolute_path, r'json\\shared-link-for-network.json')
        if is_existed and not os.path.exists(json_file_path):
            chapter_list = self.get_crawl_list()
            self.get_shared_link(chapter_list)
            self.datalog(self.alldata, 'shared-link-for-network.json')

    def download_video(self, m3u8_links):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.download_single_video, link.copy()) for link in m3u8_links]
            concurrent.futures.wait(futures)
            for _ in futures:
                try:
                    pass
                except Exception as e:
                    print(f"Error in download: {e}")

    def download_single_video(self, link):
        if len(link.items()) > 3:
            m3u8_link = link['m3u8_link']
            mp4_name = self.video_name + link['chapter_name'] + '.mp4'
            download_links, path_names = self.preHandle_m3u8_link(web=m3u8_link)
            temp_folder_path = self.downloader(download_links=download_links, path_names=path_names)
            temp_obj = {'mp4_name': mp4_name, 'temp_folder_path': temp_folder_path, 'path_names': path_names}
            self.ts_data.append(temp_obj)

    def preHandle_m3u8_link(self, web):
        # get all m3u8 complete links
        pattern = re.compile(r'\b\w+\.ts\b')
        last_slash_index = web.rfind('/')
        prefix = web[:last_slash_index + 1]
        response = self.session.get(web, headers=self.headers)
        if response.status_code == 200:
            init_contents = response.text
            # filter *.ts string and add prefix to it
            path_names = pattern.findall(init_contents)
            ts_list = [(prefix + ts) for ts in path_names]
            return ts_list, path_names

    def downloader(self, download_links, path_names):
        temp_folder_path = os.path.join(self.absolute_path, 'temp')
        os.makedirs(temp_folder_path, exist_ok=True)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # as_completed
            futures = [executor.submit(self.download_ts, link, name, temp_folder_path) for link, name in
                       zip(download_links, path_names)]
            for _ in concurrent.futures.as_completed(futures):
                try:
                    pass
                except Exception as e:
                    print(f"Error in downloading ts file: {e}")
        return temp_folder_path

    def download_ts(self, link, name, temp_folder_path):
        ts_path = os.path.join(temp_folder_path, name)
        try:
            response = self.session.get(link, headers=self.headers)
            response.raise_for_status()
            with open(ts_path, 'wb') as file:
                file.write(response.content)
            print(f'来自 {link} 的文件 {name} 下载完成!')
        except requests.exceptions.RequestException as e:
            print(f"Error in downloading ts file {name}: {e}")

    def connector(self):
        if self.ts_data:
            temp_folder_path = ''
            for ts in self.ts_data:
                # ts_dict = {'mp4_name': mp4_name, 'temp_folder_path': temp_folder_path, 'path_names': path_names}
                ts_path_list = ts['path_names']
                temp_folder_path = ts['temp_folder_path']
                mp4_name = ts['mp4_name']
                self.connection(ts_path_list, mp4_name, temp_folder_path)
            self.datalog(self.ts_data, 'per-video-ts-data.json')
            # remove all things in this folder
            shutil.rmtree(temp_folder_path)
            print('视频文件下载完成!')
        else:
            print('无文件拼接数据')

    def connection(self, ts_path_list, mp4_name, temp_folder_path):
        # connection demo
        mp4_path = os.path.join(self.absolute_path, mp4_name)
        open(mp4_path, 'w').close()
        with open(mp4_path, 'ab') as connect_obj:  # append binary
            for ts in ts_path_list:
                ts_path = os.path.join(temp_folder_path, ts)
                with open(ts_path, 'rb') as temporary_obj:  # read binary
                    connect_obj.write(temporary_obj.read())
                os.remove(ts_path)
        print(f'{mp4_name}文件拼接完成!')

    def Launcher(self):
        self.download_video(m3u8_links=self.alldata)
        self.connector()


if __name__ == '__main__':
    target = 'https://www.yhdmdm.com/tv/dm15979.html'
    video_crawler = VideoDownloader(target=target)
    video_crawler.PreWork()
    isOk = video_crawler.get_m3u8_links()
    if not isOk:
        print('Check the shared-link-for-network.json in json folder.')
        print('Request the shared_link and follow the next step.')
        print('Open your browser and check real m3u8 links with Shift + Ctrl + I, '
              'then put them into m3u8_links.txt in order.')
    else:
        video_crawler.Launcher()


