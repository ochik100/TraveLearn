from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from bs4 import BeautifulSoup
from items import StateItem, StateTopicItem
import scrapy


class StateCrawlSpider(CrawlSpider):
    name = "forum"
    allowed_domains = ['tripadvisor.com']
    start_urls = ['https://www.tripadvisor.com/ListForums-g191-i3-United_States.html']
    custom_settings = {
        'BOT_NAME': 'tripadvisor',
        'DEPTH_LIMIT': 5,
        'DOWNLOAD_DELAY': 3
    }

    def parse(self, response):
        for info in response.css("table.forumtopic tr")[1:]:
            # html = info.extract()
            # soup = BeautifulSoup(html, 'html.parser')
            state = StateItem()
            state['state'] = info.css('tr a::text').extract_first()
            state[
                'url'] = 'https://www.tripadvisor.com{}'.format(info.css('tr a::attr(href)').extract_first())
            state['num_topics'] = info.css('td.top::text').extract_first()
            state['num_posts'] = info.css('td.pos::text').extract_first()
            request = scrapy.Request(state['url'], callback=self.parse_state_topics)
            request.meta['state'] = state['state']
            yield request

    def parse_state_topics(self, response):
        state = response.meta['state']
        for info in response.css('table.topics tr')[1:]:
            state_topic = StateTopicItem()
            state_topic['topic'] = info.css('b a::text').extract_first()
            state_topic[
                'topic_url'] = 'https://www.tripadvisor.com{}'.format(info.css('b a::attr(href)').extract_first())
            state_topic['creator'] = info.css('div.bymember a::text').extract_first()
            state_topic['state'] = state
            yield state_topic

    def parse_posts(self, response):
        pass
