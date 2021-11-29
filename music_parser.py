import requests
import datetime
from bs4 import BeautifulSoup


class Mosconsv:

    def __init__(self):
        self.today = datetime.date.today()
        self.url = f'https://www.mosconsv.ru/afisha/{self.today}'
        self.__host = self.url.replace('//', '/').split('/')[1].replace('www.', '')

    def __get_html(self):
        page = requests.get(self.url)
        print(page.status_code)
        return page

    def __get_all_data(self):
        html = self.__get_html().text
        soup = BeautifulSoup(html, 'html.parser')
        every_concerts_data = soup.find_all('div', class_='row hall-block')
        concerts_links = []
        for i in every_concerts_data:
            concerts_links.append(self.__host + i.find('a').get('href'))
        return concerts_links

    def get_concerts_program(self):
        program = []
        for i in self.__get_all_data():
            page = requests.get(f'http://{i}')
            html = page.text
            soup = BeautifulSoup(html, 'html.parser')
            program.append({
                'date': soup.find('div', class_='col-sm-3 afisha-date').get_text(),
                'time': soup.find('div', class_='time').get_text(),
                'place': soup.find('div', class_='col-sm-6 afisha-hall').get_text(),
                'programs': soup.find('div', itemtype="https://schema.org/CreativeWork").get_text()
            })
        print(program)

    def parser(self, params=None):
        self.__get_all_data()

a = Mosconsv()
a.get_concerts_program()
