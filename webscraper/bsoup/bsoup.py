# -*- coding: UTF-8 -*-
import multiprocessing as mp
import Queue
import threading

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

DATABASE_NAME = "tripadvisor_r3_2x"
COLLECTION_NAME = 'florida'

client = MongoClient(connect=False)
db = client[DATABASE_NAME]
coll = db[COLLECTION_NAME]


class ForumPostCollector(object):

    def __init__(self, state, url):
        self.base_url = 'https://www.tripadvisor.com{}'
        self.state = state
        self.url = url

    def run(self):
        '''
        Runs forum webscraper on specified state and url
        '''
        soup = self.get_soup(self.url)
        self.get_topic_info(soup)

    def get_soup(self, url):
        '''
        Get soup from given url

        INPUT:
            url (str): URL to be soupified
        OUTPUT:
            soup (BeautifulSoup): soupified url
        '''
        content = requests.get(url).content
        soup = BeautifulSoup(content, 'html.parser')
        return soup

    def get_post_info_concurrent(self, topic, url, next_page=False):
        '''
        Retrieve all forum posts for the specified topic

        INPUT:
            topic (str): forum topic
            url (str): topic url
            next_page (bool): indicates whether a subsquent page of post exists for the specified topic
        '''
        soup = self.get_soup(url)
        if next_page:
            posts = soup.find_all('div', class_='post')[1:]
        else:
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
            url = self.base_url.format(next_page['href'])
            self.get_post_info_concurrent(topic, url, True)

    def scrape_post_details(self, tag, topic):
        '''
        Retrieves information from an individual post in a forum and inserts into respective mongodb collection

        INPUT:
            tag (BeautifulSoup Selector): forum post selector
            topic (str): post topic
        '''
        if tag.find('div', class_='username'):
            user = tag.find('div', class_='username').a['href'].split('/')[-1]
            date = tag.find('div', class_='postDate').text
            text = tag.find('div', class_='postBody').text.replace("\n", ' ').strip()
            self.insert_into_collection(self.state, topic, user, date, text)

    def insert_into_collection(self, state, topic, user, date, text):
        '''
        Insert details into mongo collection

        INPUT:
            state (str)
            topic (str)
            user (str)
            date (str)
            text (str)
        '''
        item = {'state': state,
                'topic': topic,
                'user': user,
                'date': date,
                'text': text}
        coll.insert_one(item)

    def get_topic_info(self, soup):
        '''
        Traverse through topic pages in forum using a queue. For each topic, start a process which gets all posts in respective topic.

        INPUT:
            soup (BeautifulSoup): soup from forum page
        '''
        # coll.remove({})  # be careful with this
        q = Queue.Queue()
        q.put(soup)
        while not q.empty():
            more_soup = q.get()
            urls = []
            topics = []
            for tag in more_soup.find('table', class_='topics').find_all('tr')[1:]:
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

            q.task_done()

            try:
                next_page = more_soup.find('div', class_='pgLinks').find(
                    'a', class_='guiArw sprite-pageNext')
            except:
                next_page = None

            if next_page:
                url = self.base_url.format(next_page['href'])
                next_soup = self.get_soup(url)
                q.put(next_soup)
            print q.empty(), url


if __name__ == '__main__':
    state = 'Florida'
    url = 'https://www.tripadvisor.com/ShowForum-g28930-i18-Florida.html'
    fdc = ForumPostCollector(state, url)
    print "Scraping", state
    print '-' * 10
    fdc.run()
    print "Complete."

    # df = pd.DataFrame(list(db.california.find())
