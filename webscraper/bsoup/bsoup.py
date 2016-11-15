# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import requests
import multiprocessing as mp
import threading
from pymongo import MongoClient
from itertools import izip

DATABASE_NAME = "tripadvisor"
COLLECTION_NAME = 'm_states'

client = MongoClient(connect=False)
db = client[DATABASE_NAME]
coll = db[COLLECTION_NAME]


class ForumPostCollector(object):

    def __init__(self, state, url):
        self.base_url = 'https://www.tripadvisor.com{}'
        self.state = state
        self.url = url

    def run(self):
        soup = self.get_soup(self.url)
        self.get_topic_info(soup)

    def get_soup(self, url):
        '''
        Get soup from a live url, as opposed to a local copy
        INPUT:
            -url: str
        OUTPUT: soup object
        '''
        content = requests.get(url).content
        soup = BeautifulSoup(content)
        return soup

    def get_post_info_concurrent(self, topic, url, next_page=False):
        soup = self.get_soup(url)
        if next_page:
            posts = soup.find_all('div', class_='post')[1:]
        else:
            posts = soup.find_all('div', class_='post')
        threads = len(posts)

        # print topic, threads
        jobs = []
        for i in range(0, threads):
            thread = threading.Thread(target=self.scrape_post_details, args=(posts[i], topic))
            jobs.append(thread)
            thread.start()
        for j in jobs:
            j.join()

        try:
            next_page = soup.find('div', class_='pgLinks').find(
                'a', class_='guiArw sprite-pageNext')
        except:
            next_page = None

        if next_page:
            url = self.base_url.format(next_page['href'])
            self.get_post_info_concurrent(topic, url, True)

    def scrape_post_details(self, tag, topic):
        if tag.find('div', class_='username'):
            # return
            user = tag.find('div', class_='username').a['href'].split('/')[-1]
            date = tag.find('div', class_='postDate').text
            text = tag.find('div', class_='postBody').text.replace("\n", ' ').strip()
            self.insert_into_collection(self.state, topic, user, date, text)
        else:
            pass
        # print topic, self.state, user, date, text

    def insert_into_collection(self, state, topic, user, date, text):
        item = {'state': state,
                'topic': topic,
                'user': user,
                'date': date,
                'text': text}
        # print json.dumps(item, ensure_ascii=False)
        coll.insert_one(item)

    def get_topic_info(self, soup):
        # coll.remove({})  # be careful with this
        urls = []
        topics = []
        for tag in soup.find('table', class_='topics').find_all('tr')[1:]:
            topic = tag.b.a.get_text().strip()
            topics.append(topic)
            topic_url = self.base_url.format(tag.b.a['href'])
            urls.append(topic_url)

        processes = []
        for i in range(len(urls)):
            proc = mp.Process(target=self.get_post_info_concurrent,
                              args=(topics[i], urls[i], ))
            proc.start()
            processes.append(proc)

        for proc in processes:
            proc.join()

        try:
            next_page = soup.find('div', class_='pgLinks').find(
                'a', class_='guiArw sprite-pageNext')
        except:
            next_page = None

        if next_page:
            url = self.base_url.format(next_page['href'])
            soup = self.get_soup(url)
            self.get_topic_info(soup)

if __name__ == '__main__':
    states = ['Maine', 'Maryland',
              'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
              'Missouri', 'Montana']
    urls = ['https://www.tripadvisor.com/ShowForum-g28940-i175-Maine.html',
            'https://www.tripadvisor.com/ShowForum-g28941-i100-Maryland.html',
            'https://www.tripadvisor.com/ShowForum-g28942-i47-Massachusetts.html',
            'https://www.tripadvisor.com/ShowForum-g28943-i319-Michigan.html',
            'https://www.tripadvisor.com/ShowForum-g28944-i371-Minnesota.html',
            'https://www.tripadvisor.com/ShowForum-g28945-i195-Mississippi.html',
            'https://www.tripadvisor.com/ShowForum-g28946-i199-Missouri.html',
            'https://www.tripadvisor.com/ShowForum-g28947-i982-Montana.html']

    for state, url in izip(states, urls):
        print "Scraping", state
        fdc = ForumPostCollector(state, url)
        fdc.run()

    # df = pd.DataFrame(list(db.california.find())
