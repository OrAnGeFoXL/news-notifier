import requests
from bs4 import BeautifulSoup

from datetime import datetime
import os
import locale

from dataclasses import dataclass

from simple_term_menu import TerminalMenu
#Задаем заголовок для парсера
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}

#Задаем URL для парсинга сайта
url = 'https://mingh.org/cc/46/' #статьи на тему совершенствования
url_list = [
        'https://mingh.org/cc/46/', #традиционная культура
        'https://mingh.org/cc/45/', #мнение и точка зрения
        'https://mingh.org/cc/24/', #совершенствование
        'https://mingh.org/cc/33/', #новости и события
        'https://mingh.org/cc/1/',  #преследование
        'https://mingh.org/cc/14/', #карма и добродетель
        'https://mingh.org/cc/40/', #материалы
        ]
#Количество просматриваемых новостей
limit = 5

#Список цветов для CLI
c = ['\033[0m','\033[94m', '\033[92m', '\033[93m', '\033[91m', '\033[95m', '\033[96m', '\033[97m']


class NewsArticle:
    def __init__(self, link, date, category, name):
        self.link = link
        self.date = date
        self.category = category
        self.name = name
        self.fresh = False

    def print(self):
        """
        Print the article information in different colors.
        """
        if self.fresh:
            print(f"{c[2]}Дата {c[5]}(свежая):{c[0]} {self.date}")
        else:
            print(f"{c[2]}Дата:{c[0]} {self.date}")
        print(f"{c[4]}Название:{c[0]} {self.name}")
        print(f"{c[3]}Категория:{c[0]} {self.category}")
        print(f"{c[1]}{self.link}{c[0]}")



def clean_text(text):
    return text.replace('  ', '').replace('\n', '')

def convert_date(date):

    #locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    month_names = ['январь', 'февраль', 'март', 'апреля', 'мая', 'июнь', 'июль', 'авг.', 'сен.', 'октябрь', 'ноябрь', 'декабрь']

    # Преобразование месяцев в соответствии с окончанием
    month_name_mapping = {month_names[i]: datetime.strptime(f'{i+1}', '%m').strftime('%B') for i in range(len(month_names))}

    # TODO упростить
    date_parts = date.split(' ')
    month = month_name_mapping[date_parts[0].lower()]
    day = date_parts[1].replace(',', '')
    year = date_parts[2]
    date_object = datetime.strptime(f'{month} {day}, {year}', '%B %d, %Y').date()

    return date_object


def get_news_list(url):

    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Получаем статьи
    articles = soup.find('ul', class_='main-category-articles-list').find_all('li')

    news_articles = []

    for article in articles[0:limit]:

        link = article.find('a')['href']
        full_link = url[:-7] + link
        divs = article.find_all('div')
        info = divs[0].text #Категория и дата статьи
        name = divs[1].text 

        # Выделяем категорию и дату
        info = clean_text(info).split('| ')
        date, category = info
        name = clean_text(name)

        # Преобразование даты
        date =convert_date(date)

        news_article = NewsArticle(
            link=full_link,
            date=date,
            category=category,
            name=name
        )
        # Сравнение даты с сегодняшней датой
        if date == datetime.today().date():
            news_article.fresh = True

        news_articles.append(news_article)

    return news_articles


def print_wrapped(text):
  terminal_width = os.get_terminal_size().columns
  words = text.split()
  current_line = []
  for word in words:
    if len(' '.join(current_line + [word])) <= terminal_width:
      current_line.append(word)
    else:
      print(' '.join(current_line))
      current_line = [word]
  if current_line:
    print(' '.join(current_line))


def show_news(url): 
    
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Получаем статьи
    text = soup.find('div', class_='article-body-content')
    title = soup.find('div', class_='article-title').text
    title = clean_text(title)
    # Выводим заголовок статьи
    print(f'{c[4]}{title}{c[0]}')

    # Выводим текст статьи
    for p in text.find_all('p'):
        print_wrapped(p.text)
        #print(p.text)
        #print('\n')

    # Выводим ссылку на источник
    print(f"\nАвторские права принадлежат Minghui.org.\nИсточник: {url}")

def main():
    try:
        list = [
        'традиционная культура',
        'мнение и точка зрения',
        'совершенствование',
        'новости и события',
        'преследование',
        'карма и добродетель',
        'материалы'
        ]

        menu = TerminalMenu(list)

        news_list = get_news_list(url_list[menu.show()])
        for article in news_list:
            i = news_list.index(article)
            print(f'[{i+1}]')
            article.print()

        while True:
            print(f"Введите номер статьи для просмотра:")
            choice = input()

            if choice.isdigit():
                if int(choice)<=limit:
                    show_news(news_list[int(choice)-1].link)
                    break
                else:
                    print('Статьи с таким номером не существует')
            else:
                print("Некорректный ввод")  

    except ConnectionError as e:
        print(f"Ошибка соединения: {e}")

if __name__ == '__main__':
    main()
 
