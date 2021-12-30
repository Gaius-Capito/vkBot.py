import datetime
import aiohttp
import asyncio
import requests
import sqlite3
from bs4 import BeautifulSoup


class Mosconsv:

    def __init__(self):
        self.today = datetime.date.today()
        self.url = f'https://www.mosconsv.ru/afisha/{self.today}'
        self.__host = self.url.replace('//', '/').split('/')[1].replace('www.', '')

    def __get_html_links_for_month(self):  # Функция получает url за 1 месяц, которые будут запрошены
        today = datetime.date.today()  # в следующих методах
        daily_links = []
        for _ in range(30):
            daily_html = f'https://www.mosconsv.ru/afisha/{today}'
            daily_links.append(daily_html)
            today += datetime.timedelta(days=1)
        return daily_links

    async def __get_html_for_month(self):  # http запросы за каждые 30 дней для получения url всех концертов
        async with aiohttp.ClientSession() as session:
            html = []
            for i in self.__get_html_links_for_month():
                response = await session.get(i)
                html.append(await response.text())
        return html

    def run_async(self):
        a = asyncio.run(self.__get_html_for_month())
        self.var = a

    def get_concerts_links_for_one_month(self):
        links_to_concerts_per_month = []
        for i in self.var:
            soup = BeautifulSoup(i, 'html.parser')
            every_concerts_data = soup.find_all('div', class_='row hall-block')
            concerts_links = []
            for j in every_concerts_data:
                concerts_links.append(self.__host + j.find('a').get('href'))
            links_to_concerts_per_month.append(concerts_links)
        return links_to_concerts_per_month

    async def get_concert_html_for_one_month(self):
        async with aiohttp.ClientSession() as session:
            html = []
            for i in self.get_concerts_links_for_one_month():
                for j in i:
                    response = await session.get(f'http://{j}')
                    html.append(await response.text())
        return html

    def run_async_1(self):
        a = asyncio.run(self.get_concert_html_for_one_month())
        self.var1 = a

    def create_db(self):
        with sqlite3.connect('concerts.db') as connection:
            table = """CREATE TABLE IF NOT EXISTS `concerts`(
            date VARCHAR(75) NOT NULL,
            time VARCHAR(20) NOT NULL,
            place VARCHAR(100) NOT NULL,
            program TEXT NOT NULL,
            link TEXT NOT NULL
            )"""
            cursor = connection.cursor()
            print("База данных подключена к SQLite")
            cursor.execute(table)
            connection.commit()
            print("Таблица SQLite создана")

    def get_final_result(self):
        self.create_db()
        with sqlite3.connect('concerts.db') as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM concerts")
            connection.commit()
        for page in self.var1:
            soup = BeautifulSoup(page, 'html.parser')
            date = soup.find('div', class_='col-sm-3 afisha-date').get_text()
            time_ = soup.find('div', class_='time').get_text()
            place = soup.find('div', class_='col-sm-6 afisha-hall').get_text()
            program = soup.find('div', itemtype="https://schema.org/CreativeWork").get_text()
            link = soup.find(property='og:url').get('content')
            with sqlite3.connect('concerts.db') as connection:
                cursor = connection.cursor()
                cursor.execute("""INSERT INTO `concerts` (date, time, place, program, link) 
                VALUES (?, ?, ?, ?, ?)""", (date, time_, place, program, link))
                connection.commit()

    def get_result_db(self):
        with sqlite3.connect('concerts.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT `rowid`, `date`, `time`, `place`, `link` FROM `concerts` "
                           "WHERE `program` LIKE '%Моцарт%';")
            result = set(cursor.fetchall())
            result = list(result)
            result.sort()
            return result

    def write_in_file(self):
        with open('concerts_to_sent.txt', 'w') as file_object:
            file_object.write('Ссылки на концерты по Вашему запросу')
            for i in self.get_result_db():
                new = i[1].replace('\n', ' ').strip().lower()
                file_object.write(f"\n\n{new}, в {i[2].strip()}\nМесто: {i[3].strip()}\nссылка на концерт: {i[4].strip()}")


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

    # def get_concerts_data(self):
    #     html = []
    #     for i in self.get_all_links():
    #         html1 = requests.get(i).text
    #         html.append(html1)
    #     print(html)

    async def get_concerts_data(self):
        async with aiohttp.ClientSession() as session:
            html = []
            for i in self.get_all_links():
                response = await session.get(i)
                html.append(await response.text())
        return html

    def run_async_2(self):
        a = asyncio.run(self.get_concerts_data())
        self.var3 = a

    def create_db(self):
        with sqlite3.connect('concerts.db') as connection:
            table = """CREATE TABLE IF NOT EXISTS `concerts1`(
            time VARCHAR(20) NOT NULL,
            place VARCHAR(100) NOT NULL,
            program TEXT NOT NULL,
            link TEXT NOT NULL
            )"""
            cursor = connection.cursor()
            print("База данных подключена к SQLite")
            cursor.execute(table)
            connection.commit()
            print("Таблица SQLite создана")

    def get_month_data(self):
        self.create_db()
        with sqlite3.connect('concerts.db') as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM concerts1")
            connection.commit()
        for i in self.var3:
            soup = BeautifulSoup(i, 'html.parser')
            time_ = soup.find('p', class_='text size18').get_text().strip()
            place = soup.find('p', class_='text size18').find_next_sibling().get_text().strip()
            program = soup.find('div', class_='small-row align-left').find_next_sibling().get_text().strip()\
                .replace('\n', '').replace('  ', '')
            link = soup.find(property="og:url").get('content')
            with sqlite3.connect('concerts.db') as connection:
                cursor = connection.cursor()
                cursor.execute("""INSERT INTO `concerts1` (time, place, program, link) 
                VALUES (?, ?, ?, ?)""", (time_, place, program, link))
                connection.commit()

    def get_result_db(self):
        with sqlite3.connect('concerts.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT `rowid`, `time`, `place`, `link` FROM `concerts1` "
                           "WHERE `program` LIKE '%Скрябин%' ORDER BY `rowid`;")
            result = cursor.fetchall()
            return result

    def write_in_file(self):
        with open('concerts_to_sent1.txt', 'w') as file_object:
            file_object.write('Ссылки на концерты по Вашему запросу')
            for i in self.get_result_db():
                file_object.write(f"\n\n{i[1].strip()}\nМесто: {i[2].strip()}\nссылка на концерт: {i[3].strip()}")


m = Meloman()
# m.run_async_2()
# m.get_month_data()
m.get_result_db()
m.write_in_file()


# m = Mosconsv()
# m.run_async()
# m.run_async_1()
# m.get_final_result()
# print(m.get_result_db())
# m.write_in_file()
