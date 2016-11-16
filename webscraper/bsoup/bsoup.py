# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import requests
import multiprocessing as mp
import threading
from pymongo import MongoClient
import sys

DATABASE_NAME = "tripadvisor"
COLLECTION_NAME = 'colorado'

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
        Get soup from given url
        INPUT:
            -url: str
        OUTPUT: soup object
        '''
        content = requests.get(url).content
        soup = BeautifulSoup(content, 'html.parser')
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
            user = tag.find('div', class_='username').a['href'].split('/')[-1]
            date = tag.find('div', class_='postDate').text
            text = tag.find('div', class_='postBody').text.replace("\n", ' ').strip()
            self.insert_into_collection(self.state, topic, user, date, text)

    def insert_into_collection(self, state, topic, user, date, text):
        item = {'state': state,
                'topic': topic,
                'user': user,
                'date': date,
                'text': text}
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
            self.url = self.base_url.format(next_page['href'])
            self.run()
            # soup = self.get_soup(url)
            # try:
            #     self.get_topic_info(soup)
            # except:
            #     print "Stopped traversing at", url
            # try:
            #     self.get_topic_info(soup)
            # except RuntimeError as re:
            #     if re.args[0] == 'maximum recursion depth exceeded':
            #         print "Stopped traversing at", url
            #         print "Continuing..."
            #         fpc = ForumPostCollector("Kentucky", url)
            #         fpc.run()
            # except:
            #     e = sys.exc_info()[0]
            #     print e
            #     print "Stopped traversing at", url

if __name__ == '__main__':
    state = 'Colorado'
    url = 'https://www.tripadvisor.com/ShowForum-g28927-i252-Colorado.html'
    fdc = ForumPostCollector(state, url)
    print "Scraping", state
    print '-' * 10
    fdc.run()
    print "Complete."

    # df = pd.DataFrame(list(db.california.find())
