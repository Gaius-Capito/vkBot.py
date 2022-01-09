import datetime
import time
import aiohttp
import asyncio
import requests
import sqlite3
import threading
from bs4 import BeautifulSoup

class Mosconsv:

    def __init__(self):
        self.today = datetime.date.today()
        self.url = f'https://www.mosconsv.ru/afisha/{self.today}'
        self.__host = self.url.replace('//', '/').split('/')[1].replace('www.', '')

    def __get_links(self):  # Функция получает url за 1 месяц, которые будут запрошены
        today = datetime.date.today()  # в следующих методах
        daily_links = []
        for _ in range(30):
            daily_html = f'https://www.mosconsv.ru/afisha/{today}'
            daily_links.append(daily_html)
            today += datetime.timedelta(days=1)
        return daily_links

    async def __get_html(self):  # http запросы за каждые 30 дней для получения url всех концертов
        async with aiohttp.ClientSession() as session:
            html = []
            for i in self.__get_links():
                response = await session.get(i)
                html.append(await response.text())
        return html

    def run_async(self):
        thread1 = threading.Thread(target=self.start_async)
        thread1.start()
        print('!!!&!')

    def start_async(self):
        a = asyncio.run(self.__get_html())
        self.var = a
        self.run_async_1()

    def get_concerts_links(self):
        links_to_concerts_per_month = []
        for i in self.var:
            soup = BeautifulSoup(i, 'html.parser')
            every_concerts_data = soup.find_all('div', class_='row hall-block')
            concerts_links = []
            for j in every_concerts_data:
                concerts_links.append(self.__host + j.find('a').get('href'))
            links_to_concerts_per_month.append(concerts_links)
        return links_to_concerts_per_month

    async def get_concert_html(self):
        async with aiohttp.ClientSession() as session:
            html = []
            for i in self.get_concerts_links():
                for j in i:
                    response = await session.get(f'http://{j}')
                    html.append(await response.text())
        return html

    def run_async_1(self):
        a = asyncio.run(self.get_concert_html())
        self.var1 = a
        self.write_result_db()

    def __create_db(self):
        with sqlite3.connect('concerts.db') as connection:
            table = """CREATE TABLE IF NOT EXISTS `concerts`(
            date VARCHAR(75) NOT NULL,
            place VARCHAR(100) NOT NULL,
            program TEXT NOT NULL,
            link TEXT NOT NULL
            )"""
            cursor = connection.cursor()
            print("База данных подключена к SQLite")
            cursor.execute(table)
            connection.commit()
            print("Таблица SQLite создана")

    def write_result_db(self):
        self.__prepearing_db()
        for date, place, program, link in self.get_final_res():
            with sqlite3.connect('concerts.db') as connection:
                cursor = connection.cursor()
                cursor.execute("""INSERT INTO `concerts` (date, place, program, link) 
                VALUES (?, ?, ?, ?)""", (date, place, program, link))
                connection.commit()

    def __prepearing_db(self):
        self.__create_db()
        with sqlite3.connect('concerts.db') as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM `concerts`")
            connection.commit()
            print('База данных очищена')

    def get_final_res(self):
        for page in self.var1:
            soup = BeautifulSoup(page, 'html.parser')
            date = soup.find('div', class_='col-sm-3 afisha-date').get_text()
            time_ = soup.find('div', class_='time').get_text()
            place = soup.find('div', class_='col-sm-6 afisha-hall').get_text()
            program = soup.find('div', itemtype="https://schema.org/CreativeWork").get_text()
            link = soup.find(property='og:url').get('content')
            date = date.replace('\n', ' ').strip().lower() + ', начало в ' + time_
            yield date, place, program, link


class Meloman:

    def __init__(self):
        self.url = 'https://meloman.ru/calendar/'
        self.__host = self.url.replace('//', '/').split('/')[1].replace('www.', '')

    def __get_html(self):
        page = requests.get(self.url)
        print(page.status_code)
        return page

    def get_all_links(self):
        html = self.__get_html().text
        soup = BeautifulSoup(html, 'html.parser')
        concerts = soup.find_all('li', class_='hall-entry pseudo-link external initially-shown')
        links = []
        for i in concerts:
            links.append(f"https://{self.__host}{i['data-link']}")
        return links

    async def get_concerts_data(self):
        async with aiohttp.ClientSession() as session:
            html = []
            for i in self.get_all_links():
                response = await session.get(i)
                html.append(await response.text())
        return html

    def run_async_2(self):
        thread2 = threading.Thread(target=self.start_async)
        thread2.start()

    def start_async(self):
        a = asyncio.run(self.get_concerts_data())
        self.var3 = a
        self.write_result_db()

    def get_final_res(self):
        for i in self.var3:
            soup = BeautifulSoup(i, 'html.parser')
            date = soup.find('p', class_='text size18').get_text().strip()
            place = soup.find('p', class_='text size18').find_next_sibling().get_text().strip()
            program = soup.find('div', class_='small-row align-left').find_next_sibling().get_text().strip()\
                .replace('\n', '').replace('  ', '')
            link = soup.find(property="og:url").get('content')
            yield date, place, program, link

    def write_result_db(self):
        time.sleep(90)
        for date, place, program, link in self.get_final_res():
            with sqlite3.connect('concerts.db') as connection:
                cursor = connection.cursor()
                cursor.execute("""INSERT INTO `concerts` (date, place, program, link) 
                VALUES (?, ?, ?, ?);""", (date, place, program, link))
                print('идет запись')
        connection.commit()

    def get_result_db(self, msg):
        print(msg)
        data = f'%{msg}%'
        with sqlite3.connect('concerts.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT `rowid`, `date`, `place`, `link` FROM `concerts` "
                           "WHERE `program` LIKE (?) ORDER BY `rowid`;", (data,))
            result = cursor.fetchall()
            print('get_result')
            return result

    def write_in_file(self, msg):
        print('write in file')
        with open('concerts_to_sent.txt', 'w') as file_object:
            file_object.write('Ссылки на концерты по Вашему запросу')
            for i in self.get_result_db(msg):
                file_object.write(f"\n\n{i[1].strip()}\nМесто: {i[2].replace(' ', ' ').strip()}\nссылка на концерт: {i[3].strip()}")
        print('finish writing')


def main():
    while True:
        m1 = Mosconsv()
        m1.run_async()
        m = Meloman()
        m.run_async_2()
        time.sleep(86400)

if __name__ == '__main__':
    main()