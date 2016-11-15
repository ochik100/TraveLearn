# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import requests
import numpy as np
import multiprocessing as mp
import threading
import json
from pymongo import MongoClient

DATABASE_NAME = "tripadvisor"
COLLECTION_NAME = 'california'

client = MongoClient()
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

    def get_post_info_concurrent(self, (topic, url)):
        soup = self.get_soup(url)
        posts = soup.find_all('div', class_='post')
        threads = len(posts)

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
            print "HASSSSS NEXXXTTT PAAAGEEE"
            url = self.base_url.format(next_page['href'])
            self.get_post_info_concurrent((topic, url))

    def scrape_post_details(self, tag, topic):
        if not tag.find('div', class_='username'):
            return
        user = tag.find('div', class_='username').a['href'].split('/')[-1]
        date = tag.find('div', class_='postDate').text
        text = tag.find('div', class_='postBody').text.replace("\n", ' ').strip()
        self.insert_into_collection(self.state, topic, user, date, text)
        # print topic, self.state, user, date, text

    def insert_into_collection(self, state, topic, user, date, text):
        item = {'state': state,
                'topic': topic,
                'user': user,
                'date': date,
                'text': text}
        # print json.dumps(item, ensure_ascii=False)
        coll.insert(item)

    def get_topic_info(self, soup):
        # self.coll.remove({})  # be careful with this
        urls = []
        topics = []
        for tag in soup.find('table', class_='topics').find_all('tr')[1:]:
            topic = tag.b.a.get_text().strip()
            topics.append(topic)
            topic_url = self.base_url.format(tag.b.a['href'])
            urls.append(topic_url)

        processes = []
        for i in range(len(urls)):
            proc = mp.Process(target=self.get_post_info_concurrent, args=((topics[i], urls[i]),))
            proc.start()
            processes.append(proc)

        try:
            next_page = soup.find('div', class_='pgLinks').find(
                'a', class_='guiArw sprite-pageNext')
        except:
            next_page = None

        if next_page:
            print "HASSSSS NEXXXTTT PAAAGEEE"
            url = self.base_url.format(next_page['href'])
            soup = self.get_soup(url)
            self.get_topic_info(soup)

if __name__ == '__main__':

    cali_url = 'https://www.tripadvisor.com/ShowForum-g28926-i29-o235520-California.html'
    fdc = ForumPostCollector("California", cali_url)
    fdc.run()

    # df = pd.DataFrame(list(db.california.find())
