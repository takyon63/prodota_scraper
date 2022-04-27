import requests
import numpy as np
import time
import csv
from bs4 import BeautifulSoup
import re


def get_page_soup(link):
    """Function that takes link and get's soup class, that contains page information"""
    response = requests.get(link)

    if not response.ok:
        # если сервер нам отказал, вернем статус ошибки
        return response.status_code

    # получаем содержимое страницы и переводим в суп
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_topic_pages(page_soup):
    """Function that gets number of pages in topic"""
    if type(page_soup) == BeautifulSoup:
        try:
            topic_pgs = int(page_soup.find('ul', attrs={'class': "ipsPagination"})['data-pages'])
            return topic_pgs
        except TypeError:
            topic_pgs = 1
            return topic_pgs
    else:
        return None


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, ' ', text)


def remove_newline(text):
    """Removes newlines, unusable tags from a string"""
    for r in (('\xa0', ''), ('\t', ''), ('\n', '')):
        text = text.replace(*r)
    return text.strip()


def get_parsed_data(page_soup):
    """Function that takes soup object and return date of the post, post itself and author of the post"""
    if type(page_soup) == BeautifulSoup:
        comments = page_soup.findAll('div', attrs={'data-role': "commentContent"})  # get list of all the comments
        comment_list = [remove_newline(remove_html_tags(str(comment))) for comment in comments]

        dates = page_soup.findAll(['time'])  # get list of comments when dates are made
        date_list = [date.attrs['title'] for date in dates[1:]]

        authors = page_soup.findAll('span', attrs={'class': "defrelNickTopic"})
        author_list = []
        for idx, author in enumerate(authors):
            author_name = authors[idx].text
            author_name_rep = author_name.replace('Дэфрэл', '').strip()
            author_list.append(author_name_rep)

        return list(zip(date_list, comment_list, author_list))

    else:
        pass


def write_data(page_soup, file='prodota_data.csv'):
    """ Function that takes in file and soup object, parses data and writes it to the file"""
    with open(file, 'a', encoding="utf-8") as f:
        write = csv.writer(f)
        if get_parsed_data(page_soup):
            for elem in get_parsed_data(page_soup):
                write.writerow(elem)
        else:
            pass


def scrape_data_pd(num_topic=11, max_num_topic=12):
    """Function that scrapes data from prodota.ru takes in topic number and iterates over all topic and topic pages
    returns csv file with comment, author of the comment and date of the comment """
    while num_topic <= max_num_topic:
        link = f'https://prodota.ru/forum/topic/{num_topic}/'
        print(link)

        soup = get_page_soup(link)
        topic_pages = get_topic_pages(soup)
        if topic_pages is not None:
            if topic_pages == 1:
                soup = get_page_soup(link)
                write_data(soup)
                num_topic += 1
            elif topic_pages == 2:
                topic_link = link + f"/page/{2}"
                soup = get_page_soup(topic_link)
                write_data(soup)
                num_topic += 1
            else:
                if topic_pages > 2:
                    write_data(get_page_soup(link))
                    for i in range(2, topic_pages + 1):
                        topic_link = link + f"page/{i}/"
                        soup = get_page_soup(topic_link)
                        write_data(soup)
                        time.sleep(np.random.random_sample())  # let script sleep to avoid bombarding the site

                num_topic += 1
        else:
            num_topic += 1

        time.sleep(np.random.random_sample())  # let script sleep to avoid bombarding the site


if __name__ == "__main__":
    scrape_data_pd(11, 5000)


#%%
