import requests
import time
import os
from bs4 import BeautifulSoup
from data_base import DataBase

def page_parsing(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    page = soup.find_all("article", class_="story")
    return page

def get_anime_info(anime):
    inf = anime.find('div', class_='story_infa')
    rat = anime.find('div', class_='div1')
    a = anime.find('a', href=True)
    dt_tag = inf.find('dt', string="Категорія:")
    ctgs = dt_tag.find_next_sibling(string=True).strip()

    name = anime.find('h2').text.strip()
    link = a['href']
    year= inf.find('a').text.strip()

    category = ctgs
    rating = rat.find('span').text.strip()
    description = anime.find('div', class_='story_c_text').text.strip()
    date = anime.find('span', class_="story_date")
    update_date = '{} {}'.format(date.find('sup').text, date.find('sub').text)
    return name, link, year, category, rating, update_date, description

def get_anime_pic(anime_url):
    response = requests.get(anime_url)
    soup = BeautifulSoup(response.text, "html.parser")
    anime = soup.find("article", class_="story")
    pic = anime.find('img', src=True)
    pic_url = 'https://anitube.in.ua/' + pic['src']
    return pic_url

def make_db(url_1):
    url = url_1
    i = 1
    while i <= 190:
        print(i)
        page = page_parsing(url)
        for anime in page:
            name, link, year, category, rating, update_date, description = get_anime_info(anime)
            db_line = Anime.insert_data(name, link, year, category, rating, update_date, description)
        i += 1
        url = url_1 + 'page/{}/'.format(i)
        time.sleep(2)

url_1 = 'https://anitube.in.ua/anime/'
if not os.path.exists('Anime.db'):
    Anime = DataBase()
    web.make_db(url_1)
else:
    print("data base already exists")













