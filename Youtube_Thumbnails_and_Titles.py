import time
import os
import sys
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from konlpy.tag import Okt
from collections import defaultdict


def get_image_title(url, word_dict):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    service = ChromeService(executable_path='./chromedriver')

    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)

    driver.get(url)
    video_list = list()
    idx = 1
    while idx <= 100:
        try:

            img_xpath = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-shelf-renderer/div[1]/div[2]/ytd-expanded-shelf-contents-renderer/div/ytd-video-renderer[' + str(
                idx) + ']/div[1]/ytd-thumbnail/a/yt-img-shadow/img'
            title_xpath = '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-shelf-renderer/div[1]/div[2]/ytd-expanded-shelf-contents-renderer/div/ytd-video-renderer[' + str(
                idx) + ']/div[1]/div/div[1]/div/h3/a/yt-formatted-string'
            img = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, img_xpath)))
            if img is None:
                print(idx, 'img is not loaded.')

            if idx % 8 == 0:
                driver.execute_script('window.scrollBy(0, 1080);')
                time.sleep(2)
                driver.execute_script('window.scrollBy(0, 1080);')
                time.sleep(2)
                driver.execute_script('window.scrollBy(0, 1080);')
                time.sleep(2)

            image = driver.find_element(By.XPATH, img_xpath)
            title = driver.find_element(By.XPATH, title_xpath)
            img_url = image.get_attribute('src')
            video_list.append(img_url.split('/')[4])
            print(idx, title.text, img_url)
            idx += 1

            okt = Okt()
            for word, _ in okt.pos(title.text):
                word_dict[word.upper()] += 1

        except Exception as e:
            print()
            print(e)
            break
    return video_list


if __name__ == '__main__':
    save_mode = False
    i = 1
    if len(sys.argv) >= 2:
        i = int(sys.argv[1])
    if len(sys.argv) == 3 and sys.argv[2] == "1":
        save_mode = True

    url_music = 'https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D'
    url_game = 'https://www.youtube.com/feed/trending?bp=4gIcGhpnYW1pbmdfY29ycHVzX21vc3RfcG9wdWxhcg%3D%3D'
    url_movie = 'https://www.youtube.com/feed/trending?bp=4gIKGgh0cmFpbGVycw%3D%3D'

    word_dict = defaultdict(int)

    videos = []
    videos += get_image_title(url_music, word_dict)
    videos += get_image_title(url_game, word_dict)
    videos += get_image_title(url_movie, word_dict)

    for video_path in videos:
        os.system("curl https://i.ytimg.com/vi/" + video_path +
                  "/maxresdefault.jpg > " + str(i) + ".jpeg")
        i += 1

    sorted_dict = sorted(
        word_dict.items(), key=lambda item: item[1], reverse=True)
    print(sorted_dict)

    if save_mode:
        f = open("word_dict.csv", "r")
        data = csv.reader(f)
        for row in data:
            word_dict[row[0].upper()] += int(row[1])
        f.close()

        sorted_dict = sorted(
            word_dict.items(), key=lambda item: item[1], reverse=True)
        print(sorted_dict)

        f = open("word_dict.csv", "w")
        wr = csv.writer(f)
        for word, num in sorted_dict:
            wr.writerow([word, num])
        f.close()
